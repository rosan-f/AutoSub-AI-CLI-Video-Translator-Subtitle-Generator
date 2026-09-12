"""
Custom Exception Hierarchy untuk AutoSub-AI.

Semua exception diorganisir dalam hierarki yang jelas agar:
- Error handling konsisten di seluruh codebase
- Pesan error aman (tidak expose stack trace internal ke user)
- Mudah di-catch secara spesifik atau general
"""


class AutoSubError(Exception):
    """Base exception untuk semua error AutoSub-AI."""

    def __init__(self, message: str = "Terjadi kesalahan pada AutoSub-AI.") -> None:
        self.message = message
        super().__init__(self.message)


# === Download Errors ===


class DownloadError(AutoSubError):
    """Error saat proses download audio dari video."""

    def __init__(self, message: str = "Gagal mengunduh audio dari video.") -> None:
        super().__init__(message)


class InvalidURLError(DownloadError):
    """URL yang diberikan tidak valid atau tidak didukung."""

    def __init__(self, url: str = "") -> None:
        sanitized = url[:200] if url else "unknown"  # Batasi panjang URL di pesan error
        super().__init__(f"URL tidak valid atau tidak didukung: {sanitized}")


# === Transcription Errors ===


class TranscriptionError(AutoSubError):
    """Error saat proses transkripsi audio."""

    def __init__(self, message: str = "Gagal melakukan transkripsi audio.") -> None:
        super().__init__(message)


class ModelLoadError(TranscriptionError):
    """Gagal memuat model Whisper."""

    def __init__(self, model_name: str = "") -> None:
        super().__init__(f"Gagal memuat model Whisper: '{model_name}'")


# === Translation Errors ===


class TranslationError(AutoSubError):
    """Error saat proses terjemahan teks."""

    def __init__(self, message: str = "Gagal melakukan terjemahan teks.") -> None:
        super().__init__(message)


# === Formatter Errors ===


class FormatterError(AutoSubError):
    """Error saat proses pembuatan file .srt."""

    def __init__(self, message: str = "Gagal membuat file subtitle (.srt).") -> None:
        super().__init__(message)


# === Validation & Security Errors ===


class ValidationError(AutoSubError):
    """Error validasi input pengguna."""

    def __init__(self, message: str = "Input tidak valid.") -> None:
        super().__init__(message)


class SecurityError(AutoSubError):
    """Error terkait keamanan (path traversal, injection, dll)."""

    def __init__(self, message: str = "Operasi ditolak karena alasan keamanan.") -> None:
        super().__init__(message)
