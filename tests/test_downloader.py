"""Tests untuk Downloader Module (unit tests tanpa network)."""

from __future__ import annotations

from pathlib import Path

import pytest

from autosub_ai.core.downloader import AudioDownloader, DownloadResult
from autosub_ai.exceptions import InvalidURLError


class TestAudioDownloader:
    """Tests untuk AudioDownloader."""

    def test_init_creates_output_dir(self, tmp_download_dir: Path) -> None:
        """Downloader harus membuat output dir jika belum ada."""
        new_dir = tmp_download_dir / "new_subdir"
        downloader = AudioDownloader(output_dir=new_dir)
        assert downloader.output_dir.exists()

    def test_download_invalid_url_raises(self, tmp_download_dir: Path) -> None:
        """Download dengan URL invalid harus raise InvalidURLError."""
        downloader = AudioDownloader(output_dir=tmp_download_dir)
        with pytest.raises(InvalidURLError):
            downloader.download("https://evil-site.com/hack")

    def test_download_result_dataclass(self) -> None:
        """DownloadResult harus menyimpan data dengan benar."""
        result = DownloadResult(
            audio_path=Path("/tmp/test.wav"),
            title="Test Video",
            duration=120.5,
            source_url="https://www.youtube.com/watch?v=test",
        )
        assert result.title == "Test Video"
        assert result.duration == 120.5
