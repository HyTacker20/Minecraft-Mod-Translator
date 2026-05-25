from unittest.mock import MagicMock, patch

from app.core.translator import Translator


class TestTranslator:
    def test_init_google(self):
        translator = Translator("en", "uk", capitalize=True, use_openai=False)
        assert translator.source_language == "en"
        assert translator.target_language == "uk"
        assert translator.capitalize is True
        assert translator.use_openai is False

    def test_translate_skip_empty_string(self):
        translator = Translator("en", "uk", use_openai=False)
        result = translator.translate("")
        assert result == ""

    def test_translate_skip_non_string(self):
        translator = Translator("en", "uk", use_openai=False)
        result = translator.translate(None)
        assert result is None

    def test_translate_with_google(self):
        translator = Translator("en", "uk", capitalize=False, use_openai=False)
        with patch("deep_translator.GoogleTranslator") as mock_gt:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = "привіт"
            mock_gt.return_value = mock_instance

            result = translator.translate("Hello")
            assert result == "привіт"

    def test_translate_with_google_capitalize(self):
        translator = Translator("en", "uk", capitalize=True, use_openai=False)
        with patch("deep_translator.GoogleTranslator") as mock_gt:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = "привіт"
            mock_gt.return_value = mock_instance

            result = translator.translate("Hello")
            assert result == "Привіт"

    def test_translate_with_google_import_error(self):
        translator = Translator("en", "uk", use_openai=False)
        with patch("deep_translator.GoogleTranslator", side_effect=ImportError("no module")):
            result = translator.translate("Hello")
            assert result == "Hello"

    def test_translate_data_google_batch(self, sample_en_us_json):
        translator = Translator("en", "uk", capitalize=False, use_openai=False)
        with patch("deep_translator.GoogleTranslator") as mock_gt:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = "translated"
            mock_gt.return_value = mock_instance
            result = translator.translate_data(sample_en_us_json)
            for value in result.values():
                assert value == "translated"

    def test_translate_data_openai_batch(self, sample_en_us_json):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            translator = Translator("en", "uk", use_openai=True)
            with patch.object(translator, "translate", side_effect=lambda t: f"ai_{t}"):
                result = translator.translate_data(sample_en_us_json)
                for value in result.values():
                    assert value.startswith("ai_")

    def test_translate_with_openai_error_returns_original(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            translator = Translator("en", "uk", use_openai=True)
            with patch.object(translator.openai_client.chat.completions, "create", side_effect=Exception("API error")):
                result = translator.translate("Hello")
                assert result == "Hello"
