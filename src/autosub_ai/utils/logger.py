"""
Logger Module — Structured logging dengan Rich handler.

Menyediakan logging yang konsisten dan aman di seluruh aplikasi.
- Format terstruktur untuk debugging
- Rich handler untuk output terminal yang cantik
- Tidak pernah log informasi sensitif (URL penuh, path absolut sistem, dll)
"""

from __future__ import annotations

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler


def setup_logger(verbose: bool = False) -> logging.Logger:
    """
    Setup dan konfigurasi root logger.

    Args:
        verbose: Jika True, set level ke DEBUG. Default: INFO.

    Returns:
        Logger instance yang sudah dikonfigurasi.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Rich handler untuk output terminal yang informatif
    rich_handler = RichHandler(
        console=Console(stderr=True),
        show_time=True,
        show_path=verbose,  # Hanya tampilkan file path di verbose mode
        rich_tracebacks=True,
        tracebacks_show_locals=verbose,  # Hanya tampilkan locals di verbose mode
        markup=True,
    )

    # Format log
    log_format = "%(message)s"

    # Konfigurasi root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[rich_handler],
        force=True,  # Override konfigurasi sebelumnya
    )

    # Set level untuk library pihak ketiga agar tidak terlalu verbose
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)
    logging.getLogger("whisper").setLevel(logging.WARNING)

    logger = logging.getLogger("autosub_ai")
    logger.setLevel(level)

    if verbose:
        logger.debug("Verbose logging diaktifkan")

    return logger
