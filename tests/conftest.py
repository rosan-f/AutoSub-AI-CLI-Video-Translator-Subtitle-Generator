"""
Pytest Fixtures — Konfigurasi dan fixtures bersama untuk test suite.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Direktori output sementara untuk testing."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def tmp_download_dir(tmp_path: Path) -> Path:
    """Direktori download sementara untuk testing."""
    download = tmp_path / "downloads"
    download.mkdir()
    return download


@pytest.fixture
def sample_audio_path(tmp_path: Path) -> Path:
    """Path ke file audio dummy untuk testing."""
    audio = tmp_path / "test_audio.wav"
    audio.write_bytes(b"\x00" * 1024)  # File dummy
    return audio


@pytest.fixture
def valid_youtube_url() -> str:
    """URL YouTube yang valid untuk testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def invalid_urls() -> list[str]:
    """List URL yang tidak valid untuk testing."""
    return [
        "",
        "not-a-url",
        "ftp://example.com/video",
        "https://evil-site.com/malware",
        "javascript:alert(1)",
        "https://youtube.com/" + "a" * 3000,  # URL terlalu panjang
        "https://user:pass@youtube.com/watch",  # URL dengan credentials
    ]
