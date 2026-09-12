"""
Downloader Module — Ekstraksi audio dari video menggunakan yt-dlp.

Fitur keamanan:
- Validasi URL dengan whitelist domain
- Sanitasi nama file output
- Subprocess call tanpa shell injection
- Timeout untuk mencegah hang
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from autosub_ai.exceptions import DownloadError, InvalidURLError
from autosub_ai.utils.security import safe_resolve_path, sanitize_filename
from autosub_ai.utils.validators import validate_url

logger = logging.getLogger(__name__)

# Konfigurasi default
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_AUDIO_QUALITY = "0"  # Best quality
DEFAULT_SAMPLE_RATE = 16000  # 16kHz — optimal untuk Whisper
DEFAULT_TIMEOUT = 600  # 10 menit timeout


@dataclass
class DownloadResult:
    """Hasil dari proses download audio."""

    audio_path: Path
    title: str
    duration: float  # Durasi dalam detik
    source_url: str


@dataclass
class AudioDownloader:
    """
    Mengelola download dan ekstraksi audio dari video.

    Menggunakan yt-dlp sebagai backend untuk mendukung berbagai
    platform video (YouTube, dll) tanpa perlu download video penuh.

    Attributes:
        output_dir: Direktori output untuk file audio.
        audio_format: Format audio output (default: wav).
        sample_rate: Sample rate audio (default: 16000 Hz).
        timeout: Timeout download dalam detik.
    """

    output_dir: Path = field(default_factory=lambda: Path("./downloads"))
    audio_format: str = DEFAULT_AUDIO_FORMAT
    sample_rate: int = DEFAULT_SAMPLE_RATE
    timeout: int = DEFAULT_TIMEOUT

    def __post_init__(self) -> None:
        """Validasi dan buat direktori output jika belum ada."""
        self.output_dir = safe_resolve_path(Path.cwd(), self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Output directory: %s", self.output_dir)

    def download(self, url: str) -> DownloadResult:
        """
        Download dan ekstrak audio dari URL video.

        Args:
            url: URL video yang valid (sudah divalidasi).

        Returns:
            DownloadResult dengan path ke file audio.

        Raises:
            InvalidURLError: Jika URL tidak valid.
            DownloadError: Jika proses download gagal.
        """
        # Validasi URL
        validated_url = validate_url(url)
        logger.info("Memulai download audio dari: %s", validated_url)

        try:
            # Import yt-dlp hanya saat dibutuhkan (lazy import)
            import yt_dlp  # noqa: S404

            # Konfigurasi yt-dlp yang aman
            ydl_opts = self._build_ydl_options()

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Ekstrak info terlebih dahulu (tanpa download)
                info = ydl.extract_info(validated_url, download=False)
                if info is None:
                    raise DownloadError(f"Tidak dapat mengekstrak info dari: {validated_url}")

                # Sanitasi judul untuk nama file
                title = sanitize_filename(info.get("title", "untitled"))
                duration = float(info.get("duration", 0))

                logger.info("Video: %s (%.1f menit)", title, duration / 60)

                # Download audio
                ydl.download([validated_url])

                # Tentukan path output
                audio_path = self.output_dir / f"{title}.{self.audio_format}"

                if not audio_path.exists():
                    raise DownloadError(f"File audio tidak ditemukan: {audio_path}")

                logger.info("Audio berhasil didownload: %s", audio_path)

                return DownloadResult(
                    audio_path=audio_path,
                    title=title,
                    duration=duration,
                    source_url=validated_url,
                )

        except ImportError:
            raise DownloadError(
                "yt-dlp tidak terinstal. Jalankan: pip install yt-dlp"
            ) from None
        except DownloadError:
            raise
        except Exception as e:
            logger.exception("Download gagal")
            raise DownloadError(f"Download gagal: {type(e).__name__}") from e

    def _build_ydl_options(self) -> dict:
        """
        Bangun opsi konfigurasi yt-dlp yang aman.

        Returns:
            Dictionary konfigurasi yt-dlp.
        """
        return {
            # Format: audio only, quality terbaik
            "format": "bestaudio/best",
            "extractaudio": True,
            "audioformat": self.audio_format,
            "audioquality": DEFAULT_AUDIO_QUALITY,
            # Output
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
            # Postprocessor untuk konversi format
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": DEFAULT_AUDIO_QUALITY,
                }
            ],
            # Keamanan
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": self.timeout,
            "retries": 3,
            # Nonaktifkan fitur yang bisa jadi risiko keamanan
            "no_exec": True,  # Jangan eksekusi external commands
            "geo_bypass": False,  # Jangan bypass geo-restriction
        }
