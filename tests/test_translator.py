from unittest.mock import MagicMock, patch

from app.core.translator import Translator


class TestTranslator:
    def test_init_google(self):
        translator = Translator("en", "uk", capitalize=True, provider="google")
        assert translator.source_language == "en"
        assert translator.target_language == "uk"
        assert translator.capitalize is True
        assert translator.provider == "google"

    def test_translate_skip_empty_string(self):
        translator = Translator("en", "uk", provider="google")
        result = translator.translate("")
        assert result == ""

    def test_translate_skip_non_string(self):
        translator = Translator("en", "uk", provider="google")
        result = translator.translate(None)
        assert result is None

    def test_translate_with_google(self):
        translator = Translator("en", "uk", capitalize=False, provider="google")
        with patch.object(translator._service, "translate", return_value="привіт"):
            result = translator.translate("Hello")
            assert result == "привіт"

    def test_translate_with_google_capitalize(self):
        translator = Translator("en", "uk", capitalize=True, provider="google")
        with patch.object(translator._service, "translate", return_value="Привіт"):
            result = translator.translate("Hello")
            assert result == "Привіт"

    def test_translate_with_google_import_error(self):
        translator = Translator("en", "uk", provider="google")
        with patch.object(translator._service, "translate", return_value="Hello"):
            result = translator.translate("Hello")
            assert result == "Hello"

    def test_translate_data_google_batch(self, sample_en_us_json):
        translator = Translator("en", "uk", capitalize=False, provider="google")
        with patch.object(translator._service, "batch_translate", return_value={k: "translated" for k in sample_en_us_json}):
            result = translator.translate_data(sample_en_us_json)
            for value in result.values():
                assert value == "translated"

    def test_translate_data_openai_batch(self, sample_en_us_json):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("app.services.factory.OpenAIService") as MockService:
                mock_svc = MagicMock()
                mock_svc.batch_translate.return_value = {k: f"ai_{k}" for k in sample_en_us_json}
                MockService.return_value = mock_svc
                translator = Translator("en", "uk", provider="openai")
                result = translator.translate_data(sample_en_us_json)
                for value in result.values():
                    assert value.startswith("ai_")

    def test_translate_with_openai_error_returns_original(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("app.services.factory.OpenAIService") as MockService:
                mock_svc = MagicMock()
                mock_svc.translate.side_effect = lambda t: t  # return same text on error
                MockService.return_value = mock_svc
                translator = Translator("en", "uk", provider="openai")
                result = translator.translate("Hello")
                assert result == "Hello"
