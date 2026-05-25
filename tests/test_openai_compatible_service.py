import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.openai_compatible_service import OpenAICompatibleService


def _mock_translate_fn(text: str) -> str:
    if text == "fail":
        raise RuntimeError("API error")
    return f"ai_{text}"


class TestOpenAICompatibleService:
    def test_init_with_valid_env(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk")
                assert service._client is mock_client

    def test_init_no_base_url(self):
        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
        }, clear=True):
            with patch("dotenv.load_dotenv", create=True):
                with pytest.raises(ValueError):
                    OpenAICompatibleService("en", "uk")

    def test_init_no_api_key(self):
        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch("dotenv.load_dotenv", create=True):
                with pytest.raises(ValueError):
                    OpenAICompatibleService("en", "uk")

    def test_init_fallback_to_openai_api_key(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-fallback",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk")
                assert service._client is mock_client

    def test_batch_translate_parallel(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk")
                data = {f"key_{i}": f"text_{i}" for i in range(6)}
                with patch.object(service, "translate", side_effect=_mock_translate_fn):
                    result = service.batch_translate(data, total_items=6, max_workers=3)
                    assert len(result) == 6
                    for i in range(6):
                        assert result[f"key_{i}"] == f"ai_text_{i}"

    def test_translate_whitespace_only(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk", capitalize=False)
                result = service.translate("   ")
                assert result == "   "

    def test_translate_error_fallback(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk", capitalize=False)
                result = service.translate("Hello")
                assert result == "Hello"

    def test_batch_translate_empty_data(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk")
                result = service.batch_translate({}, max_workers=4)
                assert result == {}

    def test_batch_translate_sequential(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk")
                data = {"a": "hello", "b": "world"}
                with patch.object(service, "translate", side_effect=_mock_translate_fn):
                    result = service.batch_translate(data, total_items=2, max_workers=1)
                    assert result["a"] == "ai_hello"
                    assert result["b"] == "ai_world"

    def test_translate_with_capitalize(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "hola"
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "es", capitalize=True)
                result = service.translate("Hello")
                assert result == "Hola"

    def test_batch_translate_with_errors(self):
        mock_openai_mod = MagicMock()
        mock_client = MagicMock()
        mock_openai_mod.OpenAI = MagicMock(return_value=mock_client)

        with patch.dict(os.environ, {
            "OPENAICOMPATIBLE_API_KEY": "sk-test",
            "OPENAICOMPATIBLE_BASE_URL": "http://localhost:8080/v1",
        }, clear=True):
            with patch.dict("sys.modules", {"openai": mock_openai_mod}):
                service = OpenAICompatibleService("en", "uk")
                data = {"a": "ok1", "b": "fail", "c": "ok2"}
                with patch.object(service, "translate", side_effect=_mock_translate_fn):
                    result = service.batch_translate(data, total_items=3, max_workers=3)
                    assert result["a"] == "ai_ok1"
                    assert result["b"] == "fail"
                    assert result["c"] == "ai_ok2"
