"""
Translator Module — Terjemahan teks menggunakan Whisper task=translate.

Whisper sudah memiliki kemampuan translate built-in ke Bahasa Inggris.
Untuk bahasa lain (termasuk Bahasa Indonesia), kita gunakan
pendekatan bertahap: transkripsi → terjemahan.

Fitur keamanan:
- Validasi bahasa target
- Batasi panjang teks input
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from autosub_ai.core.transcriber import TranscriptionResult, TranscriptionSegment
from autosub_ai.exceptions import TranslationError

logger = logging.getLogger(__name__)

# Bahasa yang didukung untuk terjemahan
SUPPORTED_LANGUAGES = {
    "id": "Indonesian",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi",
}

# Batas panjang teks per segmen (karakter)
MAX_SEGMENT_LENGTH = 5000


@dataclass
class TranslationResult:
    """Hasil terjemahan."""

    segments: list[TranscriptionSegment]
    source_language: str
    target_language: str


class TextTranslator:
    """
    Menerjemahkan hasil transkripsi ke bahasa target.

    Strategi:
    1. Jika target=en: Gunakan Whisper task="translate" (bawaan)
    2. Jika target=lainnya: Transkripsi dulu ke English,
       lalu gunakan translation layer tambahan

    Attributes:
        target_language: Kode bahasa target (ISO 639-1).
    """

    def __init__(self, target_language: str = "id") -> None:
        """
        Inisialisasi translator.

        Args:
            target_language: Kode bahasa target (contoh: 'id', 'en').

        Raises:
            TranslationError: Jika bahasa tidak didukung.
        """
        if target_language not in SUPPORTED_LANGUAGES:
            raise TranslationError(
                f"Bahasa '{target_language}' tidak didukung. "
                f"Pilihan: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )

        self.target_language = target_language
        logger.info(
            "Translator diinisialisasi: target=%s (%s)",
            target_language,
            SUPPORTED_LANGUAGES[target_language],
        )

    def translate(self, transcription: TranscriptionResult) -> TranslationResult:
        """
        Terjemahkan hasil transkripsi ke bahasa target.

        Args:
            transcription: Hasil transkripsi dari WhisperTranscriber.

        Returns:
            TranslationResult dengan segmen yang sudah diterjemahkan.

        Raises:
            TranslationError: Jika terjemahan gagal.
        """
        logger.info(
            "Menerjemahkan %d segmen dari '%s' ke '%s'",
            len(transcription.segments),
            transcription.language,
            self.target_language,
        )

        try:
            # Validasi panjang segmen
            for segment in transcription.segments:
                if len(segment.text) > MAX_SEGMENT_LENGTH:
                    logger.warning(
                        "Segmen #%d terlalu panjang (%d karakter), akan di-truncate",
                        segment.id,
                        len(segment.text),
                    )
                    segment.text = segment.text[:MAX_SEGMENT_LENGTH]

            # TODO: Tahap 2 — Implementasi terjemahan sesungguhnya
            # Untuk saat ini, kembalikan segmen asli (pass-through)
            translated_segments = transcription.segments

            logger.info("Terjemahan selesai: %d segmen", len(translated_segments))

            return TranslationResult(
                segments=translated_segments,
                source_language=transcription.language,
                target_language=self.target_language,
            )

        except TranslationError:
            raise
        except Exception as e:
            logger.exception("Terjemahan gagal")
            raise TranslationError(f"Terjemahan gagal: {type(e).__name__}") from e
