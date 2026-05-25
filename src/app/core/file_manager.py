import os
import json
import shutil
import logging
import zipfile
from zipfile import ZipFile, ZIP_DEFLATED

from .settings import Settings
from .translator import Translator
from ..parsers import json_parser, lang_parser, mcfunction_parser

logger = logging.getLogger("mod_translator")

JAR = ".jar"
JSON = ".json"
LANG = ".lang"
MCFUNCTION = ".mcfunction"


class FileManager:
    def __init__(self, settings: Settings) -> None:
        self.temp_path = settings.temp_path
        self.translation_path = settings.translation_path
        self.mods_path = settings.mods_path
        self.settings = settings

        self.source_mc_lang = settings.source_mc_lang
        self.target_mc_lang = settings.target_mc_lang

        if settings.use_ai:
            logger.info("Using OpenAI translator...")
            try:
                self.translator = Translator(
                    settings.source_google_lang,
                    settings.target_google_lang,
                    use_openai=True,
                )
            except (ImportError, ValueError) as e:
                logger.info("OpenAI initialization failed: %s", e)
                logger.info("Falling back to Google Translate...")
                self.translator = Translator(
                    settings.source_google_lang, settings.target_google_lang
                )
        else:
            logger.info("Using Google Translate...")
            self.translator = Translator(
                settings.source_google_lang, settings.target_google_lang
            )

    def create_needed_folders(self) -> None:
        os.makedirs(self.temp_path, exist_ok=True)
        os.makedirs(self.translation_path, exist_ok=True)

    def unpack_mods(self) -> None:
        mod_list = os.listdir(self.mods_path)
        for mod_name in mod_list:
            if mod_name.endswith(JAR):
                mod_file_path = os.path.join(self.mods_path, mod_name)
                unpacking_destination = os.path.join(self.temp_path, mod_name)
                with ZipFile(mod_file_path, "r") as zip:
                    logger.info("Unpacking %s...", mod_name)
                    zip.extractall(unpacking_destination)

    def get_lang_folders(self) -> list[str]:
        lang_folders: list[str] = []
        found_files: list[tuple[str, str]] = []
        logger.info("Searching for language files in %s...", self.temp_path)

        for foldername, _, filenames in os.walk(self.temp_path):
            source_json_lower = f"{self.source_mc_lang.lower()}{JSON}"
            source_json_original = f"{self.source_mc_lang}{JSON}"
            source_lang_lower = f"{self.source_mc_lang.lower()}{LANG}"
            source_lang_original = f"{self.source_mc_lang}{LANG}"

            for filename in filenames:
                lower_filename = filename.lower()
                if (
                    lower_filename == source_json_lower.lower()
                    or lower_filename == source_json_original.lower()
                    or lower_filename == source_lang_lower.lower()
                    or lower_filename == source_lang_original.lower()
                ):
                    found_files.append((foldername, filename))

        for folder, filename in found_files:
            if "lang" in folder.lower():
                if folder not in lang_folders:
                    lang_folders.append(folder)
                    mod_path_parts = folder.split(os.sep)
                    mod_name = mod_path_parts[1] if len(mod_path_parts) > 1 else "unknown"
                    logger.info("Found language folder: %s", folder)
                    logger.info("Contains source file: %s", filename)
            else:
                parent_folder = os.path.dirname(folder)
                if parent_folder not in lang_folders:
                    lang_folders.append(parent_folder)
                    mod_path_parts = parent_folder.split(os.sep)
                    mod_name = mod_path_parts[1] if len(mod_path_parts) > 1 else "unknown"
                    logger.info("Found language file outside standard lang folder: %s", folder)
                    logger.info("Using parent folder: %s", parent_folder)

        mcfunction_folders = self.get_mcfunction_folders()
        for folder in mcfunction_folders:
            if folder not in lang_folders:
                lang_folders.append(folder)

        if not lang_folders:
            logger.info("Warning: No language folders found containing %s files", self.source_mc_lang)
            for dirpath, dirnames, _ in os.walk(self.temp_path):
                if "lang" in dirpath.lower() or "assets" in dirpath.lower():
                    logger.info("  - %s", dirpath)
                    logger.info("    Contents: %s", os.listdir(dirpath))

        return lang_folders

    def get_mcfunction_folders(self) -> list[str]:
        mcfunction_folders: list[str] = []
        logger.info("Searching for .mcfunction files in %s...", self.temp_path)

        for foldername, _, filenames in os.walk(self.temp_path):
            for filename in filenames:
                if filename.endswith(MCFUNCTION):
                    path_parts = foldername.split(os.sep)
                    temp_parts = self.temp_path.split(os.sep)

                    if len(path_parts) > len(temp_parts):
                        mod_root_parts = temp_parts + [path_parts[len(temp_parts)]]
                        mod_root = os.sep.join(mod_root_parts)

                        if mod_root not in mcfunction_folders:
                            mcfunction_folders.append(mod_root)
                            mod_name = path_parts[len(temp_parts)] if len(path_parts) > len(temp_parts) else "unknown"
                            logger.info("Found mod with .mcfunction files: %s", mod_name)
                            break

        return mcfunction_folders

    def edit_lang_files(self, lang_folders: list[str]) -> None:
        for lang_folder in lang_folders:
            path_parts = lang_folder.split(os.sep)
            if len(path_parts) > 1:
                mod_name = path_parts[1]
                mod_name = mod_name.replace(JAR, "")
            else:
                mod_name = "unknown-mod"

            logger.info("Processing %s...", mod_name)

            source_json_path = os.path.join(lang_folder, f"{self.source_mc_lang.lower()}{JSON}")
            source_lang_path = os.path.join(lang_folder, f"{self.source_mc_lang}{LANG}")
            target_json_path = os.path.join(lang_folder, f"{self.target_mc_lang.lower()}{JSON}")
            target_lang_path = os.path.join(lang_folder, f"{self.target_mc_lang}{LANG}")

            files_processed = False

            if os.path.exists(source_json_path):
                logger.info("Creating %s%s from %s%s...", self.target_mc_lang.lower(), JSON, self.source_mc_lang.lower(), JSON)
                original_data = self._read_json_file(source_json_path)
                if original_data:
                    translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                    self._write_json_file(translated_data, target_json_path)
                    logger.info("Successfully translated JSON file for %s", mod_name)
                    files_processed = True
                else:
                    logger.info("No data found in source JSON file for %s", mod_name)

            if os.path.exists(source_lang_path):
                logger.info("Creating %s%s from %s%s...", self.target_mc_lang, LANG, self.source_mc_lang, LANG)
                original_data = self._read_lang_file(source_lang_path)
                if original_data:
                    translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                    self._write_lang_file(translated_data, target_lang_path)
                    logger.info("Successfully translated LANG file for %s", mod_name)
                    files_processed = True
                else:
                    logger.info("No data found in source LANG file for %s", mod_name)

            if not files_processed:
                logger.info("Searching for alternative source files in %s...", lang_folder)
                for filename in os.listdir(lang_folder):
                    lower_filename = filename.lower()

                    if lower_filename == f"{self.source_mc_lang.lower()}{JSON}".lower():
                        source_file_path = os.path.join(lang_folder, filename)
                        target_file_path = os.path.join(lang_folder, f"{self.target_mc_lang.lower()}{JSON}")
                        logger.info("Creating %s%s from %s...", self.target_mc_lang.lower(), JSON, filename)
                        original_data = self._read_json_file(source_file_path)
                        if original_data:
                            translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                            self._write_json_file(translated_data, target_file_path)
                            logger.info("Successfully translated JSON file for %s", mod_name)
                            files_processed = True

                    elif lower_filename == f"{self.source_mc_lang}{LANG}".lower():
                        source_file_path = os.path.join(lang_folder, filename)
                        target_file_path = os.path.join(lang_folder, f"{self.target_mc_lang}{LANG}")
                        logger.info("Creating %s%s from %s...", self.target_mc_lang, LANG, filename)
                        original_data = self._read_lang_file(source_file_path)
                        if original_data:
                            translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                            self._write_lang_file(translated_data, target_file_path)
                            logger.info("Successfully translated LANG file for %s", mod_name)
                            files_processed = True

            if not files_processed:
                logger.info("No translatable language files found for %s", mod_name)

            temp_path_parts = self.temp_path.split(os.sep)
            lang_folder_parts = lang_folder.split(os.sep)
            if len(lang_folder_parts) == len(temp_path_parts) + 1:
                logger.info("Checking for .mcfunction files in %s...", mod_name)
                self.translate_mcfunction_files(lang_folder)
                files_processed = True

    def _read_json_file(self, path: str) -> dict[str, str]:
        try:
            data = json_parser.parse_json_with_comments(path)
            if data:
                logger.info("Successfully loaded JSON with %d entries", len(data))
            else:
                logger.info("Warning: No data found in JSON file: %s", path)
            return data
        except Exception:
            logger.info("Warning: No data found in JSON file: %s", path)
            return {}

    def _read_lang_file(self, path: str) -> dict[str, str]:
        return lang_parser.read_lang_file(path)

    def _write_json_file(self, data: dict[str, str], path: str) -> None:
        try:
            logger.info("Writing JSON file to %s", path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            if os.path.exists(path):
                file_size = os.path.getsize(path)
                logger.info("JSON file successfully written (%d bytes)", file_size)
                with open(path, "r", encoding="utf-8") as check_file:
                    content = check_file.read()
                    if len(content) > 0:
                        logger.info("Verified file content: %d bytes", len(content))
                    else:
                        logger.info("WARNING: File exists but is empty")
            else:
                logger.info("WARNING: Failed to create file %s", path)
        except OSError as e:
            logger.error("ERROR writing JSON file: %s", e)

    def _write_lang_file(self, data: dict[str, str], path: str) -> None:
        try:
            logger.info("Writing LANG file to %s", path)
            lang_parser.write_lang_file(data, path)
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                logger.info("LANG file successfully written (%d bytes)", file_size)
            else:
                logger.info("WARNING: Failed to create file %s", path)
        except OSError as e:
            logger.error("ERROR writing LANG file: %s", e)

    def _read_mcfunction_file(self, path: str) -> dict[str, str]:
        data = mcfunction_parser.read_mcfunction_file(path)
        logger.info("Extracted %d translatable strings from %s", len(data), path)
        return data

    def _write_mcfunction_file(self, original_path: str, translated_data: dict[str, str]) -> None:
        try:
            logger.info("Writing MCFUNCTION file to %s", original_path)
            mcfunction_parser.write_mcfunction_file(original_path, translated_data)
            file_size = os.path.getsize(original_path)
            logger.info("MCFUNCTION file successfully updated (%d bytes)", file_size)
        except OSError as e:
            logger.error("ERROR writing MCFUNCTION file: %s", e)

    def translate_mcfunction_files(self, mod_root_path: str) -> None:
        mcfunction_files = []
        for foldername, _, filenames in os.walk(mod_root_path):
            for filename in filenames:
                if filename.endswith(MCFUNCTION):
                    file_path = os.path.join(foldername, filename)
                    mcfunction_files.append(file_path)

        if not mcfunction_files:
            return

        logger.info("Found %d .mcfunction files to translate", len(mcfunction_files))

        for file_path in mcfunction_files:
            logger.info("Processing %s", file_path)
            original_data = self._read_mcfunction_file(file_path)
            if original_data:
                translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                self._write_mcfunction_file(file_path, translated_data)
                logger.info("Successfully translated %d strings in %s", len(original_data), file_path)
            else:
                logger.info("No translatable content found in %s", file_path)

    def convert_translated_mods(self) -> None:
        mod_folder_list = os.listdir(self.temp_path)
        for mod_folder in mod_folder_list:
            logger.info("Converting %s into mod file...", mod_folder)
            unpacked_mod_path = os.path.join(self.temp_path, mod_folder)

            same_paths = os.path.abspath(self.mods_path) == os.path.abspath(self.translation_path)
            if same_paths:
                translation_path = os.path.join(self.mods_path, mod_folder)
            else:
                translation_path = os.path.join(self.translation_path, mod_folder)

            self._convert_folder_to_jar(unpacked_mod_path, translation_path)

    def _convert_folder_to_jar(self, folder_path: str, jar_path: str) -> None:
        logger.info("Creating JAR file: %s", jar_path)
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)

        lang_files_found = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".json") or file.lower().endswith(".lang"):
                    if self.target_mc_lang.lower() in file.lower():
                        relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                        lang_files_found.append(relative_path)
                        logger.info("Found target language file: %s", relative_path)

        if not lang_files_found:
            logger.info("WARNING: No target language files found. Looking for source files...")
            source_files_found = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(".json") or file.lower().endswith(".lang"):
                        if self.source_mc_lang.lower() in file.lower():
                            source_path = os.path.join(root, file)
                            target_path = source_path.replace(
                                self.source_mc_lang.lower(), self.target_mc_lang.lower()
                            )
                            source_files_found.append((source_path, target_path, file))
                            logger.info("Found source language file: %s", file)

            for source_path, target_path, filename in source_files_found:
                extension = os.path.splitext(filename)[1].lower()
                if extension == JSON:
                    logger.info("Translating source file: %s", filename)
                    original_data = self._read_json_file(source_path)
                    if original_data:
                        translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                        self._write_json_file(translated_data, target_path)
                        relative_path = os.path.relpath(target_path, folder_path)
                        lang_files_found.append(relative_path)
                elif extension == LANG:
                    logger.info("Translating source file: %s", filename)
                    original_data = self._read_lang_file(source_path)
                    if original_data:
                        translated_data = self.translator.translate_data(original_data, max_workers=self.settings.max_workers)
                        self._write_lang_file(translated_data, target_path)
                        relative_path = os.path.relpath(target_path, folder_path)
                        lang_files_found.append(relative_path)

        file_count = 0
        tmp_jar_path = jar_path + ".tmp"
        try:
            with ZipFile(tmp_jar_path, "w", ZIP_DEFLATED) as jar:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, folder_path)
                        jar.write(file_path, relative_path)
                        file_count += 1

                        if file.lower().endswith(".json") or file.lower().endswith(".lang"):
                            if self.target_mc_lang.lower() in file.lower():
                                logger.info("Added target language file to JAR: %s", relative_path)

            if os.path.exists(tmp_jar_path):
                if zipfile.is_zipfile(tmp_jar_path):
                    if os.path.exists(jar_path):
                        os.remove(jar_path)
                    os.rename(tmp_jar_path, jar_path)
                    jar_size = os.path.getsize(jar_path)
                    logger.info("Successfully created JAR file with %d files (%d bytes)", file_count, jar_size)
                else:
                    logger.error("Temp JAR is not valid: %s", tmp_jar_path)
                    os.remove(tmp_jar_path)
            else:
                logger.error("Failed to create JAR file %s", jar_path)
        except OSError as e:
            logger.error("ERROR creating JAR file: %s", e)

    def remove_original_mod_files(self) -> None:
        translated_jars = [f for f in os.listdir(self.translation_path) if f.endswith(JAR)]
        if not translated_jars:
            logger.info("WARNING: No translated JAR files found. Skipping removal of original files.")
            return

        logger.info("Found %d translated JAR files. Proceeding with removal of originals.", len(translated_jars))

        files_to_remove = []
        for filename in os.listdir(self.mods_path):
            file_path = os.path.join(self.mods_path, filename)
            if os.path.isfile(file_path) and file_path.endswith(JAR):
                if filename in translated_jars:
                    files_to_remove.append(file_path)

        logger.info("Will remove %d original JAR files that have translated versions", len(files_to_remove))

        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                logger.info("Removed original JAR file: %s", file_path)
            except OSError as e:
                logger.error("Error removing original JAR file %s: %s", file_path, e)

    def move_translated_mod_files(self) -> None:
        for filename in os.listdir(self.translation_path):
            source_path = os.path.join(self.translation_path, filename)
            destination_path = os.path.join(self.mods_path, filename)

            if os.path.abspath(source_path) == os.path.abspath(destination_path):
                logger.info("Skipping %s as source and destination are the same", filename)
                continue

            logger.info("Moving %s from %s to %s", filename, self.translation_path, self.mods_path)

            if os.path.isfile(source_path):
                shutil.copy2(source_path, destination_path)
                logger.info("Copied file %s", filename)
            elif os.path.isdir(source_path):
                if os.path.exists(destination_path):
                    for root, dirs, files in os.walk(source_path):
                        rel_path = os.path.relpath(root, source_path)
                        if rel_path == ".":
                            rel_path = ""
                        target_dir = os.path.join(destination_path, rel_path)
                        os.makedirs(target_dir, exist_ok=True)
                        for file in files:
                            src_file = os.path.join(root, file)
                            dst_file = os.path.join(target_dir, file)
                            shutil.copy2(src_file, dst_file)
                            logger.info("Copied %s", os.path.join(rel_path, file))
                else:
                    shutil.copytree(source_path, destination_path)
                    logger.info("Copied directory %s", filename)

    def copy_translated_files_to_same_path(self) -> None:
        logger.info("Copying translated files to original directory: %s", self.mods_path)
        os.makedirs(self.mods_path, exist_ok=True)

        jar_files_copied = 0
        for filename in os.listdir(self.translation_path):
            source_path = os.path.join(self.translation_path, filename)
            dest_path = os.path.join(self.mods_path, filename)

            if os.path.isfile(source_path) and source_path.endswith(JAR):
                logger.info("Copying JAR file: %s", filename)
                try:
                    shutil.copy2(source_path, dest_path)
                    jar_files_copied += 1
                    logger.info("Copied %s to %s", filename, self.mods_path)
                except OSError as e:
                    logger.error("Error copying JAR file %s: %s", filename, e)
            elif os.path.isdir(source_path):
                logger.info("Processing directory: %s", filename)
                for root, dirs, files in os.walk(source_path):
                    rel_path = os.path.relpath(root, source_path)
                    if rel_path == ".":
                        rel_path = ""
                    target_dir = os.path.join(dest_path, rel_path)
                    os.makedirs(target_dir, exist_ok=True)
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(target_dir, file)
                        try:
                            shutil.copy2(src_file, dst_file)
                            logger.info("Copied file: %s", os.path.join(rel_path, file))
                        except OSError as e:
                            logger.error("Error copying file %s: %s", os.path.join(rel_path, file), e)

        if jar_files_copied > 0:
            logger.info("Successfully copied %d JAR files to %s", jar_files_copied, self.mods_path)
        else:
            logger.info("WARNING: No JAR files were copied to %s", self.mods_path)

        jar_files_in_dest = [f for f in os.listdir(self.mods_path) if f.endswith(JAR)]
        logger.info("JAR files in destination directory after copying: %d", len(jar_files_in_dest))
        for jar_file in jar_files_in_dest:
            jar_path = os.path.join(self.mods_path, jar_file)
            jar_size = os.path.getsize(jar_path)
            logger.info("  - %s (%d bytes)", jar_file, jar_size)

    def remove_folder(self, folder_path: str) -> None:
        shutil.rmtree(folder_path)
