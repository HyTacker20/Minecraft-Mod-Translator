from __future__ import annotations

import argparse
from typing import Any


class Settings:
    def __init__(
        self,
        cli_args: argparse.Namespace | None = None,
        config_data: dict[str, Any] | None = None,
    ) -> None:
        self.source_mc_lang = self._format_lang("en_US")
        self.target_mc_lang = self._format_lang("es_ES")
        self.mods_path = "./"
        self.temp_path = "temp"
        self.translation_path = "./translated_mods"
        self.provider = "google"
        self.max_workers = 4
        self.dry_run = False

        if config_data:
            self._apply_config_data(config_data)

        if cli_args:
            self._apply_cli_args(cli_args)

        self.source_google_lang = self._get_google_lang(self.source_mc_lang)
        self.target_google_lang = self._get_google_lang(self.target_mc_lang)

    def _apply_config_data(self, config_data: dict[str, Any]) -> None:
        if "source" in config_data and config_data["source"]:
            self.source_mc_lang = self._format_lang(config_data["source"])
        if "target" in config_data and config_data["target"]:
            self.target_mc_lang = self._format_lang(config_data["target"])
        if "provider" in config_data and config_data["provider"]:
            self.provider = config_data["provider"]
        if "workers" in config_data and config_data["workers"] is not None:
            self.max_workers = int(config_data["workers"])
        if "output" in config_data and config_data["output"]:
            self.translation_path = config_data["output"]

    def _apply_cli_args(self, cli_args: argparse.Namespace) -> None:
        if hasattr(cli_args, "source") and cli_args.source:
            self.source_mc_lang = self._format_lang(cli_args.source)

        if hasattr(cli_args, "target") and cli_args.target:
            self.target_mc_lang = self._format_lang(cli_args.target)

        if hasattr(cli_args, "path") and cli_args.path:
            self.mods_path = cli_args.path

        if hasattr(cli_args, "output") and cli_args.output:
            self.translation_path = cli_args.output

        if hasattr(cli_args, "provider") and cli_args.provider:
            self.provider = cli_args.provider

        if hasattr(cli_args, "ai") and cli_args.ai:
            self.provider = "openai"

        if hasattr(cli_args, "workers"):
            self.max_workers = cli_args.workers

        if hasattr(cli_args, "dry_run"):
            self.dry_run = cli_args.dry_run

    def _get_google_lang(self, mc_lang: str) -> str:
        google_lang = mc_lang.split("_")[0]
        return google_lang

    def _format_lang(self, mc_lang: str) -> str:
        language, region = mc_lang.split("_")
        formatted_language_code = f"{language.lower()}_{region.upper()}"
        return formatted_language_code
