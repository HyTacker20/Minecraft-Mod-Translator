import argparse

import pytest

from app.commands.translate import add_translate_arguments
from app.core.settings import Settings
from app.parsers.json_parser import parse_json_with_comments, remove_comments_from_json


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.source_mc_lang == "en_US"
        assert settings.target_mc_lang == "es_ES"
        assert settings.mods_path == "./"
        assert settings.temp_path == "temp"
        assert settings.translation_path == "./translated"
        assert settings.provider == "google"

    def test_cli_args_override(self):
        args = argparse.Namespace(
            source="uk_UA",
            target="de_DE",
            path="./my_mods",
            output="./my_output",
            provider="openai",
        )
        settings = Settings(cli_args=args)
        assert settings.source_mc_lang == "uk_UA"
        assert settings.target_mc_lang == "de_DE"
        assert settings.mods_path == "./my_mods"
        assert settings.translation_path == "./my_output"
        assert settings.provider == "openai"

    def test_cli_args_ai_deprecated_flag(self):
        args = argparse.Namespace(
            source="uk_UA",
            target="de_DE",
            path="./my_mods",
            output="./my_output",
            ai=True,
        )
        settings = Settings(cli_args=args)
        assert settings.provider == "openai"

    def test_google_lang_extraction(self):
        settings = Settings()
        assert settings.source_google_lang == "en"
        assert settings.target_google_lang == "es"

    def test_format_lang(self):
        settings = Settings()
        result = settings._format_lang("UK_ua")
        assert result == "uk_UA"

    def test_add_translate_arguments(self):
        parser = argparse.ArgumentParser()
        add_translate_arguments(parser)
        args = parser.parse_args(["-p", "./mods", "-s", "en_US", "-t", "uk_UA", "--provider", "openai"])
        assert args.path == "./mods"
        assert args.source == "en_US"
        assert args.target == "uk_UA"
        assert args.provider == "openai"

    def test_add_translate_arguments_deprecated_ai_flag(self):
        parser = argparse.ArgumentParser()
        add_translate_arguments(parser)
        args = parser.parse_args(["-p", "./mods", "-s", "en_US", "-t", "uk_UA", "--ai"])
        assert args.ai is True


class TestJsonParsing:
    def test_remove_comments_single_line(self):
        content = '{"key": "value"} // comment'
        result = remove_comments_from_json(content)
        assert "comment" not in result

    def test_remove_comments_multi_line(self):
        content = '{"key": /* block comment */ "value"}'
        result = remove_comments_from_json(content)
        assert "block comment" not in result

    def test_parse_json_with_comments(self, tmp_path, sample_json_with_comments):
        path = tmp_path / "test.json"
        path.write_text(sample_json_with_comments, encoding="utf-8")
        result = parse_json_with_comments(str(path))
        assert result["item.minecraft.diamond"] == "Diamond"
        assert result["item.minecraft.gold_ingot"] == "Gold Ingot"

    def test_parse_json_missing_file(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        from app.exceptions import FileParsingError
        with pytest.raises(FileParsingError):
            parse_json_with_comments(str(path))
