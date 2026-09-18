"""
AutoSub-AI — Transcription Engine Tests

Unit tests for WhisperTranscriber, TranscriptionOptions, and data models.
All inference is mocked to prevent network or heavy compute operations in CI/tests.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from autosub_ai.core.transcriber import (
    AVAILABLE_MODELS,
    TranscriptionOptions,
    TranscriptionProgress,
    TranscriptionResult,
    TranscriptionSegment,
    WhisperTranscriber,
)
from autosub_ai.exceptions import ModelLoadError, TranscriptionError, ValidationError


# ================================================================
# Initialization & Options Tests
# ================================================================


class TestWhisperTranscriberInit:
    """Tests for WhisperTranscriber initialization and configuration."""

    @pytest.mark.parametrize("model_name", AVAILABLE_MODELS)
    def test_init_valid_model(self, model_name: str) -> None:
        """Transcriber must accept all valid model sizes."""
        transcriber = WhisperTranscriber(model_size=model_name)
        assert transcriber.model_size == model_name

    def test_init_invalid_model_raises(self) -> None:
        """Transcriber must reject invalid model sizes."""
        with pytest.raises(ValidationError):
            WhisperTranscriber(model_size="ultra-huge")

    def test_device_detection(self) -> None:
        """Device detection must return a valid compute target."""
        transcriber = WhisperTranscriber(model_size="tiny")
        assert transcriber.device in ("cuda", "mps", "cpu")

    def test_fp16_auto_configuration(self) -> None:
        """FP16 must default to True on CUDA and False on CPU."""
        with patch.object(WhisperTranscriber, "_detect_device", return_value="cpu"):
            transcriber_cpu = WhisperTranscriber(model_size="tiny")
            assert transcriber_cpu.options.fp16 is False

        with patch.object(WhisperTranscriber, "_detect_device", return_value="cuda"):
            transcriber_cuda = WhisperTranscriber(model_size="tiny")
            assert transcriber_cuda.options.fp16 is True


class TestTranscriptionOptions:
    """Tests for TranscriptionOptions validation."""

    def test_default_options(self) -> None:
        """Default options must be properly initialized."""
        opts = TranscriptionOptions()
        assert opts.task == "transcribe"
        assert opts.beam_size == 5
        assert opts.temperature == 0.0

    def test_invalid_task_raises(self) -> None:
        """Invalid tasks must be rejected."""
        with pytest.raises(ValidationError, match="Invalid task"):
            TranscriptionOptions(task="summarize")

    def test_invalid_beam_size_raises(self) -> None:
        """Beam size must be at least 1."""
        with pytest.raises(ValidationError, match="beam_size"):
            TranscriptionOptions(beam_size=0)

    def test_invalid_temperature_raises(self) -> None:
        """Temperature must be between 0.0 and 1.0."""
        with pytest.raises(ValidationError, match="temperature"):
            TranscriptionOptions(temperature=1.5)


# ================================================================
# Model Loading & Inference Tests
# ================================================================


class TestWhisperTranscriberExecution:
    """Tests for model loading and transcription execution."""

    def test_load_model_success(self) -> None:
        """load_model must call whisper.load_model with correct args."""
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"whisper": mock_whisper}):
            transcriber = WhisperTranscriber(model_size="base", device="cpu")
            transcriber.load_model()

            mock_whisper.load_model.assert_called_once_with("base", device="cpu")
            assert transcriber._model == mock_model

    def test_load_model_missing_package_raises(self) -> None:
        """Missing whisper package must raise ModelLoadError."""
        with patch.dict("sys.modules", {"whisper": None}):
            transcriber = WhisperTranscriber(model_size="base")
            with pytest.raises(ModelLoadError, match="openai-whisper"):
                transcriber.load_model()

    def test_transcribe_success(self, sample_audio_path: Path) -> None:
        """transcribe() must parse raw segments and calculate metrics correctly."""
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": " Welcome to cybersecurity bootcamp.",
            "language": "en",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.5,
                    "text": " Welcome to",
                    "no_speech_prob": 0.01,
                },
                {
                    "id": 1,
                    "start": 2.5,
                    "end": 5.0,
                    "text": " cybersecurity bootcamp.",
                    "no_speech_prob": 0.02,
                },
            ],
        }
        mock_whisper.load_model.return_value = mock_model

        progress_events: list[TranscriptionProgress] = []

        with patch.dict("sys.modules", {"whisper": mock_whisper}):
            transcriber = WhisperTranscriber(
                model_size="base",
                device="cpu",
                on_progress=progress_events.append,
            )
            result = transcriber.transcribe(sample_audio_path)

            assert isinstance(result, TranscriptionResult)
            assert result.language == "en"
            assert result.duration == 5.0
            assert len(result.segments) == 2
            assert result.segments[0].text == "Welcome to"
            assert result.segments[1].end == 5.0
            assert len(progress_events) >= 2

    def test_transcribe_nonexistent_audio_raises(self, tmp_path: Path) -> None:
        """Nonexistent audio files must fail validation."""
        transcriber = WhisperTranscriber(model_size="base")
        with pytest.raises(ValidationError):
            transcriber.transcribe(tmp_path / "missing.wav")

    def test_transcribe_runtime_failure_raises(self, sample_audio_path: Path) -> None:
        """Internal transcription failures must raise TranscriptionError."""
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = RuntimeError("Inference crash")
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"whisper": mock_whisper}):
            transcriber = WhisperTranscriber(model_size="base", device="cpu")
            with pytest.raises(TranscriptionError, match="Transcription failed"):
                transcriber.transcribe(sample_audio_path)


# ================================================================
# Context Manager & Cleanup Tests
# ================================================================


class TestContextManagerAndCleanup:
    """Tests for context management and resource release."""

    def test_cleanup_releases_model(self) -> None:
        """cleanup() must reset model and invoke torch memory release."""
        transcriber = WhisperTranscriber(model_size="base")
        transcriber._model = MagicMock()

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        with patch.dict("sys.modules", {"torch": mock_torch}):
            transcriber.cleanup()
            assert transcriber._model is None
            mock_torch.cuda.empty_cache.assert_called_once()

    def test_context_manager_calls_cleanup(self) -> None:
        """Context manager exit must trigger cleanup."""
        with patch.object(WhisperTranscriber, "cleanup") as mock_cleanup:
            with WhisperTranscriber(model_size="base") as transcriber:
                assert transcriber.model_size == "base"
            mock_cleanup.assert_called_once()


# ================================================================
# Data Models Tests
# ================================================================


class TestDataModels:
    """Tests for transcriber data structures."""

    def test_segment_creation(self) -> None:
        """TranscriptionSegment stores timing and text data."""
        segment = TranscriptionSegment(
            id=0,
            start=0.0,
            end=2.5,
            text="Testing audio segment",
            no_speech_prob=0.05,
        )
        assert segment.id == 0
        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.text == "Testing audio segment"
        assert segment.no_speech_prob == 0.05

    def test_empty_segments_duration(self) -> None:
        """TranscriptionResult with empty segments must have 0.0 duration."""
        result = TranscriptionResult(
            segments=[],
            language="en",
            text="",
            duration=0.0,
        )
        assert result.duration == 0.0
        assert len(result.segments) == 0
