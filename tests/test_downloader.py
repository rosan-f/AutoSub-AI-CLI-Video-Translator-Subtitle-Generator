"""Tests for the Downloader module (unit tests, no network calls)."""

from __future__ import annotations

from pathlib import Path

import pytest

from autosub_ai.core.downloader import AudioDownloader, DownloadResult
from autosub_ai.exceptions import InvalidURLError


class TestAudioDownloader:
    """Tests for AudioDownloader."""

    def test_init_creates_output_dir(self, tmp_download_dir: Path) -> None:
        """Downloader must create the output directory if it does not exist."""
        new_dir = tmp_download_dir / "new_subdir"
        downloader = AudioDownloader(output_dir=new_dir)
        assert downloader.output_dir.exists()

    def test_download_invalid_url_raises(self, tmp_download_dir: Path) -> None:
        """Download with a non-whitelisted URL must raise InvalidURLError."""
        downloader = AudioDownloader(output_dir=tmp_download_dir)
        with pytest.raises(InvalidURLError):
            downloader.download("https://evil-site.com/hack")

    def test_download_result_dataclass(self) -> None:
        """DownloadResult must store data correctly."""
        result = DownloadResult(
            audio_path=Path("/tmp/test.wav"),
            title="Test Video",
            duration=120.5,
            source_url="https://www.youtube.com/watch?v=test",
        )
        assert result.title == "Test Video"
        assert result.duration == 120.5
