"""
AutoSub-AI — Input Validators

All user-facing input from CLI arguments or configuration must pass
through these validators before processing.

Principle: treat all user input as untrusted.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from autosub_ai.exceptions import InvalidURLError, ValidationError

# ================================================================
# Domain Whitelist
# ================================================================

ALLOWED_DOMAINS: frozenset[str] = frozenset({
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "music.youtube.com",
})

# ================================================================
# Model Configuration
# ================================================================

VALID_MODEL_SIZES: frozenset[str] = frozenset({
    "tiny",
    "base",
    "small",
    "medium",
    "large",
})

# ================================================================
# URL Validation
# ================================================================

URL_PATTERN = re.compile(
    r"^https?://"
    r"[a-zA-Z0-9]"
    r"[a-zA-Z0-9\-\.]*"
    r"\.[a-zA-Z]{2,}"
    r"(/[^\s]*)?$",
)

MAX_URL_LENGTH = 2048


def validate_url(url: str) -> str:
    """
    Validate a video URL against the domain whitelist and format rules.

    Args:
        url: The URL to validate.

    Returns:
        The validated and cleaned URL.

    Raises:
        InvalidURLError: If the URL is invalid or the domain is not whitelisted.
    """
    if not url or not isinstance(url, str):
        raise InvalidURLError("Empty or non-string URL")

    url = url.strip()

    # --- Length check ---
    if len(url) > MAX_URL_LENGTH:
        raise InvalidURLError(f"URL exceeds maximum length ({MAX_URL_LENGTH} chars)")

    # --- Parse and validate components ---
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise InvalidURLError(url) from e

    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(f"Unsupported scheme: {parsed.scheme}")

    # --- Reject embedded credentials ---
    if parsed.username or parsed.password:
        raise InvalidURLError("URL must not contain credentials")

    domain = parsed.hostname
    if domain is None or domain not in ALLOWED_DOMAINS:
        raise InvalidURLError(
            f"Domain '{domain}' is not supported. "
            f"Allowed: {', '.join(sorted(ALLOWED_DOMAINS))}"
        )

    # --- Format check ---
    if not URL_PATTERN.match(url):
        raise InvalidURLError(url)

    return url


# ================================================================
# Model Validation
# ================================================================


def validate_model_size(model: str) -> str:
    """
    Validate a Whisper model size identifier.

    Args:
        model: Model name to validate.

    Returns:
        Validated model name (lowercase).

    Raises:
        ValidationError: If the model name is not recognized.
    """
    if not model or not isinstance(model, str):
        raise ValidationError("Model size must not be empty")

    cleaned = model.strip().lower()

    if cleaned not in VALID_MODEL_SIZES:
        raise ValidationError(
            f"Model '{cleaned}' is not valid. "
            f"Available: {', '.join(sorted(VALID_MODEL_SIZES))}"
        )

    return cleaned


# ================================================================
# File Path Validation
# ================================================================


def validate_file_path(path: Path | str) -> Path:
    """
    Validate a file path for existence and safety.

    Args:
        path: Path to the file to validate.

    Returns:
        Resolved absolute Path.

    Raises:
        ValidationError: If the path is invalid, unsafe, or does not exist.
    """
    if not path:
        raise ValidationError("File path must not be empty")

    path = Path(path)

    # --- Path traversal guard ---
    path_str = str(path)
    if ".." in path_str:
        raise ValidationError(f"Path must not contain '..': {path_str}")

    resolved = path.resolve()

    if not resolved.exists():
        raise ValidationError(f"File not found: {resolved.name}")

    if resolved.is_dir():
        raise ValidationError(f"Path is a directory, not a file: {resolved.name}")

    return resolved
