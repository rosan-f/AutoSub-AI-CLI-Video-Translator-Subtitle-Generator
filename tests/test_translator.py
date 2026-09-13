"""Tests for the Translator module."""

from __future__ import annotations

import pytest

from autosub_ai.core.translator import TextTranslator
from autosub_ai.exceptions import TranslationError


class TestTextTranslator:
    """Tests for TextTranslator."""

    def test_init_valid_language(self) -> None:
        """Translator must accept supported languages."""
        translator = TextTranslator(target_language="id")
        assert translator.target_language == "id"

    def test_init_invalid_language_raises(self) -> None:
        """Translator must reject unsupported languages."""
        with pytest.raises(TranslationError, match="not supported"):
            TextTranslator(target_language="xx")

    @pytest.mark.parametrize("lang", ["id", "en", "ja", "ko", "zh"])
    def test_supported_languages(self, lang: str) -> None:
        """All listed languages must be accepted."""
        translator = TextTranslator(target_language=lang)
        assert translator.target_language == lang
