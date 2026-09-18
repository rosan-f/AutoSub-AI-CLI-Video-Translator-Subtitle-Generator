"""
AutoSub-AI — Transcription Engine

Handles audio-to-text transcription using OpenAI Whisper.

Security measures:
- Audio file path validation (path traversal guard)
- Model size validation against allowed set
- Automatic CUDA/CPU/MPS device detection
- GPU memory cleanup after processing
- Context manager protocol for guaranteed resource disposal
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from autosub_ai.exceptions import ModelLoadError, TranscriptionError, ValidationError
from autosub_ai.utils.validators import validate_file_path, validate_model_size

logger = logging.getLogger(__name__)

# ================================================================
# Constants
# ================================================================

AVAILABLE_MODELS = ("tiny", "base", "small", "medium", "large")
VALID_TASKS = frozenset({"transcribe", "translate"})


# ================================================================
# Data Models
# ================================================================


@dataclass
class TranscriptionSegment:
    """A single transcription segment with timing data."""

    id: int
    start: float  # Start time in seconds
    end: float  # End time in seconds
    text: str
    no_speech_prob: float = 0.0


@dataclass
class TranscriptionResult:
    """Complete transcription output."""

    segments: list[TranscriptionSegment]
    language: str
    text: str  # Full concatenated text
    duration: float  # Total audio duration in seconds


@dataclass
class TranscriptionOptions:
    """Configuration options for Whisper inference."""

    task: str = "transcribe"
    beam_size: int = 5
    temperature: float = 0.0
    best_of: int = 5
    fp16: bool | None = None
    initial_prompt: str | None = None
    condition_on_previous_text: bool = True

    def __post_init__(self) -> None:
        """Validate inference options."""
        if self.task not in VALID_TASKS:
            raise ValidationError(
                f"Invalid task '{self.task}'. Supported: {', '.join(sorted(VALID_TASKS))}"
            )
        if self.beam_size < 1:
            raise ValidationError("beam_size must be >= 1")
        if not (0.0 <= self.temperature <= 1.0):
            raise ValidationError("temperature must be between 0.0 and 1.0")


@dataclass
class TranscriptionProgress:
    """Progress event emitted during transcription."""

    status: str
    message: str = ""


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
        model_size:  Whisper model variant to use.
        device:      Inference device (cuda/cpu/mps, auto-detected).
        language:    Source audio language (None = auto-detect).
        options:     Inference options (beam size, task, fp16, etc.).
        on_progress: Optional callback for progress reporting.
    """

    model_size: str = "base"
    device: str | None = None
    language: str | None = None
    options: TranscriptionOptions = field(default_factory=TranscriptionOptions)
    on_progress: Callable[[TranscriptionProgress], None] | None = field(
        default=None, repr=False
    )
    _model: Any = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        """Validate model size and detect compute device."""
        self.model_size = validate_model_size(self.model_size)

        if self.device is None:
            self.device = self._detect_device()

        if self.options.fp16 is None:
            # --- FP16 is only effective on CUDA devices ---
            self.options.fp16 = self.device == "cuda"

        logger.info(
            "Whisper config: model=%s, device=%s, task=%s, fp16=%s",
            self.model_size,
            self.device,
            self.options.task,
            self.options.fp16,
        )

    # ----------------------------------------------------------------
    # Context Manager Protocol
    # ----------------------------------------------------------------

    def __enter__(self) -> WhisperTranscriber:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager and clean up resources."""
        self.cleanup()

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

        self._emit_progress("loading_model", f"Loading model '{self.model_size}'...")

        try:
            import whisper

            logger.info("Loading Whisper model '%s' on %s...", self.model_size, self.device)
            self._model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Model loaded successfully")
            self._emit_progress("model_loaded", "Model loaded successfully.")

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
        self._emit_progress("transcribing", f"Transcribing {validated_path.name}...")

        try:
            kwargs: dict[str, Any] = {
                "task": self.options.task,
                "beam_size": self.options.beam_size,
                "temperature": self.options.temperature,
                "best_of": self.options.best_of,
                "fp16": self.options.fp16,
                "verbose": False,
            }

            if self.language is not None:
                kwargs["language"] = self.language

            if self.options.initial_prompt is not None:
                kwargs["initial_prompt"] = self.options.initial_prompt

            result = self._model.transcribe(str(validated_path), **kwargs)

            raw_segments = result.get("segments", [])
            segments = [
                TranscriptionSegment(
                    id=i,
                    start=float(seg["start"]),
                    end=float(seg["end"]),
                    text=str(seg.get("text", "")).strip(),
                    no_speech_prob=float(seg.get("no_speech_prob", 0.0)),
                )
                for i, seg in enumerate(raw_segments)
            ]

            transcription = TranscriptionResult(
                segments=segments,
                language=str(result.get("language", "unknown")),
                text=str(result.get("text", "")).strip(),
                duration=float(segments[-1].end) if segments else 0.0,
            )

            logger.info(
                "Transcription complete: %d segments, language=%s, duration=%.1fs",
                len(segments),
                transcription.language,
                transcription.duration,
            )
            self._emit_progress(
                "complete",
                f"Transcription complete ({len(segments)} segments).",
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
            'cuda' if an NVIDIA GPU is available, 'mps' for Apple Silicon,
            otherwise 'cpu'.
        """
        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                logger.info("GPU detected: %s", gpu_name)
                return "cuda"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                logger.info("Apple Silicon MPS detected")
                return "mps"
        except ImportError:
            logger.warning("PyTorch not installed, falling back to CPU")

        logger.info("Using CPU for inference")
        return "cpu"

    def _emit_progress(self, status: str, message: str = "") -> None:
        """Emit a progress event if a callback is registered."""
        if self.on_progress is not None:
            self.on_progress(TranscriptionProgress(status=status, message=message))
