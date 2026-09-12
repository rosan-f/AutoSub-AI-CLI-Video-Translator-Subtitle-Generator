"""
Transcription Engine — Transkripsi audio menggunakan OpenAI Whisper.

Fitur keamanan:
- Validasi path file audio (path traversal guard)
- Validasi model size
- Auto-detect CUDA/CPU
- Resource cleanup setelah selesai
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from autosub_ai.exceptions import ModelLoadError, TranscriptionError
from autosub_ai.utils.security import safe_resolve_path
from autosub_ai.utils.validators import validate_file_path, validate_model_size

logger = logging.getLogger(__name__)

# Model sizes yang tersedia
AVAILABLE_MODELS = ("tiny", "base", "small", "medium", "large")


@dataclass
class TranscriptionSegment:
    """Satu segmen hasil transkripsi."""

    id: int
    start: float  # Waktu mulai (detik)
    end: float  # Waktu selesai (detik)
    text: str


@dataclass
class TranscriptionResult:
    """Hasil lengkap transkripsi."""

    segments: list[TranscriptionSegment]
    language: str
    text: str  # Teks penuh
    duration: float  # Total durasi audio


@dataclass
class WhisperTranscriber:
    """
    Otak utama pemrosesan suara menggunakan OpenAI Whisper.

    Mendukung akselerasi GPU (CUDA) untuk pemrosesan cepat
    pada video berdurasi panjang.

    Attributes:
        model_size: Ukuran model Whisper yang digunakan.
        device: Device untuk inference (cuda/cpu, auto-detect).
        language: Bahasa sumber audio (None = auto-detect).
    """

    model_size: str = "base"
    device: str | None = None
    language: str | None = None
    _model: Any = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        """Validasi model size dan detect device."""
        self.model_size = validate_model_size(self.model_size)

        if self.device is None:
            self.device = self._detect_device()

        logger.info("Whisper config: model=%s, device=%s", self.model_size, self.device)

    def _detect_device(self) -> str:
        """
        Auto-detect device terbaik (CUDA GPU atau CPU).

        Returns:
            String device: 'cuda' atau 'cpu'.
        """
        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                logger.info("GPU terdeteksi: %s", gpu_name)
                return "cuda"
        except ImportError:
            logger.warning("PyTorch tidak terinstal, menggunakan CPU")

        logger.info("Menggunakan CPU untuk inference")
        return "cpu"

    def load_model(self) -> None:
        """
        Muat model Whisper ke memory.

        Raises:
            ModelLoadError: Jika model gagal dimuat.
        """
        if self._model is not None:
            logger.debug("Model sudah dimuat, skip loading")
            return

        try:
            import whisper

            logger.info("Memuat model Whisper '%s'...", self.model_size)
            self._model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Model berhasil dimuat")

        except ImportError:
            raise ModelLoadError(
                "openai-whisper tidak terinstal. Jalankan: pip install openai-whisper"
            ) from None
        except Exception as e:
            logger.exception("Gagal memuat model")
            raise ModelLoadError(self.model_size) from e

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        """
        Transkripsi file audio menjadi teks beserta timestamp.

        Args:
            audio_path: Path ke file audio (.wav, .mp3, dll).

        Returns:
            TranscriptionResult dengan segmen-segmen teks.

        Raises:
            TranscriptionError: Jika transkripsi gagal.
        """
        # Validasi path
        validated_path = validate_file_path(audio_path)
        logger.info("Memulai transkripsi: %s", validated_path.name)

        # Pastikan model sudah dimuat
        self.load_model()

        try:
            # Jalankan transkripsi
            result = self._model.transcribe(
                str(validated_path),
                language=self.language,
                verbose=False,
            )

            # Parse hasil menjadi TranscriptionResult
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
                "Transkripsi selesai: %d segmen, bahasa=%s",
                len(segments),
                transcription.language,
            )

            return transcription

        except TranscriptionError:
            raise
        except Exception as e:
            logger.exception("Transkripsi gagal")
            raise TranscriptionError(f"Transkripsi gagal: {type(e).__name__}") from e

    def cleanup(self) -> None:
        """Bersihkan model dari memory."""
        if self._model is not None:
            del self._model
            self._model = None
            logger.debug("Model dibersihkan dari memory")

            # Coba bebaskan GPU memory
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass
