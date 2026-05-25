"""
Minecraft mod translation orchestration.
"""

import argparse
import logging
import os
import zipfile

from ..core.file_manager import FileManager
from ..core.settings import Settings

logger = logging.getLogger("mod_translator")

JAR = ".jar"


def add_translate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-p", "--path", help="Path to mod or mod folder", default="./mods")
    parser.add_argument("-s", "--source", help="Source language code (e.g., en_US)")
    parser.add_argument("-t", "--target", help="Target language code (e.g., es_ES)")
    parser.add_argument("-o", "--output", help="Output folder path")
    parser.add_argument("--ai", action="store_true", help="Use OpenAI translation instead of Google Translate")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent translation workers (default: 4)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without making changes")


def _check_dependencies(use_ai: bool) -> bool:
    if use_ai:
        try:
            import openai
            try:
                from dotenv import load_dotenv
                load_dotenv()
                logger.info("Loaded .env file")
            except ImportError:
                logger.info("python-dotenv not found, using system environment variables")

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set.")
                return False
            else:
                logger.info("OpenAI API key configured")
        except ImportError:
            logger.error("OpenAI package not found. Install with: pip install openai python-dotenv")
            return False
    else:
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            logger.error("deep_translator package is required. Install with: pip install deep-translator")
            return False
    return True


def handle_translate_command(args: argparse.Namespace) -> None:
    try:
        if not _check_dependencies(getattr(args, "ai", False)):
            return

        settings = Settings(cli_args=args)
        file_manager = FileManager(settings)

        file_manager.create_needed_folders()

        if getattr(args, "dry_run", False):
            logger.info("--- DRY RUN ---")
            logger.info("Mods path: %s", settings.mods_path)
            logger.info("Source language: %s", settings.source_mc_lang)
            logger.info("Target language: %s", settings.target_mc_lang)
            logger.info("Translation method: %s", "OpenAI" if settings.use_ai else "Google Translate")
            logger.info("Output path: %s", settings.translation_path)
            logger.info("Workers: %d", settings.max_workers)

            file_manager.unpack_mods()
            lang_folders = file_manager.get_lang_folders()
            logger.info("Would translate files in %d folder(s):", len(lang_folders))
            for folder in lang_folders:
                logger.info("  - %s", folder)
            logger.info("--- DRY RUN COMPLETE (no files modified) ---")
            file_manager.remove_folder(settings.temp_path)
            return

        logger.info("Unpacking mod files...")
        file_manager.unpack_mods()
        lang_folders = file_manager.get_lang_folders()
        logger.info("Translating mods...")
        file_manager.edit_lang_files(lang_folders)

        same_paths = os.path.abspath(settings.mods_path) == os.path.abspath(settings.translation_path)

        logger.info("Converting to mod files...")
        file_manager.convert_translated_mods()

        if same_paths:
            logger.info("Verifying translated JAR files...")
            jar_files = [f for f in os.listdir(settings.mods_path) if f.endswith(JAR)]
            logger.info("Found %d JAR files in output directory", len(jar_files))
            for jar_file in jar_files:
                jar_path = os.path.join(settings.mods_path, jar_file)
                if not zipfile.is_zipfile(jar_path):
                    logger.warning("%s is not a valid JAR file", jar_file)
                size = os.path.getsize(jar_path)
                logger.info("Verified JAR file: %s (%d bytes)", jar_file, size)
        else:
            logger.info("Translation completed to output directory...")

        file_manager.remove_folder(settings.temp_path)
        logger.info("All mods have been translated!")
    except Exception as e:
        logger.exception("Error translating mods: %s", e)
