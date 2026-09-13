"""Tests for the Transcriber module (unit tests, no model loading)."""

from __future__ import annotations

import pytest

from autosub_ai.core.transcriber import (
    TranscriptionResult,
    TranscriptionSegment,
    WhisperTranscriber,
)
from autosub_ai.exceptions import ValidationError


# ================================================================
# WhisperTranscriber
# ================================================================


class TestWhisperTranscriber:
    """Tests for WhisperTranscriber."""

    def test_init_valid_model(self) -> None:
        """Transcriber must accept valid model sizes."""
        transcriber = WhisperTranscriber(model_size="tiny")
        assert transcriber.model_size == "tiny"

    def test_init_invalid_model_raises(self) -> None:
        """Transcriber must reject invalid model sizes."""
        with pytest.raises(ValidationError):
            WhisperTranscriber(model_size="nonexistent")

    def test_device_detection(self) -> None:
        """Device detection must return 'cuda' or 'cpu'."""
        transcriber = WhisperTranscriber(model_size="tiny")
        assert transcriber.device in ("cuda", "cpu")


# ================================================================
# Data Models
# ================================================================


class TestTranscriptionSegment:
    """Tests for TranscriptionSegment."""

    def test_segment_creation(self) -> None:
        """Segment must store timing and text data correctly."""
        segment = TranscriptionSegment(
            id=0, start=0.0, end=2.5, text="Hello world"
        )
        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.text == "Hello world"


class TestTranscriptionResult:
    """Tests for TranscriptionResult."""

    def test_result_with_segments(self) -> None:
        """Result must hold segments correctly."""
        segments = [
            TranscriptionSegment(id=0, start=0.0, end=2.5, text="Hello"),
            TranscriptionSegment(id=1, start=2.5, end=5.0, text="World"),
        ]
        result = TranscriptionResult(
            segments=segments,
            language="en",
            text="Hello World",
            duration=5.0,
        )
        assert len(result.segments) == 2
        assert result.language == "en"
