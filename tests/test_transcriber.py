"""Tests untuk Transcriber Module (unit tests tanpa model loading)."""

from __future__ import annotations

import pytest

from autosub_ai.core.transcriber import (
    TranscriptionResult,
    TranscriptionSegment,
    WhisperTranscriber,
)
from autosub_ai.exceptions import ValidationError


class TestWhisperTranscriber:
    """Tests untuk WhisperTranscriber."""

    def test_init_valid_model(self) -> None:
        """Transcriber harus menerima model size yang valid."""
        transcriber = WhisperTranscriber(model_size="tiny")
        assert transcriber.model_size == "tiny"

    def test_init_invalid_model_raises(self) -> None:
        """Transcriber harus menolak model size yang invalid."""
        with pytest.raises(ValidationError):
            WhisperTranscriber(model_size="nonexistent")

    def test_device_detection(self) -> None:
        """Device detection harus mengembalikan 'cuda' atau 'cpu'."""
        transcriber = WhisperTranscriber(model_size="tiny")
        assert transcriber.device in ("cuda", "cpu")


class TestTranscriptionSegment:
    """Tests untuk TranscriptionSegment."""

    def test_segment_creation(self) -> None:
        """Segment harus menyimpan data dengan benar."""
        segment = TranscriptionSegment(
            id=0, start=0.0, end=2.5, text="Hello world"
        )
        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.text == "Hello world"


class TestTranscriptionResult:
    """Tests untuk TranscriptionResult."""

    def test_result_with_segments(self) -> None:
        """Result harus menyimpan segmen dengan benar."""
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
