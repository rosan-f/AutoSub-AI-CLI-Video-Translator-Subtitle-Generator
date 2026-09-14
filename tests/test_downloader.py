"""Tests for the Downloader module (unit tests, no network calls)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from autosub_ai.core.downloader import (
    AudioDownloader,
    DownloadProgress,
    DownloadResult,
    SUPPORTED_AUDIO_FORMATS,
)
from autosub_ai.exceptions import DownloadError, InvalidURLError


# ================================================================
# AudioDownloader — Initialization
# ================================================================


class TestAudioDownloaderInit:
    """Tests for AudioDownloader initialization."""

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_creates_output_dir(self, _mock_which, tmp_download_dir: Path) -> None:
        """Downloader must create the output directory if it does not exist."""
        new_dir = tmp_download_dir / "new_subdir"
        downloader = AudioDownloader(output_dir=new_dir)
        assert downloader.output_dir.exists()

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_default_audio_format(self, _mock_which, tmp_download_dir: Path) -> None:
        """Default audio format must be wav."""
        downloader = AudioDownloader(output_dir=tmp_download_dir)
        assert downloader.audio_format == "wav"

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_invalid_format_raises(self, _mock_which, tmp_download_dir: Path) -> None:
        """Unsupported audio formats must be rejected."""
        with pytest.raises(DownloadError, match="Unsupported audio format"):
            AudioDownloader(output_dir=tmp_download_dir, audio_format="aac")

    @patch("shutil.which", return_value=None)
    def test_missing_ffmpeg_raises(self, _mock_which, tmp_download_dir: Path) -> None:
        """Missing FFmpeg must raise DownloadError."""
        with pytest.raises(DownloadError, match="FFmpeg"):
            AudioDownloader(output_dir=tmp_download_dir)


# ================================================================
# AudioDownloader — Download
# ================================================================


class TestAudioDownloaderDownload:
    """Tests for AudioDownloader.download()."""

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_invalid_url_raises(self, _mock_which, tmp_download_dir: Path) -> None:
        """Download with a non-whitelisted URL must raise InvalidURLError."""
        downloader = AudioDownloader(output_dir=tmp_download_dir)
        with pytest.raises(InvalidURLError):
            downloader.download("https://evil-site.com/hack")

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_empty_url_raises(self, _mock_which, tmp_download_dir: Path) -> None:
        """Download with an empty URL must raise InvalidURLError."""
        downloader = AudioDownloader(output_dir=tmp_download_dir)
        with pytest.raises(InvalidURLError):
            downloader.download("")


# ================================================================
# AudioDownloader — Cleanup
# ================================================================


class TestAudioDownloaderCleanup:
    """Tests for AudioDownloader.cleanup()."""

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_removes_temp_files(self, _mock_which, tmp_download_dir: Path) -> None:
        """cleanup() must remove .part and .temp files."""
        # Create temp files
        (tmp_download_dir / "video.part").write_text("data")
        (tmp_download_dir / "video.ytdl").write_text("data")
        (tmp_download_dir / "audio.wav").write_text("data")

        downloader = AudioDownloader(output_dir=tmp_download_dir)
        removed = downloader.cleanup()

        assert removed == 2
        assert (tmp_download_dir / "audio.wav").exists()
        assert not (tmp_download_dir / "video.part").exists()
        assert not (tmp_download_dir / "video.ytdl").exists()

    @patch("shutil.which", return_value="/usr/bin/ffmpeg")
    def test_preserves_keep_file(self, _mock_which, tmp_download_dir: Path) -> None:
        """cleanup() must not remove the file specified as keep_file."""
        keep = tmp_download_dir / "important.temp"
        keep.write_text("data")

        downloader = AudioDownloader(output_dir=tmp_download_dir)
        removed = downloader.cleanup(keep_file=keep)

        assert removed == 0
        assert keep.exists()


# ================================================================
# Data Models
# ================================================================


class TestDownloadResult:
    """Tests for DownloadResult."""

    def test_stores_data(self) -> None:
        """DownloadResult must store all fields correctly."""
        result = DownloadResult(
            audio_path=Path("/tmp/test.wav"),
            title="Test Video",
            duration=120.5,
            source_url="https://www.youtube.com/watch?v=test",
            file_size=1024000,
        )
        assert result.title == "Test Video"
        assert result.duration == 120.5
        assert result.file_size == 1024000

    def test_default_file_size(self) -> None:
        """file_size must default to 0."""
        result = DownloadResult(
            audio_path=Path("/tmp/test.wav"),
            title="Test",
            duration=60.0,
            source_url="https://www.youtube.com/watch?v=test",
        )
        assert result.file_size == 0


class TestDownloadProgress:
    """Tests for DownloadProgress."""

    def test_downloading_state(self) -> None:
        """DownloadProgress must represent download state."""
        progress = DownloadProgress(
            status="downloading",
            downloaded_bytes=5000,
            total_bytes=10000,
            percent=50.0,
        )
        assert progress.status == "downloading"
        assert progress.percent == 50.0

    def test_default_values(self) -> None:
        """DownloadProgress must have sensible defaults."""
        progress = DownloadProgress(status="complete")
        assert progress.downloaded_bytes == 0
        assert progress.speed == 0.0


class TestSupportedFormats:
    """Tests for format configuration."""

    @pytest.mark.parametrize("fmt", ["wav", "mp3", "m4a", "flac", "opus"])
    def test_all_formats_listed(self, fmt: str) -> None:
        """All documented formats must be in SUPPORTED_AUDIO_FORMATS."""
        assert fmt in SUPPORTED_AUDIO_FORMATS
