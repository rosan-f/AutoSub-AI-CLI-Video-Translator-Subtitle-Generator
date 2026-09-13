"""Tests for the Validators module."""

from __future__ import annotations

import pytest

from autosub_ai.exceptions import InvalidURLError, ValidationError
from autosub_ai.utils.validators import validate_file_path, validate_model_size, validate_url


# ================================================================
# URL Validation
# ================================================================


class TestValidateURL:
    """Tests for validate_url()."""

    def test_valid_youtube_url(self, valid_youtube_url: str) -> None:
        """Standard YouTube URL must be accepted."""
        result = validate_url(valid_youtube_url)
        assert result == valid_youtube_url

    def test_valid_youtu_be_short_url(self) -> None:
        """youtu.be shortlinks must be accepted."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = validate_url(url)
        assert result == url

    def test_empty_url_raises(self) -> None:
        """Empty string must raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_url("")

    def test_none_url_raises(self) -> None:
        """None must raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_url(None)  # type: ignore[arg-type]

    def test_invalid_domain_raises(self) -> None:
        """Non-whitelisted domains must be rejected."""
        with pytest.raises(InvalidURLError, match="not supported"):
            validate_url("https://evil-site.com/video.mp4")

    def test_ftp_scheme_raises(self) -> None:
        """FTP scheme must be rejected."""
        with pytest.raises(InvalidURLError):
            validate_url("ftp://youtube.com/video")

    def test_url_with_credentials_raises(self) -> None:
        """URLs containing embedded credentials must be rejected."""
        with pytest.raises(InvalidURLError, match="credentials"):
            validate_url("https://user:pass@youtube.com/watch?v=abc")

    def test_url_too_long_raises(self) -> None:
        """URLs exceeding the max length must be rejected."""
        long_url = "https://www.youtube.com/watch?v=" + "a" * 3000
        with pytest.raises(InvalidURLError, match="maximum length"):
            validate_url(long_url)


# ================================================================
# Model Validation
# ================================================================


class TestValidateModelSize:
    """Tests for validate_model_size()."""

    @pytest.mark.parametrize("model", ["tiny", "base", "small", "medium", "large"])
    def test_valid_models(self, model: str) -> None:
        """All recognized model names must be accepted."""
        assert validate_model_size(model) == model

    def test_case_insensitive(self) -> None:
        """Model names must be case-insensitive."""
        assert validate_model_size("BASE") == "base"
        assert validate_model_size("Large") == "large"

    def test_invalid_model_raises(self) -> None:
        """Unrecognized model names must raise ValidationError."""
        with pytest.raises(ValidationError, match="not valid"):
            validate_model_size("xlarge")

    def test_empty_model_raises(self) -> None:
        """Empty model name must raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_model_size("")


# ================================================================
# File Path Validation
# ================================================================


class TestValidateFilePath:
    """Tests for validate_file_path()."""

    def test_valid_file(self, sample_audio_path) -> None:
        """An existing file must be accepted."""
        result = validate_file_path(sample_audio_path)
        assert result.exists()

    def test_path_traversal_raises(self) -> None:
        """Paths containing '..' must be rejected."""
        with pytest.raises(ValidationError, match="\\.\\."):
            validate_file_path("../../etc/passwd")

    def test_nonexistent_file_raises(self, tmp_path) -> None:
        """Non-existent files must raise ValidationError."""
        with pytest.raises(ValidationError, match="not found"):
            validate_file_path(tmp_path / "nonexistent.wav")

    def test_directory_raises(self, tmp_path) -> None:
        """Directories must be rejected (not a file)."""
        with pytest.raises(ValidationError, match="directory"):
            validate_file_path(tmp_path)
