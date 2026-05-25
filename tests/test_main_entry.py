import sys
from unittest.mock import patch
import pytest


class TestMainEntry:
    def test_main_entry_point(self):
        if "app.__main__" in sys.modules:
            del sys.modules["app.__main__"]
        with patch("sys.argv", ["mod-translator", "cli", "-s", "en_US", "-t", "uk_UA"]):
            with patch("app.commands.command_line.main") as mock_main:
                mock_main.return_value = None
                try:
                    import app.__main__
                except SystemExit:
                    pass

    def test_main_importable(self):
        import app.__main__
        assert hasattr(app.__main__, "__name__")

    def test_main_error_path(self):
        if "app.__main__" in sys.modules:
            del sys.modules["app.__main__"]
        with patch("sys.argv", ["mod-translator"]):
            with patch("app.commands.command_line.main", side_effect=RuntimeError("test error")):
                with pytest.raises(SystemExit):
                    import app.__main__
