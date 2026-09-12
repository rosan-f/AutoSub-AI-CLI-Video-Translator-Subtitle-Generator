"""
Validators Module — Validasi dan sanitasi input pengguna.

Semua input dari CLI atau konfigurasi HARUS melewati validator ini
sebelum diproses. Prinsip: treat all user input as untrusted.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from autosub_ai.exceptions import InvalidURLError, ValidationError

# === Domain Whitelist ===
# Hanya URL dari domain ini yang diizinkan
ALLOWED_DOMAINS: frozenset[str] = frozenset({
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "music.youtube.com",
})

# === Model Sizes ===
VALID_MODEL_SIZES: frozenset[str] = frozenset({
    "tiny",
    "base",
    "small",
    "medium",
    "large",
})

# Pola URL yang valid
URL_PATTERN = re.compile(
    r"^https?://"  # Harus dimulai dengan http:// atau https://
    r"[a-zA-Z0-9]"  # Domain harus dimulai dengan alphanumeric
    r"[a-zA-Z0-9\-\.]*"  # Domain body
    r"\.[a-zA-Z]{2,}"  # TLD minimal 2 karakter
    r"(/[^\s]*)?$",  # Path (opsional)
)

# Panjang URL maksimum (cegah DoS)
MAX_URL_LENGTH = 2048


def validate_url(url: str) -> str:
    """
    Validasi URL video terhadap whitelist dan format.

    Args:
        url: URL yang akan divalidasi.

    Returns:
        URL yang sudah divalidasi dan dibersihkan.

    Raises:
        InvalidURLError: Jika URL tidak valid atau domain tidak diizinkan.
    """
    if not url or not isinstance(url, str):
        raise InvalidURLError("URL kosong atau bukan string")

    # Strip whitespace
    url = url.strip()

    # Cek panjang
    if len(url) > MAX_URL_LENGTH:
        raise InvalidURLError(f"URL terlalu panjang (maks {MAX_URL_LENGTH} karakter)")

    # Cek format dasar
    if not URL_PATTERN.match(url):
        raise InvalidURLError(url)

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise InvalidURLError(url) from e

    # Validasi scheme (hanya HTTPS/HTTP)
    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(f"Scheme tidak didukung: {parsed.scheme}")

    # Validasi domain terhadap whitelist
    domain = parsed.hostname
    if domain is None or domain not in ALLOWED_DOMAINS:
        raise InvalidURLError(
            f"Domain '{domain}' tidak didukung. "
            f"Domain yang diizinkan: {', '.join(sorted(ALLOWED_DOMAINS))}"
        )

    # Cegah URL dengan credentials (user:pass@host)
    if parsed.username or parsed.password:
        raise InvalidURLError("URL tidak boleh mengandung credentials")

    return url


def validate_model_size(model: str) -> str:
    """
    Validasi ukuran model Whisper.

    Args:
        model: Nama model yang akan divalidasi.

    Returns:
        Nama model yang sudah divalidasi (lowercase).

    Raises:
        ValidationError: Jika model tidak valid.
    """
    if not model or not isinstance(model, str):
        raise ValidationError("Model size tidak boleh kosong")

    cleaned = model.strip().lower()

    if cleaned not in VALID_MODEL_SIZES:
        raise ValidationError(
            f"Model '{cleaned}' tidak valid. "
            f"Pilihan: {', '.join(sorted(VALID_MODEL_SIZES))}"
        )

    return cleaned


def validate_file_path(path: Path | str) -> Path:
    """
    Validasi path file — pastikan ada dan aman.

    Args:
        path: Path ke file yang akan divalidasi.

    Returns:
        Path yang sudah divalidasi dan di-resolve.

    Raises:
        ValidationError: Jika path tidak valid atau tidak aman.
    """
    if not path:
        raise ValidationError("Path file tidak boleh kosong")

    path = Path(path)

    # Cegah path traversal
    path_str = str(path)
    if ".." in path_str:
        raise ValidationError(f"Path tidak boleh mengandung '..': {path_str}")

    # Resolve ke absolute path
    resolved = path.resolve()

    # Pastikan file ada
    if not resolved.exists():
        raise ValidationError(f"File tidak ditemukan: {resolved.name}")

    # Pastikan bukan direktori
    if resolved.is_dir():
        raise ValidationError(f"Path adalah direktori, bukan file: {resolved.name}")

    return resolved
