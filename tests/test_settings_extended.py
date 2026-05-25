from app.core.settings import Settings


class TestSettingsExtended:
    def test_no_cli_args_defaults(self):
        settings = Settings()
        assert settings.max_workers == 4
        assert settings.dry_run is False
        assert settings.source_mc_lang == "en_US"
        assert settings.target_mc_lang == "es_ES"
        assert settings.provider == "google"
