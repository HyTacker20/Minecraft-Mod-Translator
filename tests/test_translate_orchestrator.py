import os
import argparse
import builtins
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

from app.commands.translate import (
    add_translate_arguments,
    _check_dependencies,
    handle_translate_command,
)


class TestCheckDependencies:
    def test_check_dependencies_google_available(self):
        assert _check_dependencies(use_ai=False) is True

    def test_check_dependencies_google_missing(self):
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "deep_translator":
                raise ImportError("No module named 'deep_translator'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = _check_dependencies(use_ai=False)
            assert result is False

    def test_check_dependencies_openai_available(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            result = _check_dependencies(use_ai=True)
            assert result is True

    def test_check_dependencies_openai_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            result = _check_dependencies(use_ai=True)
            assert result is False

    def test_check_dependencies_openai_not_installed(self):
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "openai":
                raise ImportError("No module named 'openai'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            result = _check_dependencies(use_ai=True)
            assert result is False


class TestTranslateOrchestrator:
    def test_handle_translate_dry_run(self, tmp_path: Path):
        mods_dir = tmp_path / "mods"
        mods_dir.mkdir()
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        args = argparse.Namespace(
            path=str(mods_dir),
            source="en_US",
            target="uk_UA",
            output=str(out_dir),
            ai=False,
            workers=4,
            dry_run=True,
        )
        with patch("app.commands.translate._check_dependencies", return_value=True):
            with patch("app.commands.translate.logger") as mock_logger:
                handle_translate_command(args)
                dry_run_messages = [
                    call_args[0][0]
                    for call_args in mock_logger.info.call_args_list
                    if call_args[0] and "DRY RUN" in str(call_args[0][0])
                ]
                assert len(dry_run_messages) >= 1

    def test_handle_translate_missing_deps(self):
        args = argparse.Namespace(
            path="./mods", source="en_US", target="uk_UA",
            output="./out", ai=True, workers=4, dry_run=False,
        )
        with patch("app.commands.translate._check_dependencies", return_value=False):
            result = handle_translate_command(args)
            assert result is None

    def test_handle_translate_with_workers_arg(self, tmp_path: Path):
        mods_dir = tmp_path / "mods"
        mods_dir.mkdir()
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        args = argparse.Namespace(
            path=str(mods_dir), source="en_US", target="uk_UA",
            output=str(out_dir), ai=False, workers=8, dry_run=True,
        )
        with patch("app.commands.translate._check_dependencies", return_value=True):
            with patch("app.commands.translate.Settings") as MockSettings:
                mock_instance = MagicMock()
                mock_instance.temp_path = str(tmp_path / "temp")
                mock_instance.mods_path = str(mods_dir)
                mock_instance.translation_path = str(out_dir)
                mock_instance.source_mc_lang = "en_US"
                mock_instance.target_mc_lang = "uk_UA"
                mock_instance.use_ai = False
                mock_instance.max_workers = 8
                mock_instance.dry_run = True
                MockSettings.return_value = mock_instance
                with patch("app.commands.translate.FileManager") as MockFM:
                    mock_fm = MagicMock()
                    mock_fm.get_lang_folders.return_value = []
                    MockFM.return_value = mock_fm
                    handle_translate_command(args)
                    MockSettings.assert_called_once()
                    call_kwargs = MockSettings.call_args[1]
                    assert call_kwargs["cli_args"].workers == 8

    def test_add_translate_arguments_all_flags(self):
        parser = argparse.ArgumentParser()
        add_translate_arguments(parser)
        args = parser.parse_args([
            "-p", "./mods", "-s", "en_US", "-t", "uk_UA",
            "-o", "./out", "--ai", "--workers", "6", "--dry-run",
        ])
        assert args.path == "./mods"
        assert args.source == "en_US"
        assert args.target == "uk_UA"
        assert args.output == "./out"
        assert args.ai is True
        assert args.workers == 6
        assert args.dry_run is True

    def test_add_translate_arguments_defaults(self):
        parser = argparse.ArgumentParser()
        add_translate_arguments(parser)
        args = parser.parse_args([])
        assert args.path == "./mods"
        assert args.source is None
        assert args.target is None
        assert args.output is None
        assert args.ai is False
        assert args.workers == 4
        assert args.dry_run is False

    def test_handle_translate_normal_flow(self, tmp_path: Path):
        mods_dir = tmp_path / "mods"
        mods_dir.mkdir()
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        args = argparse.Namespace(
            path=str(mods_dir), source="en_US", target="uk_UA",
            output=str(out_dir), ai=False, workers=4, dry_run=False,
        )
        with patch("app.commands.translate._check_dependencies", return_value=True):
            with patch("app.commands.translate.FileManager") as MockFM:
                mock_fm = MagicMock()
                mock_fm.get_lang_folders.return_value = []
                MockFM.return_value = mock_fm
                handle_translate_command(args)
                mock_fm.create_needed_folders.assert_called_once()
                mock_fm.unpack_mods.assert_called_once()
                mock_fm.edit_lang_files.assert_called_once()
                mock_fm.convert_translated_mods.assert_called_once()
                mock_fm.remove_folder.assert_called_once()

    def test_handle_translate_same_paths_verifies_jars(self, tmp_path: Path):
        shared_dir = tmp_path / "shared"
        shared_dir.mkdir()
        args = argparse.Namespace(
            path=str(shared_dir), source="en_US", target="uk_UA",
            output=str(shared_dir), ai=False, workers=4, dry_run=False,
        )
        with patch("app.commands.translate._check_dependencies", return_value=True):
            with patch("app.commands.translate.FileManager") as MockFM:
                mock_fm = MagicMock()
                mock_fm.get_lang_folders.return_value = []
                MockFM.return_value = mock_fm
                handle_translate_command(args)
                mock_fm.convert_translated_mods.assert_called_once()

    def test_handle_translate_exception_logged(self, tmp_path: Path):
        mods_dir = tmp_path / "mods"
        mods_dir.mkdir()
        args = argparse.Namespace(
            path=str(mods_dir), source="en_US", target="uk_UA",
            output=str(tmp_path / "out"), ai=False, workers=4, dry_run=False,
        )
        with patch("app.commands.translate._check_dependencies", return_value=True):
            with patch("app.commands.translate.FileManager") as MockFM:
                MockFM.side_effect = RuntimeError("Something broke")
                with patch("app.commands.translate.logger") as mock_logger:
                    handle_translate_command(args)
                    exception_calls = [
                        c for c in mock_logger.exception.call_args_list
                        if "Error translating mods" in str(c[0])
                    ]
                    assert len(exception_calls) >= 1
