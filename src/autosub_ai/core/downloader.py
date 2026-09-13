"""
AutoSub-AI — Downloader Module

Handles audio extraction from video URLs using yt-dlp.

Security measures:
- URL validation against domain whitelist
- Output filename sanitization
- Subprocess calls via list args (no shell injection)
- Configurable timeout to prevent hangs
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from autosub_ai.exceptions import DownloadError, InvalidURLError
from autosub_ai.utils.security import safe_resolve_path, sanitize_filename
from autosub_ai.utils.validators import validate_url

logger = logging.getLogger(__name__)

# ================================================================
# Constants
# ================================================================

DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_AUDIO_QUALITY = "0"
DEFAULT_SAMPLE_RATE = 16000       # 16kHz — optimal for Whisper
DEFAULT_TIMEOUT = 600             # 10 minutes


# ================================================================
# Data Models
# ================================================================


@dataclass
class DownloadResult:
    """Container for audio download results."""

    audio_path: Path
    title: str
    duration: float               # Duration in seconds
    source_url: str


# ================================================================
# Downloader
# ================================================================


@dataclass
class AudioDownloader:
    """
    Manages audio download and extraction from video sources.

    Uses yt-dlp as the backend to support multiple video platforms
    (YouTube, etc.) without downloading the full video stream.

    Attributes:
        output_dir:   Directory for downloaded audio files.
        audio_format: Output audio format (default: wav).
        sample_rate:  Audio sample rate (default: 16000 Hz).
        timeout:      Download timeout in seconds.
    """

    output_dir: Path = field(default_factory=lambda: Path("./downloads"))
    audio_format: str = DEFAULT_AUDIO_FORMAT
    sample_rate: int = DEFAULT_SAMPLE_RATE
    timeout: int = DEFAULT_TIMEOUT

    def __post_init__(self) -> None:
        """Validate configuration and create output directory."""
        self.output_dir = safe_resolve_path(Path.cwd(), self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Output directory: %s", self.output_dir)

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def download(self, url: str) -> DownloadResult:
        """
        Download and extract audio from a video URL.

        Args:
            url: A valid, whitelisted video URL.

        Returns:
            DownloadResult containing the path to the extracted audio.

        Raises:
            InvalidURLError: If the URL is invalid or not whitelisted.
            DownloadError:   If the download process fails.
        """
        validated_url = validate_url(url)
        logger.info("Starting audio download: %s", validated_url)

        try:
            import yt_dlp  # noqa: S404

            ydl_opts = self._build_ydl_options()

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # --- Extract metadata (no download) ---
                info = ydl.extract_info(validated_url, download=False)
                if info is None:
                    raise DownloadError(f"Cannot extract info from: {validated_url}")

                title = sanitize_filename(info.get("title", "untitled"))
                duration = float(info.get("duration", 0))
                logger.info("Video: %s (%.1f min)", title, duration / 60)

                # --- Download audio stream ---
                ydl.download([validated_url])

                audio_path = self.output_dir / f"{title}.{self.audio_format}"
                if not audio_path.exists():
                    raise DownloadError(f"Audio file not found after download: {audio_path}")

                logger.info("Audio downloaded: %s", audio_path)

                return DownloadResult(
                    audio_path=audio_path,
                    title=title,
                    duration=duration,
                    source_url=validated_url,
                )

        except ImportError:
            raise DownloadError(
                "yt-dlp is not installed. Run: pip install yt-dlp"
            ) from None
        except DownloadError:
            raise
        except Exception as e:
            logger.exception("Download failed")
            raise DownloadError(f"Download failed: {type(e).__name__}") from e

    # ----------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------

    def _build_ydl_options(self) -> dict:
        """
        Build a safe yt-dlp configuration dictionary.

        Returns:
            yt-dlp options with security-hardened defaults.
        """
        return {
            # --- Format ---
            "format": "bestaudio/best",
            "extractaudio": True,
            "audioformat": self.audio_format,
            "audioquality": DEFAULT_AUDIO_QUALITY,
            # --- Output ---
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
            # --- Post-processing ---
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": DEFAULT_AUDIO_QUALITY,
                }
            ],
            # --- Logging ---
            "quiet": True,
            "no_warnings": True,
            # --- Security ---
            "socket_timeout": self.timeout,
            "retries": 3,
            "no_exec": True,
            "geo_bypass": False,
        }
