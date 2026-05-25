from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger("mod_translator")

CONFIG_FILE_NAME = "translator.toml"
HIDDEN_CONFIG_FILE_NAME = ".translator.toml"

VALID_CONFIG_KEYS = frozenset({"source", "target", "provider", "workers", "output"})

CONFIG_TEMPLATE = """# Minecraft Mod Translator configuration
# This file is auto-discovered when placed next to your mods.
# CLI arguments override values set here.

[translation]
# Source language code (e.g., en_US)
source = "en_US"

# Target language code (e.g., uk_UA)
target = "es_ES"

# Translation provider: google, openai, anthropic, gemini, ollama, litellm, openaicompatible
provider = "google"

# Number of concurrent translation workers
workers = 4

# Output directory for translated mods (relative to config file or absolute)
# output = "./translated_mods"
"""


def find_config_file(mods_path: str, explicit_path: str | None = None) -> Path | None:
    if explicit_path:
        explicit = Path(explicit_path)
        if explicit.is_file():
            logger.info("Using explicitly specified config file: %s", explicit)
            return explicit
        logger.warning("Explicit config file not found: %s", explicit)
        return None

    search_paths: list[Path] = []

    mods_dir = Path(mods_path).resolve()
    if mods_dir.is_dir():
        search_paths.append(mods_dir / CONFIG_FILE_NAME)

    cwd = Path.cwd()
    if cwd != mods_dir:
        search_paths.append(cwd / CONFIG_FILE_NAME)
        search_paths.append(cwd / HIDDEN_CONFIG_FILE_NAME)
    else:
        search_paths.append(cwd / HIDDEN_CONFIG_FILE_NAME)

    for candidate in search_paths:
        if candidate.is_file():
            logger.info("Found config file at: %s", candidate)
            return candidate

    return None


def load_config(config_path: Path) -> dict[str, Any]:
    logger.info("Loading config from: %s", config_path)
    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    translation_table = raw.get("translation", {})
    if not isinstance(translation_table, dict):
        logger.warning("Config [translation] section is not a table, ignoring")
        return {}

    config: dict[str, Any] = {}
    for key, value in translation_table.items():
        if key in VALID_CONFIG_KEYS:
            if key == "workers" and not isinstance(value, (int, type(None))):
                try:
                    config[key] = int(value)
                except (ValueError, TypeError):
                    logger.warning("Config key 'workers' must be an integer, got: %s", type(value).__name__)
                    continue
            else:
                config[key] = value
        else:
            logger.warning("Unknown config key: '%s' — ignoring", key)

    return config


def generate_config_template(output_dir: str) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    config_path = out / CONFIG_FILE_NAME
    config_path.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    logger.info("Generated config template at: %s", config_path)
    return config_path
