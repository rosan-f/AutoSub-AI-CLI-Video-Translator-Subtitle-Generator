"""
Security Module — Utilitas keamanan untuk AutoSub-AI.

Menyediakan fungsi-fungsi keamanan yang digunakan di seluruh aplikasi:
- Sanitasi nama file (cegah injection & karakter berbahaya)
- Safe path resolution (cegah directory traversal)
- File permission checking
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from autosub_ai.exceptions import SecurityError

logger = logging.getLogger(__name__)

# Karakter yang diizinkan dalam nama file
SAFE_FILENAME_PATTERN = re.compile(r"[^\w\s\-\.\(\)\[\]]", re.UNICODE)

# Panjang nama file maksimum
MAX_FILENAME_LENGTH = 200

# Nama file yang dilarang (reserved names di Windows & Unix)
RESERVED_NAMES: frozenset[str] = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    ".", "..",
})


def sanitize_filename(filename: str) -> str:
    """
    Sanitasi nama file — hapus karakter berbahaya.

    Memastikan nama file aman untuk digunakan di semua filesystem
    dan tidak mengandung komponen path traversal.

    Args:
        filename: Nama file mentah (bisa dari judul video, dll).

    Returns:
        Nama file yang sudah disanitasi.

    Raises:
        SecurityError: Jika nama file tidak bisa disanitasi.
    """
    if not filename or not isinstance(filename, str):
        return "untitled"

    # Strip whitespace di awal/akhir
    cleaned = filename.strip()

    # Hapus komponen path (hanya ambil basename)
    cleaned = os.path.basename(cleaned)

    # Hapus karakter berbahaya
    cleaned = SAFE_FILENAME_PATTERN.sub("_", cleaned)

    # Collapse multiple underscores/spaces
    cleaned = re.sub(r"[_\s]+", "_", cleaned)

    # Strip leading/trailing underscores dan dots
    cleaned = cleaned.strip("_. ")

    # Cek reserved names
    name_upper = cleaned.upper().split(".")[0]
    if name_upper in RESERVED_NAMES:
        cleaned = f"file_{cleaned}"

    # Truncate jika terlalu panjang
    if len(cleaned) > MAX_FILENAME_LENGTH:
        cleaned = cleaned[:MAX_FILENAME_LENGTH]

    # Fallback jika hasilnya kosong
    if not cleaned:
        return "untitled"

    return cleaned


def safe_resolve_path(base_dir: Path, target_path: Path) -> Path:
    """
    Resolve path secara aman — pastikan hasil tetap di dalam base_dir.

    Mencegah directory traversal attacks di mana path seperti
    '../../etc/passwd' bisa keluar dari direktori yang diizinkan.

    Args:
        base_dir: Direktori dasar yang diizinkan.
        target_path: Path target yang akan di-resolve.

    Returns:
        Path yang sudah di-resolve dan aman.

    Raises:
        SecurityError: Jika path resolve ke luar base_dir.
    """
    # Resolve kedua path
    base_resolved = base_dir.resolve()

    # Jika target_path relatif, gabungkan dengan base
    if not target_path.is_absolute():
        full_path = (base_resolved / target_path).resolve()
    else:
        full_path = target_path.resolve()

    # Pastikan hasil masih di dalam base_dir
    try:
        full_path.relative_to(base_resolved)
    except ValueError:
        logger.warning(
            "Path traversal terdeteksi! base=%s, target=%s, resolved=%s",
            base_resolved,
            target_path,
            full_path,
        )
        raise SecurityError(
            f"Akses ditolak: path '{target_path}' berada di luar direktori yang diizinkan."
        )

    return full_path


def check_file_permissions(path: Path) -> dict[str, bool]:
    """
    Periksa permission file/direktori.

    Args:
        path: Path ke file atau direktori.

    Returns:
        Dictionary dengan status permission.
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
