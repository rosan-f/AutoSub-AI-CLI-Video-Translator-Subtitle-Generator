"""
Settings Module — Manajemen konfigurasi berbasis Pydantic.

Semua konfigurasi dimuat dari environment variables dan/atau file .env
dengan validasi ketat menggunakan Pydantic v2.

Urutan prioritas:
1. CLI arguments (tertinggi)
2. Environment variables
3. File .env
4. Default values (terendah)
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class ModelSize(str, Enum):
    """Ukuran model Whisper yang tersedia."""

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class LogLevel(str, Enum):
    """Level logging yang tersedia."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AppSettings(BaseSettings):
    """
    Konfigurasi aplikasi AutoSub-AI.

    Semua setting divalidasi secara ketat oleh Pydantic v2.
    Nilai dimuat otomatis dari environment variables dengan prefix AUTOSUB_.
    """

    model_config = SettingsConfigDict(
        env_prefix="AUTOSUB_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Abaikan env vars yang tidak dikenal
    )

    # === Model Settings ===
    model_size: ModelSize = Field(
        default=ModelSize.BASE,
        description="Ukuran model Whisper (tiny/base/small/medium/large).",
    )

    # === Language Settings ===
    target_language: str = Field(
        default="id",
        min_length=2,
        max_length=5,
        description="Kode bahasa target (ISO 639-1).",
    )

    # === Path Settings ===
    output_dir: Path = Field(
        default=Path("./output"),
        description="Direktori output file .srt.",
    )
    download_dir: Path = Field(
        default=Path("./downloads"),
        description="Direktori penyimpanan audio sementara.",
    )

    # === Performance Settings ===
    use_gpu: bool = Field(
        default=True,
        description="Aktifkan akselerasi GPU (CUDA).",
    )

    # === Logging ===
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Level logging aplikasi.",
    )

    @field_validator("target_language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        """Validasi kode bahasa: hanya huruf lowercase."""
        cleaned = v.lower().strip()
        if not cleaned.isalpha():
            msg = f"Kode bahasa harus berupa huruf saja, diterima: '{v}'"
            raise ValueError(msg)
        return cleaned

    @field_validator("output_dir", "download_dir")
    @classmethod
    def validate_paths(cls, v: Path) -> Path:
        """Pastikan path tidak mengandung komponen berbahaya."""
        path_str = str(v)
        # Cegah path traversal
        if ".." in path_str:
            msg = f"Path tidak boleh mengandung '..': {path_str}"
            raise ValueError(msg)
        return v


def get_settings() -> AppSettings:
    """
    Muat dan kembalikan settings aplikasi.

    Returns:
        AppSettings instance yang sudah divalidasi.
    """
    settings = AppSettings()
    logger.debug("Settings dimuat: model=%s, gpu=%s", settings.model_size, settings.use_gpu)
    return settings
