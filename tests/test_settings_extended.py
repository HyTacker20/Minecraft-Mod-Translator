import os
from unittest.mock import patch

from app.core.settings import Settings


class TestSettingsExtended:
    def test_no_cli_args_defaults(self):
        settings = Settings()
        assert settings.max_workers == 4
        assert settings.dry_run is False
        assert settings.source_mc_lang == "en_US"
        assert settings.target_mc_lang == "es_ES"
        assert settings.provider == "google"

    def test_replace_appdata(self):
        settings = Settings()
        with patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            result = settings._replace_appdata("%APPDATA%/mods")
            assert "Test" in result
            assert "mods" in result
            assert "%APPDATA%" not in result.lower()
