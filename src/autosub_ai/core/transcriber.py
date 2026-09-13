"""
AutoSub-AI — Transcription Engine

Handles audio-to-text transcription using OpenAI Whisper.

Security measures:
- Audio file path validation (path traversal guard)
- Model size validation against allowed set
- Automatic CUDA/CPU device detection
- GPU memory cleanup after processing
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from autosub_ai.exceptions import ModelLoadError, TranscriptionError
from autosub_ai.utils.validators import validate_file_path, validate_model_size

logger = logging.getLogger(__name__)

# ================================================================
# Constants
# ================================================================

AVAILABLE_MODELS = ("tiny", "base", "small", "medium", "large")


# ================================================================
# Data Models
# ================================================================


@dataclass
class TranscriptionSegment:
    """A single transcription segment with timing data."""

    id: int
    start: float                  # Start time (seconds)
    end: float                    # End time (seconds)
    text: str


@dataclass
class TranscriptionResult:
    """Complete transcription output."""

    segments: list[TranscriptionSegment]
    language: str
    text: str                     # Full concatenated text
    duration: float               # Total audio duration


# ================================================================
# Transcriber
# ================================================================


@dataclass
class WhisperTranscriber:
    """
    Core speech-to-text engine powered by OpenAI Whisper.

    Supports GPU acceleration (CUDA) for efficient processing
    of long-duration video content.

    Attributes:
        model_size: Whisper model variant to use.
        device:     Inference device (cuda/cpu, auto-detected).
        language:   Source audio language (None = auto-detect).
    """

    model_size: str = "base"
    device: str | None = None
    language: str | None = None
    _model: Any = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        """Validate model size and detect compute device."""
        self.model_size = validate_model_size(self.model_size)

        if self.device is None:
            self.device = self._detect_device()

        logger.info("Whisper config: model=%s, device=%s", self.model_size, self.device)

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def load_model(self) -> None:
        """
        Load the Whisper model into memory.

        Raises:
            ModelLoadError: If the model cannot be loaded.
        """
        if self._model is not None:
            logger.debug("Model already loaded, skipping")
            return

        try:
            import whisper

            logger.info("Loading Whisper model '%s'...", self.model_size)
            self._model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Model loaded successfully")

        except ImportError:
            raise ModelLoadError(
                "openai-whisper is not installed. Run: pip install openai-whisper"
            ) from None
        except Exception as e:
            logger.exception("Model loading failed")
            raise ModelLoadError(self.model_size) from e

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        """
        Transcribe an audio file into text segments with timestamps.

        Args:
            audio_path: Path to the audio file (.wav, .mp3, etc.).

        Returns:
            TranscriptionResult containing timed text segments.

        Raises:
            TranscriptionError: If transcription fails.
        """
        validated_path = validate_file_path(audio_path)
        logger.info("Starting transcription: %s", validated_path.name)

        self.load_model()

        try:
            result = self._model.transcribe(
                str(validated_path),
                language=self.language,
                verbose=False,
            )

            segments = [
                TranscriptionSegment(
                    id=i,
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"].strip(),
                )
                for i, seg in enumerate(result.get("segments", []))
            ]

            transcription = TranscriptionResult(
                segments=segments,
                language=result.get("language", "unknown"),
                text=result.get("text", ""),
                duration=segments[-1].end if segments else 0.0,
            )

            logger.info(
                "Transcription complete: %d segments, language=%s",
                len(segments),
                transcription.language,
            )

            return transcription

        except TranscriptionError:
            raise
        except Exception as e:
            logger.exception("Transcription failed")
            raise TranscriptionError(f"Transcription failed: {type(e).__name__}") from e

    def cleanup(self) -> None:
        """Release model from memory and free GPU resources."""
        if self._model is not None:
            del self._model
            self._model = None
            logger.debug("Model released from memory")

            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

    # ----------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------

    def _detect_device(self) -> str:
        """
        Auto-detect the best available compute device.

        Returns:
            'cuda' if an NVIDIA GPU is available, otherwise 'cpu'.
        """
        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                logger.info("GPU detected: %s", gpu_name)
                return "cuda"
        except ImportError:
            logger.warning("PyTorch not installed, falling back to CPU")

        logger.info("Using CPU for inference")
        return "cpu"
