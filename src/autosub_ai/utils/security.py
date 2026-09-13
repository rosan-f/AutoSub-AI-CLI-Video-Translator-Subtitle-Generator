"""
AutoSub-AI — Security Utilities

Provides cross-cutting security functions used throughout the application:
- Filename sanitization (prevent injection and dangerous characters)
- Safe path resolution (prevent directory traversal attacks)
- File permission inspection
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from autosub_ai.exceptions import SecurityError

logger = logging.getLogger(__name__)

# ================================================================
# Constants
# ================================================================

SAFE_FILENAME_PATTERN = re.compile(r"[^\w\s\-\.\(\)\[\]]", re.UNICODE)

MAX_FILENAME_LENGTH = 200

RESERVED_NAMES: frozenset[str] = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    ".", "..",
})


# ================================================================
# Filename Sanitization
# ================================================================


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing dangerous characters.

    Ensures the filename is safe for all major filesystems and
    contains no path traversal components.

    Args:
        filename: Raw filename (e.g., from a video title).

    Returns:
        Sanitized filename string.

    Raises:
        SecurityError: If the filename cannot be sanitized.
    """
    if not filename or not isinstance(filename, str):
        return "untitled"

    cleaned = filename.strip()

    # --- Extract basename only ---
    cleaned = os.path.basename(cleaned)

    # --- Remove unsafe characters ---
    cleaned = SAFE_FILENAME_PATTERN.sub("_", cleaned)

    # --- Collapse multiple underscores/spaces ---
    cleaned = re.sub(r"[_\s]+", "_", cleaned)

    # --- Strip leading/trailing punctuation ---
    cleaned = cleaned.strip("_. ")

    # --- Block reserved names ---
    name_upper = cleaned.upper().split(".")[0]
    if name_upper in RESERVED_NAMES:
        cleaned = f"file_{cleaned}"

    # --- Truncate ---
    if len(cleaned) > MAX_FILENAME_LENGTH:
        cleaned = cleaned[:MAX_FILENAME_LENGTH]

    # --- Fallback ---
    if not cleaned:
        return "untitled"

    return cleaned


# ================================================================
# Path Traversal Guard
# ================================================================


def safe_resolve_path(base_dir: Path, target_path: Path) -> Path:
    """
    Resolve a path safely, ensuring the result stays within base_dir.

    Prevents directory traversal attacks where paths like
    '../../etc/passwd' escape the allowed directory.

    Args:
        base_dir:    The allowed root directory.
        target_path: The target path to resolve.

    Returns:
        Resolved path guaranteed to be within base_dir.

    Raises:
        SecurityError: If the resolved path escapes base_dir.
    """
    base_resolved = base_dir.resolve()

    if not target_path.is_absolute():
        full_path = (base_resolved / target_path).resolve()
    else:
        full_path = target_path.resolve()

    try:
        full_path.relative_to(base_resolved)
    except ValueError:
        logger.warning(
            "Path traversal detected: base=%s, target=%s, resolved=%s",
            base_resolved,
            target_path,
            full_path,
        )
        raise SecurityError(
            f"Access denied: path '{target_path}' resolves outside the allowed directory."
        )

    return full_path


# ================================================================
# Permission Inspection
# ================================================================


def check_file_permissions(path: Path) -> dict[str, bool]:
    """
    Inspect file or directory permissions.

    Args:
        path: Path to the file or directory.

    Returns:
        Dictionary mapping permission names to boolean status.
    """
    resolved = path.resolve()

    return {
        "exists": resolved.exists(),
        "readable": os.access(resolved, os.R_OK) if resolved.exists() else False,
        "writable": os.access(resolved, os.W_OK) if resolved.exists() else False,
        "executable": os.access(resolved, os.X_OK) if resolved.exists() else False,
        "is_file": resolved.is_file() if resolved.exists() else False,
        "is_dir": resolved.is_dir() if resolved.exists() else False,
    }
