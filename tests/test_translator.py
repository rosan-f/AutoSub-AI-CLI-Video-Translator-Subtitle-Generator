"""Tests untuk Translator Module."""

from __future__ import annotations

import pytest

from autosub_ai.core.translator import TextTranslator
from autosub_ai.exceptions import TranslationError


class TestTextTranslator:
    """Tests untuk TextTranslator."""

    def test_init_valid_language(self) -> None:
        """Translator harus menerima bahasa yang didukung."""
        translator = TextTranslator(target_language="id")
        assert translator.target_language == "id"

    def test_init_invalid_language_raises(self) -> None:
        """Translator harus menolak bahasa yang tidak didukung."""
        with pytest.raises(TranslationError, match="tidak didukung"):
            TextTranslator(target_language="xx")

    @pytest.mark.parametrize("lang", ["id", "en", "ja", "ko", "zh"])
    def test_supported_languages(self, lang: str) -> None:
        """Semua bahasa yang didukung harus diterima."""
        translator = TextTranslator(target_language=lang)
        assert translator.target_language == lang
