import argparse


class Settings:
    def __init__(self, cli_args: argparse.Namespace | None = None) -> None:
        self.source_mc_lang = self._format_lang("en_US")
        self.target_mc_lang = self._format_lang("es_ES")
        self.mods_path = "./"
        self.temp_path = "temp"
        self.translation_path = "./translated"
        self.provider = "google"

        if cli_args:
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

        self.source_google_lang = self._get_google_lang(self.source_mc_lang)
        self.target_google_lang = self._get_google_lang(self.target_mc_lang)
        self.max_workers = getattr(cli_args, "workers", 4) if cli_args else 4
        self.dry_run = getattr(cli_args, "dry_run", False) if cli_args else False

    def _get_google_lang(self, mc_lang: str) -> str:
        google_lang = mc_lang.split("_")[0]
        return google_lang

    def _format_lang(self, mc_lang: str) -> str:
        language, region = mc_lang.split("_")
        formatted_language_code = f"{language.lower()}_{region.upper()}"
        return formatted_language_code
