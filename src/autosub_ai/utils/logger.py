"""
AutoSub-AI — Logger Module

Structured logging with Rich terminal handler.

Design constraints:
- Structured format for debugging
- Rich handler for formatted terminal output
- Sensitive information (full URLs, absolute system paths) is never logged
- Third-party library noise is suppressed
"""

from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_logger(verbose: bool = False) -> logging.Logger:
    """
    Configure and return the application root logger.

    Args:
        verbose: If True, set level to DEBUG. Default: INFO.

    Returns:
        Configured Logger instance.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # --- Rich terminal handler ---
    rich_handler = RichHandler(
        console=Console(stderr=True),
        show_time=True,
        show_path=verbose,
        rich_tracebacks=True,
        tracebacks_show_locals=verbose,
        markup=True,
    )

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[rich_handler],
        force=True,
    )

    # --- Suppress third-party noise ---
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)
    logging.getLogger("whisper").setLevel(logging.WARNING)

    logger = logging.getLogger("autosub_ai")
    logger.setLevel(level)

    if verbose:
        logger.debug("Verbose logging enabled")

    return logger
