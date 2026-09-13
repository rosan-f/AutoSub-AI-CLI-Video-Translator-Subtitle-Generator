"""Tests for the SRT Formatter module."""

from __future__ import annotations

from pathlib import Path

import pytest

from autosub_ai.core.formatter import SRTFormatter
from autosub_ai.core.transcriber import TranscriptionSegment
from autosub_ai.exceptions import FormatterError


# ================================================================
# Formatting
# ================================================================


class TestSRTFormatter:
    """Tests for SRTFormatter."""

    def test_format_segments(self, tmp_output_dir: Path) -> None:
        """format() must produce valid SRT output."""
        formatter = SRTFormatter(output_dir=tmp_output_dir)
        segments = [
            TranscriptionSegment(id=0, start=0.0, end=2.5, text="Hello"),
            TranscriptionSegment(id=1, start=2.5, end=5.0, text="World"),
        ]
        result = formatter.format(segments)

        assert "1\n" in result
        assert "00:00:00,000 --> 00:00:02,500" in result
        assert "Hello" in result
        assert "2\n" in result
        assert "World" in result

    def test_format_empty_segments_raises(self, tmp_output_dir: Path) -> None:
        """format() with no segments must raise FormatterError."""
        formatter = SRTFormatter(output_dir=tmp_output_dir)
        with pytest.raises(FormatterError, match="No segments"):
            formatter.format([])

    # ----------------------------------------------------------------
    # File Operations
    # ----------------------------------------------------------------

    def test_save_creates_file(self, tmp_output_dir: Path) -> None:
        """save() must create a valid .srt file."""
        formatter = SRTFormatter(output_dir=tmp_output_dir)
        content = "1\n00:00:00,000 --> 00:00:02,500\nHello\n"
        result_path = formatter.save(content, "test_subtitle")

        assert result_path.exists()
        assert result_path.suffix == ".srt"
        assert result_path.read_text(encoding="utf-8") == content

    # ----------------------------------------------------------------
    # Timestamp Formatting
    # ----------------------------------------------------------------

    def test_timestamp_formatting(self, tmp_output_dir: Path) -> None:
        """Timestamps must follow HH:MM:SS,mmm format."""
        formatter = SRTFormatter(output_dir=tmp_output_dir)

        assert formatter._format_timestamp(0.0) == "00:00:00,000"
        assert formatter._format_timestamp(61.5) == "00:01:01,500"
        assert formatter._format_timestamp(3661.123) == "01:01:01,123"
        assert formatter._format_timestamp(-1.0) == "00:00:00,000"

    # ----------------------------------------------------------------
    # Text Sanitization
    # ----------------------------------------------------------------

    def test_sanitize_text(self, tmp_output_dir: Path) -> None:
        """Control characters must be stripped from text."""
        formatter = SRTFormatter(output_dir=tmp_output_dir)

        assert formatter._sanitize_text("Normal text") == "Normal text"
        assert formatter._sanitize_text("  Spaced  ") == "Spaced"
        assert formatter._sanitize_text("\x00Null\x01char") == "Nullchar"

    # ----------------------------------------------------------------
    # Security
    # ----------------------------------------------------------------

    def test_save_sanitizes_filename(self, tmp_output_dir: Path) -> None:
        """Dangerous filenames must be sanitized before writing."""
        formatter = SRTFormatter(output_dir=tmp_output_dir)
        content = "1\n00:00:00,000 --> 00:00:01,000\nTest\n"

        result_path = formatter.save(content, "../../etc/passwd")
        assert result_path.parent == tmp_output_dir
        assert result_path.exists()
