"""
AutoSub-AI — Exception Hierarchy

All exceptions are organized in a clear hierarchy to ensure:
- Consistent error handling across the codebase
- Safe error messages (no internal stack traces exposed to users)
- Granular catch capability at any level
"""


class AutoSubError(Exception):
    """Base exception for all AutoSub-AI errors."""

    def __init__(self, message: str = "An internal error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


# ================================================================
# Download Errors
# ================================================================


class DownloadError(AutoSubError):
    """Raised when audio download from a video source fails."""

    def __init__(self, message: str = "Failed to download audio from video.") -> None:
        super().__init__(message)


class InvalidURLError(DownloadError):
    """Raised when the provided URL is invalid or unsupported."""

    def __init__(self, url: str = "") -> None:
        sanitized = url[:200] if url else "unknown"
        super().__init__(f"Invalid or unsupported URL: {sanitized}")


# ================================================================
# Transcription Errors
# ================================================================


class TranscriptionError(AutoSubError):
    """Raised when audio transcription fails."""

    def __init__(self, message: str = "Failed to transcribe audio.") -> None:
        super().__init__(message)


class ModelLoadError(TranscriptionError):
    """Raised when a Whisper model fails to load."""

    def __init__(self, model_name: str = "") -> None:
        super().__init__(f"Failed to load Whisper model: '{model_name}'")


# ================================================================
# Translation Errors
# ================================================================


class TranslationError(AutoSubError):
    """Raised when text translation fails."""

    def __init__(self, message: str = "Failed to translate text.") -> None:
        super().__init__(message)


# ================================================================
# Formatter Errors
# ================================================================


class FormatterError(AutoSubError):
    """Raised when .srt file generation fails."""

    def __init__(self, message: str = "Failed to generate subtitle file (.srt).") -> None:
        super().__init__(message)


# ================================================================
# Validation & Security Errors
# ================================================================


class ValidationError(AutoSubError):
    """Raised when user input fails validation."""

    def __init__(self, message: str = "Invalid input.") -> None:
        super().__init__(message)


class SecurityError(AutoSubError):
    """Raised when a security violation is detected (path traversal, injection, etc.)."""

    def __init__(self, message: str = "Operation denied for security reasons.") -> None:
        super().__init__(message)
