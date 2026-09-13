"""
Shared pytest fixtures for the AutoSub-AI test suite.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ================================================================
# Directory Fixtures
# ================================================================


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def tmp_download_dir(tmp_path: Path) -> Path:
    """Temporary download directory."""
    download = tmp_path / "downloads"
    download.mkdir()
    return download


# ================================================================
# File Fixtures
# ================================================================


@pytest.fixture
def sample_audio_path(tmp_path: Path) -> Path:
    """Dummy audio file for testing."""
    audio = tmp_path / "test_audio.wav"
    audio.write_bytes(b"\x00" * 1024)
    return audio


# ================================================================
# URL Fixtures
# ================================================================


@pytest.fixture
def valid_youtube_url() -> str:
    """A valid YouTube URL."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def invalid_urls() -> list[str]:
    """Collection of invalid URLs for negative testing."""
    return [
        "",
        "not-a-url",
        "ftp://example.com/video",
        "https://evil-site.com/malware",
        "javascript:alert(1)",
        "https://youtube.com/" + "a" * 3000,
        "https://user:pass@youtube.com/watch",
    ]
