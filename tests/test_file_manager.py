import json
import os
from pathlib import Path
from unittest.mock import patch

from app.core.file_manager import FileManager
from app.core.settings import Settings


class TestFileManager:
    def test_create_needed_folders(self, tmp_path: Path):
        settings = Settings()
        settings.temp_path = str(tmp_path / "temp")
        settings.translation_path = str(tmp_path / "out")
        fm = FileManager(settings)
        fm.create_needed_folders()
        assert os.path.exists(str(tmp_path / "temp"))
        assert os.path.exists(str(tmp_path / "out"))

    def test_read_lang_file(self, sample_en_us_lang_file: Path):
        settings = Settings()
        fm = FileManager(settings)
        data = fm._read_lang_file(str(sample_en_us_lang_file))
        assert data["item.diamond.name"] == "Diamond"
        assert data["item.gold_ingot.name"] == "Gold Ingot"
        assert len(data) == 4

    def test_write_lang_file(self, tmp_path: Path, sample_en_us_json: dict):
        settings = Settings()
        fm = FileManager(settings)
        out_path = tmp_path / "output.lang"
        fm._write_lang_file(sample_en_us_json, str(out_path))
        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8")
        for key, value in sample_en_us_json.items():
            assert f"{key}={value}" in content

    def test_read_json_file(self, clean_sample_en_us_json_path: Path):
        settings = Settings()
        fm = FileManager(settings)
        data = fm._read_json_file(str(clean_sample_en_us_json_path))
        assert data["item.minecraft.diamond"] == "Diamond"
        assert len(data) == 4

    def test_write_json_file(self, tmp_path: Path, sample_en_us_json: dict):
        settings = Settings()
        fm = FileManager(settings)
        out_path = tmp_path / "sub" / "output.json"
        fm._write_json_file(sample_en_us_json, str(out_path))
        assert out_path.exists()
        with open(out_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data == sample_en_us_json

    def test_read_mcfunction_file(self, sample_mcfunction_file: Path):
        settings = Settings()
        fm = FileManager(settings)
        data = fm._read_mcfunction_file(str(sample_mcfunction_file))
        assert len(data) == 3
        values = list(data.values())
        assert "Player joined the game" in values
        assert "Welcome to the arena!" in values
        assert "Goodbye, see you next time!" in values

    def test_write_mcfunction_file(self, sample_mcfunction_file: Path):
        settings = Settings()
        fm = FileManager(settings)
        translated = {}
        for key, val in fm._read_mcfunction_file(str(sample_mcfunction_file)).items():
            translated[key] = "TR_" + val
        fm._write_mcfunction_file(str(sample_mcfunction_file), translated)
        data = fm._read_mcfunction_file(str(sample_mcfunction_file))
        for v in data.values():
            assert v.startswith("TR_")

    def test_unpack_mods(self, temp_mods_dir: Path, sample_jar: Path, tmp_path: Path):
        settings = Settings()
        settings.mods_path = str(temp_mods_dir)
        settings.temp_path = str(tmp_path / "temp")
        fm = FileManager(settings)
        fm.create_needed_folders()
        fm.unpack_mods()
        unpacked = os.path.join(str(tmp_path / "temp"), "test_mod.jar")
        assert os.path.exists(unpacked)
        lang_dir = os.path.join(unpacked, "assets", "testmod", "lang")
        assert os.path.exists(lang_dir)

    def test_get_lang_folders(self, temp_mods_dir: Path, sample_jar: Path, tmp_path: Path):
        settings = Settings()
        settings.source_mc_lang = "en_US"
        settings.mods_path = str(temp_mods_dir)
        settings.temp_path = str(tmp_path / "temp")
        fm = FileManager(settings)
        fm.create_needed_folders()
        fm.unpack_mods()
        folders = fm.get_lang_folders()
        assert len(folders) > 0

    def test_convert_folder_to_jar(self, tmp_path: Path, sample_en_us_json: dict):
        settings = Settings()
        folder_path = tmp_path / "mod_folder"
        assets = folder_path / "assets" / "testmod" / "lang"
        assets.mkdir(parents=True)
        en_path = assets / "en_us.json"
        en_path.write_text(json.dumps(sample_en_us_json), encoding="utf-8")
        jar_path = tmp_path / "output" / "test.jar"
        os.makedirs(str(tmp_path / "output"), exist_ok=True)
        fm = FileManager(settings)
        fm._convert_folder_to_jar(str(folder_path), str(jar_path))
        assert jar_path.exists()
        assert jar_path.stat().st_size > 0

    def test_edit_lang_files(self, tmp_path: Path, sample_en_us_json: dict):
        settings = Settings()
        settings.source_mc_lang = "en_US"
        settings.target_mc_lang = "uk_UA"
        settings.temp_path = str(tmp_path / "temp")
        os.makedirs(settings.temp_path, exist_ok=True)
        mod_root = os.path.join(settings.temp_path, "testmod.jar")
        lang_dir = os.path.join(mod_root, "assets", "testmod", "lang")
        os.makedirs(lang_dir, exist_ok=True)
        en_path = os.path.join(lang_dir, "en_us.json")
        with open(en_path, "w", encoding="utf-8") as f:
            json.dump(sample_en_us_json, f)
        fm = FileManager(settings)
        with patch.object(fm.translator, "translate_data", return_value={k: f"tr_{v}" for k, v in sample_en_us_json.items()}):
            fm.edit_lang_files([lang_dir])
        target_path = os.path.join(lang_dir, "uk_ua.json")
        assert os.path.exists(target_path)
