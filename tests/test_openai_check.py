import os
import builtins
from unittest.mock import patch

from app.core.openai_check import check_openai_available


class TestOpenaiCheck:
    def test_available_with_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            available, msg = check_openai_available()
            assert available is True
            assert "API key configured" in msg or "Available" in msg

    def test_unavailable_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            available, msg = check_openai_available()
            assert available is False
            assert "API key not found" in msg or "API key" in msg.lower()

    def test_openai_not_installed(self):
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "openai":
                raise ImportError("No module named 'openai'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            available, msg = check_openai_available()
            assert available is False
            assert "not installed" in msg or "Package" in msg
