"""
AutoSub-AI — Downloader Module

Handles audio extraction from video URLs using yt-dlp.

Security measures:
- URL validation against domain whitelist
- Output filename sanitization
- Subprocess calls via list args (no shell injection)
- Configurable timeout to prevent hangs
- Temporary file cleanup on failure
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

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
MAX_RETRIES = 3
SUPPORTED_AUDIO_FORMATS = frozenset({"wav", "mp3", "m4a", "flac", "opus"})


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
    file_size: int = 0            # File size in bytes


@dataclass
class DownloadProgress:
    """Snapshot of download progress state."""

    status: str                   # "downloading", "processing", "complete", "error"
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0            # Bytes per second
    eta: float = 0.0              # Estimated time remaining (seconds)
    percent: float = 0.0


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
        output_dir:    Directory for downloaded audio files.
        audio_format:  Output audio format (default: wav).
        sample_rate:   Audio sample rate (default: 16000 Hz).
        timeout:       Download timeout in seconds.
        on_progress:   Optional callback for progress updates.
    """

    output_dir: Path = field(default_factory=lambda: Path("./downloads"))
    audio_format: str = DEFAULT_AUDIO_FORMAT
    sample_rate: int = DEFAULT_SAMPLE_RATE
    timeout: int = DEFAULT_TIMEOUT
    on_progress: Callable[[DownloadProgress], None] | None = field(
        default=None, repr=False
    )

    def __post_init__(self) -> None:
        """Validate configuration and create output directory."""
        # --- Validate audio format ---
        if self.audio_format not in SUPPORTED_AUDIO_FORMATS:
            raise DownloadError(
                f"Unsupported audio format: '{self.audio_format}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_AUDIO_FORMATS))}"
            )

        # --- Verify FFmpeg is available ---
        if not shutil.which("ffmpeg"):
            raise DownloadError(
                "FFmpeg is not installed or not in PATH. "
                "Install it with: sudo apt install ffmpeg"
            )

        self.output_dir = self.output_dir.resolve()
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
            import yt_dlp

            ydl_opts = self._build_ydl_options()

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # --- Extract metadata (dry run) ---
                self._emit_progress(DownloadProgress(status="extracting_info"))

                info = ydl.extract_info(validated_url, download=False)
                if info is None:
                    raise DownloadError(f"Cannot extract info from: {validated_url}")

                title = sanitize_filename(info.get("title", "untitled"))
                duration = float(info.get("duration", 0))
                logger.info("Video: %s (%.1f min)", title, duration / 60)

                # --- Download audio stream ---
                self._emit_progress(DownloadProgress(status="downloading"))

                ydl.download([validated_url])

                # --- Locate output file ---
                audio_path = self._find_output_file(title)

                file_size = audio_path.stat().st_size
                logger.info(
                    "Audio downloaded: %s (%.2f MB)",
                    audio_path.name,
                    file_size / (1024 * 1024),
                )

                self._emit_progress(DownloadProgress(status="complete", percent=100.0))

                return DownloadResult(
                    audio_path=audio_path,
                    title=title,
                    duration=duration,
                    source_url=validated_url,
                    file_size=file_size,
                )

        except ImportError:
            raise DownloadError(
                "yt-dlp is not installed. Run: pip install yt-dlp"
            ) from None
        except (DownloadError, InvalidURLError):
            raise
        except Exception as e:
            self._emit_progress(DownloadProgress(status="error"))
            logger.exception("Download failed")
            raise DownloadError(f"Download failed: {type(e).__name__}") from e

    def extract_info(self, url: str) -> dict[str, Any]:
        """
        Extract video metadata without downloading.

        Args:
            url: A valid, whitelisted video URL.

        Returns:
            Dictionary of video metadata (title, duration, formats, etc.).

        Raises:
            InvalidURLError: If the URL is invalid.
            DownloadError:   If metadata extraction fails.
        """
        validated_url = validate_url(url)

        try:
            import yt_dlp

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": self.timeout,
                "no_exec": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(validated_url, download=False)
                if info is None:
                    raise DownloadError(f"Cannot extract info from: {validated_url}")

                return {
                    "title": info.get("title", "Unknown"),
                    "duration": float(info.get("duration", 0)),
                    "uploader": info.get("uploader", "Unknown"),
                    "view_count": info.get("view_count", 0),
                    "upload_date": info.get("upload_date", "Unknown"),
                    "description": info.get("description", "")[:500],
                }

        except ImportError:
            raise DownloadError(
                "yt-dlp is not installed. Run: pip install yt-dlp"
            ) from None
        except DownloadError:
            raise
        except Exception as e:
            raise DownloadError(f"Info extraction failed: {type(e).__name__}") from e

    def cleanup(self, keep_file: Path | None = None) -> int:
        """
        Remove temporary files from the download directory.

        Args:
            keep_file: Optional path to preserve (skip deletion).

        Returns:
            Number of files removed.
        """
        removed = 0

        if not self.output_dir.exists():
            return removed

        temp_extensions = {".part", ".ytdl", ".temp", ".tmp"}

        for file_path in self.output_dir.iterdir():
            if not file_path.is_file():
                continue

            if keep_file and file_path.resolve() == keep_file.resolve():
                continue

            if file_path.suffix in temp_extensions:
                try:
                    file_path.unlink()
                    removed += 1
                    logger.debug("Removed temp file: %s", file_path.name)
                except OSError as e:
                    logger.warning("Failed to remove %s: %s", file_path.name, e)

        if removed > 0:
            logger.info("Cleaned up %d temporary file(s)", removed)

        return removed

    # ----------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------

    def _build_ydl_options(self) -> dict:
        """
        Build a safe yt-dlp configuration dictionary.

        Returns:
            yt-dlp options with security-hardened defaults.
        """
        opts: dict[str, Any] = {
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
            # --- Network ---
            "socket_timeout": self.timeout,
            "retries": MAX_RETRIES,
            "fragment_retries": MAX_RETRIES,
            # --- Security ---
            "no_exec": True,
            "geo_bypass": False,
            "nocheckcertificate": False,
        }

        # --- Progress hook ---
        if self.on_progress is not None:
            opts["progress_hooks"] = [self._ydl_progress_hook]

        return opts

    def _ydl_progress_hook(self, d: dict) -> None:
        """
        Translate yt-dlp progress events into DownloadProgress callbacks.

        Args:
            d: Progress dictionary from yt-dlp.
        """
        if self.on_progress is None:
            return

        status = d.get("status", "unknown")

        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total > 0 else 0.0

            self.on_progress(DownloadProgress(
                status="downloading",
                downloaded_bytes=downloaded,
                total_bytes=total,
                speed=d.get("speed") or 0.0,
                eta=d.get("eta") or 0.0,
                percent=percent,
            ))

        elif status == "finished":
            self.on_progress(DownloadProgress(
                status="processing",
                percent=100.0,
            ))

    def _find_output_file(self, title: str) -> Path:
        """
        Locate the downloaded audio file in the output directory.

        yt-dlp may sanitize the title differently, so we search by
        expected name first, then fall back to the most recent file.

        Args:
            title: Sanitized video title.

        Returns:
            Path to the audio file.

        Raises:
            DownloadError: If no matching file is found.
        """
        # --- Try exact match ---
        exact_path = safe_resolve_path(
            self.output_dir, Path(f"{title}.{self.audio_format}")
        )
        if exact_path.exists():
            return exact_path

        # --- Fallback: find most recent file with matching extension ---
        candidates = sorted(
            self.output_dir.glob(f"*.{self.audio_format}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if candidates:
            logger.debug(
                "Exact match not found for '%s', using: %s",
                title,
                candidates[0].name,
            )
            return candidates[0]

        raise DownloadError(
            f"Audio file not found after download. "
            f"Expected: {title}.{self.audio_format}"
        )

    def _emit_progress(self, progress: DownloadProgress) -> None:
        """Emit a progress event if a callback is registered."""
        if self.on_progress is not None:
            self.on_progress(progress)
