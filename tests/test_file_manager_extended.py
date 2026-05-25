import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.file_manager import FileManager
from app.core.settings import Settings


class TestFileManagerExtended:
    def test_move_translated_mod_files(self, tmp_path: Path):
        settings = Settings()
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        mods_dir.mkdir()
        translation_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(tmp_path / "temp")

        jar_path = translation_dir / "test_mod.jar"
        jar_path.write_text("fake jar content", encoding="utf-8")

        fm = FileManager(settings)
        fm.move_translated_mod_files()
        assert (mods_dir / "test_mod.jar").exists()

    def test_copy_translated_files_to_same_path(self, tmp_path: Path):
        settings = Settings()
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        mods_dir.mkdir()
        translation_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(tmp_path / "temp")

        jar_path = translation_dir / "test_mod.jar"
        jar_path.write_text("fake jar content", encoding="utf-8")

        fm = FileManager(settings)
        fm.copy_translated_files_to_same_path()
        assert (mods_dir / "test_mod.jar").exists()

    def test_remove_original_mod_files(self, tmp_path: Path):
        settings = Settings()
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        mods_dir.mkdir()
        translation_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(tmp_path / "temp")

        (mods_dir / "keep.jar").write_text("keep", encoding="utf-8")
        (translation_dir / "remove_me.jar").write_text("translated", encoding="utf-8")

        fm = FileManager(settings)
        fm.remove_original_mod_files()

        translated_jars = [f for f in os.listdir(str(translation_dir)) if f.endswith(".jar")]
        assert len(translated_jars) == 1

    def test_remove_folder(self, tmp_path: Path):
        settings = Settings()
        settings.temp_path = str(tmp_path / "temp")
        folder = tmp_path / "to_remove"
        folder.mkdir()
        (folder / "file.txt").write_text("test", encoding="utf-8")

        fm = FileManager(settings)
        fm.remove_folder(str(folder))
        assert not folder.exists()

    def test_convert_translated_mods_multiple(self, tmp_path: Path, sample_en_us_json: dict):
        settings = Settings()
        settings.source_mc_lang = "en_US"
        settings.target_mc_lang = "uk_UA"
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        temp_dir = tmp_path / "temp"
        mods_dir.mkdir()
        translation_dir.mkdir()
        temp_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(temp_dir)

        for i in range(3):
            mod_folder = temp_dir / f"mod_{i}"
            assets = mod_folder / "assets" / "mod" / "lang"
            assets.mkdir(parents=True)
            en_path = assets / "en_us.json"
            en_path.write_text(json.dumps(sample_en_us_json), encoding="utf-8")
            uk_path = assets / "uk_ua.json"
            uk_path.write_text(json.dumps(sample_en_us_json), encoding="utf-8")

        settings.use_ai = False
        fm = FileManager(settings)
        fm.convert_translated_mods()

        all_files = [f for f in os.listdir(str(translation_dir)) if os.path.isfile(os.path.join(str(translation_dir), f))]
        assert len(all_files) == 3

    def test_remove_original_mod_files_no_translated(self, tmp_path: Path):
        settings = Settings()
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        mods_dir.mkdir()
        translation_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(tmp_path / "temp")

        (mods_dir / "some.jar").write_text("original", encoding="utf-8")

        fm = FileManager(settings)
        fm.remove_original_mod_files()
        assert (mods_dir / "some.jar").exists()

    def test_get_mcfunction_folders(self, tmp_path: Path):
        settings = Settings()
        settings.temp_path = str(tmp_path)
        mc_dir = tmp_path / "mod.jar" / "data" / "test" / "functions"
        mc_dir.mkdir(parents=True)
        (mc_dir / "tick.mcfunction").write_text('say hello', encoding="utf-8")
        fm = FileManager(settings)
        folders = fm.get_mcfunction_folders()
        assert len(folders) >= 1

    def test_move_translated_mod_files_directory(self, tmp_path: Path):
        settings = Settings()
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        mods_dir.mkdir()
        translation_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(tmp_path / "temp")

        sub_dir = translation_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file.txt").write_text("content", encoding="utf-8")

        fm = FileManager(settings)
        fm.move_translated_mod_files()
        assert (mods_dir / "subdir").exists()
        assert (mods_dir / "subdir" / "file.txt").exists()

    def test_copy_translated_files_to_same_path_directory(self, tmp_path: Path):
        settings = Settings()
        mods_dir = tmp_path / "mods"
        translation_dir = tmp_path / "translated"
        mods_dir.mkdir()
        translation_dir.mkdir()
        settings.mods_path = str(mods_dir)
        settings.translation_path = str(translation_dir)
        settings.temp_path = str(tmp_path / "temp")

        sub_dir = translation_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file.txt").write_text("content", encoding="utf-8")

        fm = FileManager(settings)
        fm.copy_translated_files_to_same_path()
        assert (mods_dir / "subdir").exists()
        assert (mods_dir / "subdir" / "file.txt").exists()

    def test_convert_translated_mods_same_paths(self, tmp_path: Path, sample_en_us_json: dict):
        settings = Settings()
        settings.source_mc_lang = "en_US"
        settings.target_mc_lang = "uk_UA"
        shared_dir = tmp_path / "shared"
        temp_dir = tmp_path / "temp"
        shared_dir.mkdir()
        temp_dir.mkdir()
        settings.mods_path = str(shared_dir)
        settings.translation_path = str(shared_dir)
        settings.temp_path = str(temp_dir)

        mod_folder = temp_dir / "mod_0"
        assets = mod_folder / "assets" / "mod" / "lang"
        assets.mkdir(parents=True)
        (assets / "en_us.json").write_text(json.dumps(sample_en_us_json), encoding="utf-8")
        (assets / "uk_ua.json").write_text(json.dumps(sample_en_us_json), encoding="utf-8")

        settings.use_ai = False
        fm = FileManager(settings)
        fm.convert_translated_mods()
        output = shared_dir / "mod_0"
        assert output.exists()

    def test_file_manager_openai_fallback(self, tmp_path: Path):
        settings = Settings()
        settings.use_ai = True
        settings.temp_path = str(tmp_path / "temp")
        settings.translation_path = str(tmp_path / "translated")
        settings.mods_path = str(tmp_path / "mods")
        settings.source_google_lang = "en"
        settings.target_google_lang = "uk"

        with patch("app.core.file_manager.Translator") as MockTranslator:
            mock_translator = MagicMock()
            mock_translator.use_openai = False
            MockTranslator.side_effect = [ImportError("no openai"), mock_translator]
            fm = FileManager(settings)
            assert fm.translator.use_openai is False
            assert MockTranslator.call_count == 2
