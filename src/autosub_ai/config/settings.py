"""
AutoSub-AI — Settings Module

Pydantic v2 based configuration management.
All settings are loaded from environment variables and/or .env files
with strict validation.

Priority order (highest to lowest):
1. CLI arguments
2. Environment variables
3. .env file
4. Default values
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# ================================================================
# Enumerations
# ================================================================


class ModelSize(str, Enum):
    """Available Whisper model sizes."""

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class LogLevel(str, Enum):
    """Available logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# ================================================================
# Application Settings
# ================================================================


class AppSettings(BaseSettings):
    """
    AutoSub-AI application configuration.

    All settings are strictly validated by Pydantic v2.
    Values are loaded from environment variables prefixed with AUTOSUB_.
    """

    model_config = SettingsConfigDict(
        env_prefix="AUTOSUB_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Model ---
    model_size: ModelSize = Field(
        default=ModelSize.BASE,
        description="Whisper model size (tiny/base/small/medium/large).",
    )

    # --- Language ---
    target_language: str = Field(
        default="id",
        min_length=2,
        max_length=5,
        description="Target language code (ISO 639-1).",
    )

    # --- Paths ---
    output_dir: Path = Field(
        default=Path("./output"),
        description="Output directory for .srt files.",
    )
    download_dir: Path = Field(
        default=Path("./downloads"),
        description="Temporary audio download directory.",
    )

    # --- Performance ---
    use_gpu: bool = Field(
        default=True,
        description="Enable GPU acceleration (CUDA).",
    )

    # --- Logging ---
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Application log level.",
    )

    # ----------------------------------------------------------------
    # Validators
    # ----------------------------------------------------------------

    @field_validator("target_language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        """Validate language code: lowercase alphabetic only."""
        cleaned = v.lower().strip()
        if not cleaned.isalpha():
            msg = f"Language code must be alphabetic, received: '{v}'"
            raise ValueError(msg)
        return cleaned

    @field_validator("output_dir", "download_dir")
    @classmethod
    def validate_paths(cls, v: Path) -> Path:
        """Reject paths containing traversal components."""
        path_str = str(v)
        if ".." in path_str:
            msg = f"Path must not contain '..': {path_str}"
            raise ValueError(msg)
        return v


# ================================================================
# Factory
# ================================================================


def get_settings() -> AppSettings:
    """
    Load and return validated application settings.

    Returns:
        Fully validated AppSettings instance.
    """
    settings = AppSettings()
    logger.debug("Settings loaded: model=%s, gpu=%s", settings.model_size, settings.use_gpu)
    return settings
