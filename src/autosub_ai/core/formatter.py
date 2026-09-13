"""
AutoSub-AI — SRT Formatter Module

Converts transcription/translation segments into standard .srt subtitle files
with precise timestamps.

SRT format specification:
    1
    00:00:00,000 --> 00:00:02,500
    First subtitle line

    2
    00:00:02,500 --> 00:00:05,000
    Second subtitle line

Security measures:
- Text content sanitization (strip dangerous control characters)
- Output path validation (path traversal guard)
- Atomic write (write to temp file first, then rename)
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from autosub_ai.core.transcriber import TranscriptionSegment
from autosub_ai.exceptions import FormatterError
from autosub_ai.utils.security import safe_resolve_path, sanitize_filename

logger = logging.getLogger(__name__)


# ================================================================
# Formatter
# ================================================================


@dataclass
class SRTFormatter:
    """
    Generates standard .srt subtitle files from timed text segments.

    Produces files compatible with all major media players.

    Attributes:
        output_dir: Target directory for .srt files.
    """

    output_dir: Path

    def __post_init__(self) -> None:
        """Create output directory if it does not exist."""
        self.output_dir = safe_resolve_path(Path.cwd(), self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def format(self, segments: list[TranscriptionSegment]) -> str:
        """
        Format segments into an SRT-compliant string.

        Args:
            segments: List of transcription segments with timestamps.

        Returns:
            SRT-formatted string.

        Raises:
            FormatterError: If formatting fails.
        """
        if not segments:
            raise FormatterError("No segments to format.")

        try:
            srt_blocks: list[str] = []

            for segment in segments:
                clean_text = self._sanitize_text(segment.text)

                if not clean_text.strip():
                    continue

                block = (
                    f"{segment.id + 1}\n"
                    f"{self._format_timestamp(segment.start)} --> "
                    f"{self._format_timestamp(segment.end)}\n"
                    f"{clean_text}\n"
                )
                srt_blocks.append(block)

            result = "\n".join(srt_blocks)
            logger.info("Formatted %d segments to SRT", len(srt_blocks))

            return result

        except FormatterError:
            raise
        except Exception as e:
            logger.exception("Formatting failed")
            raise FormatterError(f"Formatting failed: {type(e).__name__}") from e

    def save(self, content: str, filename: str) -> Path:
        """
        Save SRT content to file using atomic write.

        Writes to a temporary file first, then renames to prevent
        corruption if the process is interrupted.

        Args:
            content:  SRT-formatted string content.
            filename: Output filename (without extension).

        Returns:
            Path to the saved .srt file.

        Raises:
            FormatterError: If the save operation fails.
        """
        try:
            safe_name = sanitize_filename(filename)
            output_path = self.output_dir / f"{safe_name}.srt"

            # --- Atomic write ---
            temp_fd = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".srt.tmp",
                dir=self.output_dir,
                delete=False,
                encoding="utf-8",
            )

            try:
                temp_path = Path(temp_fd.name)
                temp_fd.write(content)
                temp_fd.flush()
                temp_fd.close()

                temp_path.replace(output_path)

            except Exception:
                temp_path = Path(temp_fd.name)
                if temp_path.exists():
                    temp_path.unlink()
                raise

            logger.info("SRT file saved: %s", output_path)
            return output_path

        except FormatterError:
            raise
        except Exception as e:
            logger.exception("Failed to save .srt file")
            raise FormatterError(f"Failed to save file: {type(e).__name__}") from e

    # ----------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """
        Convert seconds to SRT timestamp format: HH:MM:SS,mmm

        Args:
            seconds: Time in seconds.

        Returns:
            SRT-formatted timestamp string.
        """
        if seconds < 0:
            seconds = 0.0

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Strip dangerous control characters from text content.

        Preserves newlines and tabs; removes all other control characters
        (0x00-0x1F) and normalizes excessive whitespace.

        Args:
            text: Raw transcription text.

        Returns:
            Sanitized text.
        """
        cleaned = "".join(
            char for char in text if char == "\n" or char == "\t" or not (0 <= ord(char) < 32)
        )

        lines = [line.strip() for line in cleaned.split("\n")]
        return "\n".join(line for line in lines if line)
