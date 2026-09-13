"""
AutoSub-AI — Translator Module

Handles text translation leveraging Whisper's built-in translate task.

Whisper natively supports translation to English via task="translate".
For other target languages, a multi-stage approach is used:
transcription > English translation > target language translation.

Security measures:
- Target language validation against supported set
- Input text length limits per segment
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from autosub_ai.core.transcriber import TranscriptionResult, TranscriptionSegment
from autosub_ai.exceptions import TranslationError

logger = logging.getLogger(__name__)

# ================================================================
# Constants
# ================================================================

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

MAX_SEGMENT_LENGTH = 5000         # Characters per segment


# ================================================================
# Data Models
# ================================================================


@dataclass
class TranslationResult:
    """Container for translation output."""

    segments: list[TranscriptionSegment]
    source_language: str
    target_language: str


# ================================================================
# Translator
# ================================================================


class TextTranslator:
    """
    Translates transcription results into a target language.

    Strategy:
    1. If target=en: Use Whisper's built-in task="translate"
    2. If target=other: Transcribe to English first,
       then apply an additional translation layer

    Attributes:
        target_language: ISO 639-1 language code.
    """

    def __init__(self, target_language: str = "id") -> None:
        """
        Initialize the translator.

        Args:
            target_language: ISO 639-1 code (e.g., 'id', 'en').

        Raises:
            TranslationError: If the language is not supported.
        """
        if target_language not in SUPPORTED_LANGUAGES:
            raise TranslationError(
                f"Language '{target_language}' is not supported. "
                f"Available: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )

        self.target_language = target_language
        logger.info(
            "Translator initialized: target=%s (%s)",
            target_language,
            SUPPORTED_LANGUAGES[target_language],
        )

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def translate(self, transcription: TranscriptionResult) -> TranslationResult:
        """
        Translate transcription segments into the target language.

        Args:
            transcription: Output from WhisperTranscriber.

        Returns:
            TranslationResult with translated segments.

        Raises:
            TranslationError: If translation fails.
        """
        logger.info(
            "Translating %d segments from '%s' to '%s'",
            len(transcription.segments),
            transcription.language,
            self.target_language,
        )

        try:
            # --- Segment length validation ---
            for segment in transcription.segments:
                if len(segment.text) > MAX_SEGMENT_LENGTH:
                    logger.warning(
                        "Segment #%d exceeds max length (%d chars), truncating",
                        segment.id,
                        len(segment.text),
                    )
                    segment.text = segment.text[:MAX_SEGMENT_LENGTH]

            # TODO Phase 3: Implement actual translation logic
            translated_segments = transcription.segments

            logger.info("Translation complete: %d segments", len(translated_segments))

            return TranslationResult(
                segments=translated_segments,
                source_language=transcription.language,
                target_language=self.target_language,
            )

        except TranslationError:
            raise
        except Exception as e:
            logger.exception("Translation failed")
            raise TranslationError(f"Translation failed: {type(e).__name__}") from e
