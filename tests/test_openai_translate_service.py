import os
import builtins
from unittest.mock import MagicMock, patch, PropertyMock

from app.services.openai_translate import (
    setup_openai_client,
    openai_translate,
    batch_translate_openai,
)


def _mock_translate_fn(text: str) -> str:
    if text == "fail":
        raise RuntimeError("API error")
    return f"ai_{text}"


class TestOpenaiTranslateService:
    def test_setup_openai_client_with_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}, clear=True):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client
                client, model = setup_openai_client()
                assert client is mock_client
                assert model == "gpt-3.5-turbo"

    def test_setup_openai_client_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            import pytest
            with pytest.raises(ValueError):
                setup_openai_client()

    def test_setup_openai_not_installed(self):
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "openai":
                raise ImportError("No module named 'openai'")
            return original_import(name, *args, **kwargs)

        import pytest
        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError):
                setup_openai_client()

    def test_batch_translate_openai_parallel(self):
        data = {f"key_{i}": f"text_{i}" for i in range(6)}
        result = batch_translate_openai(data, _mock_translate_fn, total_items=6, max_workers=3)
        assert len(result) == 6
        for i in range(6):
            assert result[f"key_{i}"] == f"ai_text_{i}"

    def test_openai_translate_whitespace_only(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            mock_client = MagicMock()
            result = openai_translate(
                "   ", "en", "uk", False,
                mock_client, "gpt-3.5-turbo",
                lambda f: f,
            )
            assert result == "   "
            mock_client.chat.completions.create.assert_not_called()

    def test_openai_translate_error_fallback(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API error")
            result = openai_translate(
                "Hello", "en", "uk", False,
                mock_client, "gpt-3.5-turbo",
                lambda f: f,
            )
            assert result == "Hello"

    def test_batch_translate_openai_empty_data(self):
        result = batch_translate_openai({}, _mock_translate_fn, max_workers=4)
        assert result == {}

    def test_batch_translate_openai_sequential(self):
        data = {"a": "hello", "b": "world"}
        result = batch_translate_openai(data, _mock_translate_fn, total_items=2, max_workers=1)
        assert result["a"] == "ai_hello"
        assert result["b"] == "ai_world"

    def test_openai_translate_with_capitalize(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            mock_client = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = "hola"
            mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

            def fake_decorator(f):
                return f
            result = openai_translate(
                "Hello", "en", "es", True,
                mock_client, "gpt-3.5-turbo",
                fake_decorator,
            )
            assert result == "Hola"

    def test_batch_translate_openai_with_errors(self):
        data = {"a": "ok1", "b": "fail", "c": "ok2"}
        result = batch_translate_openai(data, _mock_translate_fn, total_items=3, max_workers=3)
        assert result["a"] == "ai_ok1"
        assert result["b"] == "fail"
        assert result["c"] == "ai_ok2"
