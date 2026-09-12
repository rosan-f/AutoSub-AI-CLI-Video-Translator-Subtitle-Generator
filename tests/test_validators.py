"""Tests untuk Validators Module."""

from __future__ import annotations

import pytest

from autosub_ai.exceptions import InvalidURLError, ValidationError
from autosub_ai.utils.validators import validate_file_path, validate_model_size, validate_url


class TestValidateURL:
    """Tests untuk validate_url()."""

    def test_valid_youtube_url(self, valid_youtube_url: str) -> None:
        """URL YouTube yang valid harus diterima."""
        result = validate_url(valid_youtube_url)
        assert result == valid_youtube_url

    def test_valid_youtu_be_short_url(self) -> None:
        """URL youtu.be shortlink harus diterima."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = validate_url(url)
        assert result == url

    def test_empty_url_raises(self) -> None:
        """URL kosong harus raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_url("")

    def test_none_url_raises(self) -> None:
        """URL None harus raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_url(None)  # type: ignore[arg-type]

    def test_invalid_domain_raises(self) -> None:
        """Domain yang tidak ada di whitelist harus ditolak."""
        with pytest.raises(InvalidURLError, match="tidak didukung"):
            validate_url("https://evil-site.com/video.mp4")

    def test_ftp_scheme_raises(self) -> None:
        """Scheme FTP harus ditolak."""
        with pytest.raises(InvalidURLError):
            validate_url("ftp://youtube.com/video")

    def test_url_with_credentials_raises(self) -> None:
        """URL dengan credentials harus ditolak."""
        with pytest.raises(InvalidURLError, match="credentials"):
            validate_url("https://user:pass@youtube.com/watch?v=abc")

    def test_url_too_long_raises(self) -> None:
        """URL yang terlalu panjang harus ditolak."""
        long_url = "https://www.youtube.com/watch?v=" + "a" * 3000
        with pytest.raises(InvalidURLError, match="terlalu panjang"):
            validate_url(long_url)


class TestValidateModelSize:
    """Tests untuk validate_model_size()."""

    @pytest.mark.parametrize("model", ["tiny", "base", "small", "medium", "large"])
    def test_valid_models(self, model: str) -> None:
        """Model yang valid harus diterima."""
        assert validate_model_size(model) == model

    def test_case_insensitive(self) -> None:
        """Model harus case-insensitive."""
        assert validate_model_size("BASE") == "base"
        assert validate_model_size("Large") == "large"

    def test_invalid_model_raises(self) -> None:
        """Model yang tidak valid harus raise ValidationError."""
        with pytest.raises(ValidationError, match="tidak valid"):
            validate_model_size("xlarge")

    def test_empty_model_raises(self) -> None:
        """Model kosong harus raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_model_size("")


class TestValidateFilePath:
    """Tests untuk validate_file_path()."""

    def test_valid_file(self, sample_audio_path) -> None:
        """File yang ada harus diterima."""
        result = validate_file_path(sample_audio_path)
        assert result.exists()

    def test_path_traversal_raises(self) -> None:
        """Path dengan '..' harus ditolak."""
        with pytest.raises(ValidationError, match="\\.\\."):
            validate_file_path("../../etc/passwd")

    def test_nonexistent_file_raises(self, tmp_path) -> None:
        """File yang tidak ada harus raise ValidationError."""
        with pytest.raises(ValidationError, match="tidak ditemukan"):
            validate_file_path(tmp_path / "nonexistent.wav")

    def test_directory_raises(self, tmp_path) -> None:
        """Direktori harus ditolak (bukan file)."""
        with pytest.raises(ValidationError, match="direktori"):
            validate_file_path(tmp_path)
