"""
Minecraft mod translation orchestration.
"""

import argparse
import logging
import os
import zipfile

from ..core.config_loader import find_config_file, load_config
from ..core.file_manager import FileManager
from ..core.settings import Settings
from ..logging_config import setup_logging

logger = logging.getLogger("mod_translator")

JAR = ".jar"


def add_translate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-p", "--path", help="Path to mod or mod folder", default="./mods")
    parser.add_argument("-s", "--source", help="Source language code (e.g., en_US)")
    parser.add_argument("-t", "--target", help="Target language code (e.g., es_ES)")
    parser.add_argument("-o", "--output", help="Output folder path")
    parser.add_argument(
        "--provider",
        type=str,
        default="google",
        choices=["google", "openai", "anthropic", "gemini", "ollama", "litellm", "openaicompatible"],
        help="Translation provider (default: google)",
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="[DEPRECATED] Use --provider openai instead",
    )
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent translation workers (default: 4)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without making changes")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging to console")
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to translator.toml config file (auto-discovered if not specified)",
    )


def _check_dependencies(provider: str) -> bool:
    if provider == "google":
        try:
            from deep_translator import GoogleTranslator  # noqa: F401
        except ImportError:
            logger.error("deep_translator package is required. Install with: pip install deep-translator")
            return False
        return True

    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded .env file")
    except ImportError:
        logger.info("python-dotenv not found, using system environment variables")

    if provider == "openai":
        try:
            import openai  # noqa: F401
        except ImportError:
            try:
                import litellm  # noqa: F401
            except ImportError:
                logger.error(
                    "OpenAI or LiteLLM package is required for OpenAI provider. "
                    "Install with: pip install openai litellm"
                )
                return False
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            return False
        logger.info("OpenAI API key configured")
        return True

    if provider == "openaicompatible":
        try:
            import openai  # noqa: F401
        except ImportError:
            logger.error(
                "OpenAI package is required for OpenAI-Compatible provider. "
                "Install with: pip install openai"
            )
            return False
        api_key = os.getenv("OPENAICOMPATIBLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAICOMPATIBLE_API_KEY environment variable not set.")
            return False
        base_url = os.getenv("OPENAICOMPATIBLE_BASE_URL")
        if not base_url:
            logger.error("OPENAICOMPATIBLE_BASE_URL environment variable not set.")
            return False
        logger.info("OpenAI-Compatible API configured (base_url: %s)", base_url)
        return True

    try:
        import litellm  # noqa: F401
    except ImportError:
        logger.error("LiteLLM package is required for AI providers. Install with: pip install litellm")
        return False

    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set.")
            return False
        logger.info("Anthropic API key configured")
        return True

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set.")
            return False
        logger.info("Gemini API key configured")
        return True

    logger.info("LiteLLM configured for provider: %s", provider)
    return True


def handle_translate_command(args: argparse.Namespace) -> None:
    try:
        provider = getattr(args, "provider", "google")
        if getattr(args, "ai", False):
            logger.warning("--ai flag is deprecated, use --provider openai instead")
            provider = "openai"

        if not _check_dependencies(provider):
            return

        debug = getattr(args, "debug", False)
        setup_logging(console_level=logging.DEBUG if debug else logging.INFO)

        args.provider = provider
        config_data = None
        config_path = find_config_file(getattr(args, "path", "./"), getattr(args, "config", None))
        if config_path:
            config_data = load_config(config_path)
        settings = Settings(cli_args=args, config_data=config_data)
        file_manager = FileManager(settings)

        file_manager.create_needed_folders()

        if getattr(args, "dry_run", False):
            logger.info("--- DRY RUN ---")
            logger.info("Mods path: %s", settings.mods_path)
            logger.info("Source language: %s", settings.source_mc_lang)
            logger.info("Target language: %s", settings.target_mc_lang)
            logger.info("Translation provider: %s", settings.provider)
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
    except KeyboardInterrupt:
        logger.info("Translation interrupted by user. Cleaning up...")
        try:
            if "settings" in locals() and os.path.exists(settings.temp_path):
                file_manager.remove_folder(settings.temp_path)
        except Exception:
            pass
    except Exception as e:
        logger.exception("Error translating mods: %s", e)
