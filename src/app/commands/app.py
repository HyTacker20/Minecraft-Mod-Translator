"""
Console application interface for Mod Translator.
This module provides a user-friendly form-based terminal interface.
"""

import argparse
import os
import sys
from typing import Any

import questionary
from loguru import logger
from pyfiglet import Figlet
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from ..commands.translate import (
    handle_translate_command,
)
from ..core.config_loader import find_config_file, load_config
from ..core.mod_scanner import ModInfo, ModScanner
from ..core.provider_check import check_provider_available
from ..logging_config import setup_logging
from ..utils.progress import ProgressReporter
from ..utils.stats import OverallStats

UI_THEME = Theme(
    {
        "primary": "white",
        "secondary": "bright_black",
        "accent": "bright_green",
        "success": "bold green",
        "warning": "bold red",
        "error": "bold red",
    }
)



QUESTIONARY_STYLE = questionary.Style(
    [
        ("qmark", "fg:#FF5555 bold"),
        ("question", "fg:#FFFFFF"),
        ("answer", "fg:#AAAAAA"),
        ("pointer", "fg:#666666 bold"),
        ("highlighted", "fg:#FF5555 bold"),
        ("selected", "fg:#AAAAAA"),
        ("separator", "fg:#AAAAAA"),
        ("instruction", "fg:#AAAAAA"),
        ("text", "fg:#AAAAAA"),
    ]
)

console = Console(theme=UI_THEME)


def display_title() -> None:
    """Display the application title using figlet."""
    os.system("cls" if os.name == "nt" else "clear")

    if os.name == "nt":
        os.system("title Minecraft Mod Translator")

    f = Figlet(font="chunky")
    title1 = f.renderText("Minecraft Mod")
    title2 = f.renderText("Translator")
    console.print(Align.center(Text(title1, style="bold red")))
    console.print(Align.center(Text(title2, style="bold red")))
    console.print(Align.center(Text("Translate your Minecraft mods from one language to another", style="italic")))
    console.print()


def get_user_input(config_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Collect user input through a form interface."""
    if config_data is None:
        config_data = {}
    try:
        language_options = [
            {"name": "Afrikaans (af_ZA)", "value": "af_ZA"},
            {"name": "Albanian (sq_AL)", "value": "sq_AL"},
            {"name": "Arabic (ar_SA)", "value": "ar_SA"},
            {"name": "Armenian (hy_AM)", "value": "hy_AM"},
            {"name": "Asturian (ast_ES)", "value": "ast_ES"},
            {"name": "Azerbaijani (az_AZ)", "value": "az_AZ"},
            {"name": "Basque (eu_ES)", "value": "eu_ES"},
            {"name": "Belarusian (be_BY)", "value": "be_BY"},
            {"name": "Bosnian (bs_BA)", "value": "bs_BA"},
            {"name": "Bulgarian (bg_BG)", "value": "bg_BG"},
            {"name": "Catalan (ca_ES)", "value": "ca_ES"},
            {"name": "Chinese Simplified (zh_CN)", "value": "zh_CN"},
            {"name": "Chinese Traditional (zh_TW)", "value": "zh_TW"},
            {"name": "Cornish (kw_GB)", "value": "kw_GB"},
            {"name": "Croatian (hr_HR)", "value": "hr_HR"},
            {"name": "Czech (cs_CZ)", "value": "cs_CZ"},
            {"name": "Danish (da_DK)", "value": "da_DK"},
            {"name": "Dutch (nl_NL)", "value": "nl_NL"},
            {"name": "English United States (en_US)", "value": "en_US"},
            {"name": "English Australia (en_AU)", "value": "en_AU"},
            {"name": "English Canada (en_CA)", "value": "en_CA"},
            {"name": "English New Zealand (en_NZ)", "value": "en_NZ"},
            {"name": "English United Kingdom (en_GB)", "value": "en_GB"},
            {"name": "Esperanto (eo_UY)", "value": "eo_UY"},
            {"name": "Estonian (et_EE)", "value": "et_EE"},
            {"name": "Faroese (fo_FO)", "value": "fo_FO"},
            {"name": "Filipino (fil_PH)", "value": "fil_PH"},
            {"name": "Finnish (fi_FI)", "value": "fi_FI"},
            {"name": "French France (fr_FR)", "value": "fr_FR"},
            {"name": "French Canada (fr_CA)", "value": "fr_CA"},
            {"name": "Frisian (fy_NL)", "value": "fy_NL"},
            {"name": "Galician (gl_ES)", "value": "gl_ES"},
            {"name": "Georgian (ka_GE)", "value": "ka_GE"},
            {"name": "German (de_DE)", "value": "de_DE"},
            {"name": "Greek (el_GR)", "value": "el_GR"},
            {"name": "Hawaiian (haw)", "value": "haw"},
            {"name": "Hebrew (he_IL)", "value": "he_IL"},
            {"name": "Hindi (hi_IN)", "value": "hi_IN"},
            {"name": "Hungarian (hu_HU)", "value": "hu_HU"},
            {"name": "Icelandic (is_IS)", "value": "is_IS"},
            {"name": "Indonesian (id_ID)", "value": "id_ID"},
            {"name": "Irish (ga_IE)", "value": "ga_IE"},
            {"name": "Italian (it_IT)", "value": "it_IT"},
            {"name": "Japanese (ja_JP)", "value": "ja_JP"},
            {"name": "Kabyle (kab_DZ)", "value": "kab_DZ"},
            {"name": "Kannada (kn_IN)", "value": "kn_IN"},
            {"name": "Korean (ko_KR)", "value": "ko_KR"},
            {"name": "Kölsch/Ripuarian (ksh_DE)", "value": "ksh_DE"},
            {"name": "Latin (la_VA)", "value": "la_VA"},
            {"name": "Latvian (lv_LV)", "value": "lv_LV"},
            {"name": "Limburgish (li_LI)", "value": "li_LI"},
            {"name": "Lithuanian (lt_LT)", "value": "lt_LT"},
            {"name": "Low German (nds_DE)", "value": "nds_DE"},
            {"name": "Luxembourgish (lb_LU)", "value": "lb_LU"},
            {"name": "Macedonian (mk_MK)", "value": "mk_MK"},
            {"name": "Malay (ms_MY)", "value": "ms_MY"},
            {"name": "Maltese (mt_MT)", "value": "mt_MT"},
            {"name": "Manx (gv_IM)", "value": "gv_IM"},
            {"name": "Māori (mi_NZ)", "value": "mi_NZ"},
            {"name": "Mohawk (moh_US)", "value": "moh_US"},
            {"name": "Mongolian (mn_MN)", "value": "mn_MN"},
            {"name": "Northern Sami (sme)", "value": "sme"},
            {"name": "Norwegian Bokmål (no_NO)", "value": "no_NO"},
            {"name": "Norwegian Nynorsk (nn_NO)", "value": "nn_NO"},
            {"name": "Nuu-chah-nulth (nuk)", "value": "nuk"},
            {"name": "Occitan (oc_FR)", "value": "oc_FR"},
            {"name": "Ojibwe (oj_CA)", "value": "oj_CA"},
            {"name": "Persian (fa_IR)", "value": "fa_IR"},
            {"name": "Polish (pl_PL)", "value": "pl_PL"},
            {"name": "Portuguese Portugal (pt_PT)", "value": "pt_PT"},
            {"name": "Portuguese Brazil (pt_BR)", "value": "pt_BR"},
            {"name": "Romanian (ro_RO)", "value": "ro_RO"},
            {"name": "Russian (ru_RU)", "value": "ru_RU"},
            {"name": "Scottish Gaelic (gd_GB)", "value": "gd_GB"},
            {"name": "Serbian (sr_SP)", "value": "sr_SP"},
            {"name": "Slovak (sk_SK)", "value": "sk_SK"},
            {"name": "Slovenian (sl_SI)", "value": "sl_SI"},
            {"name": "Somali (so_SO)", "value": "so_SO"},
            {"name": "Spanish Spain (es_ES)", "value": "es_ES"},
            {"name": "Spanish Argentina (es_AR)", "value": "es_AR"},
            {"name": "Spanish Chile (es_CL)", "value": "es_CL"},
            {"name": "Spanish Mexico (es_MX)", "value": "es_MX"},
            {"name": "Spanish Uruguay (es_UY)", "value": "es_UY"},
            {"name": "Spanish Venezuela (es_VE)", "value": "es_VE"},
            {"name": "Swedish (sv_SE)", "value": "sv_SE"},
            {"name": "Thai (th_TH)", "value": "th_TH"},
            {"name": "Turkish (tr_TR)", "value": "tr_TR"},
            {"name": "Ukrainian (uk_UA)", "value": "uk_UA"},
            {"name": "Vietnamese (vi_VN)", "value": "vi_VN"},
            {"name": "Welsh (cy_GB)", "value": "cy_GB"},
        ]

        language_names = {option["value"]: option["name"] for option in language_options}

        mods_path = questionary.text(
            "Path to mods folder:", default=os.path.join(os.getcwd(), "mods"), style=QUESTIONARY_STYLE
        ).ask()

        if mods_path is None:
            sys.exit(0)

        if not mods_path:
            console.print("[bold red]Path is required. Exiting.[/bold red]")
            sys.exit(1)

        if not os.path.exists(mods_path):
            console.print(f"[bold red]Path '{mods_path}' does not exist. Exiting.[/bold red]")
            sys.exit(1)

        mods_path = os.path.abspath(mods_path)

        config_source = config_data.get("source", "en_US")
        default_source = next(
            (option for option in language_options if option["value"] == config_source), language_options[0]
        )

        source_lang = questionary.select(
            "Source language:",
            choices=language_options,
            default=default_source,
            instruction="(Use ↑↓ and Enter, or type to search)",
            style=QUESTIONARY_STYLE,
            use_jk_keys=False,
            use_search_filter=True,
        ).ask()

        if source_lang is None:
            sys.exit(0)

        target_language_options = [option for option in language_options if option["value"] != source_lang]

        config_target = config_data.get("target", "")
        default_target = next(
            (option for option in target_language_options if option["value"] == config_target),
            target_language_options[0],
        )

        target_lang = questionary.select(
            "Target language:",
            choices=target_language_options,
            default=default_target,
            instruction="(Use ↑↓ and Enter, or type to search)",
            style=QUESTIONARY_STYLE,
            use_jk_keys=False,
            use_search_filter=True,
        ).ask()

        if target_lang is None:
            sys.exit(0)

        providers = [
            ("google", "Google Translate (Free)", "Always available"),
            ("openai", "OpenAI (GPT-4o-mini)", "OPENAI_API_KEY"),
            ("anthropic", "Anthropic Claude", "ANTHROPIC_API_KEY"),
            ("gemini", "Google Gemini", "GEMINI_API_KEY"),
            ("ollama", "Ollama (Local)", "OLLAMA_API_BASE"),
            ("openaicompatible", "OpenAI-Compatible (Custom)", "OPENAICOMPATIBLE_API_KEY + BASE_URL"),
        ]

        translation_choices = []
        for provider_key, label, requirement in providers:
            available, status_msg = check_provider_available(provider_key)
            if available:
                translation_choices.append({"name": f"{label} ✅ ({status_msg})", "value": provider_key})
            else:
                translation_choices.append(
                    {"name": f"{label} ❌ ({status_msg})", "value": f"{provider_key}_unavailable"}
                )

        config_provider = config_data.get("provider", "")
        default_translation = translation_choices[0]
        if config_provider:
            matching = next((c for c in translation_choices if c["value"] == config_provider), None)
            if matching:
                default_translation = matching

        translation_method = questionary.select(
            "Choose translation method:",
            choices=translation_choices,
            default=default_translation,
            instruction="(Use ↑↓ and Enter)",
            style=QUESTIONARY_STYLE,
            use_jk_keys=False,
        ).ask()

        if translation_method is None:
            sys.exit(0)

        if translation_method.endswith("_unavailable"):
            provider_name = translation_method.replace("_unavailable", "")
            _, status = check_provider_available(provider_name)
            console.print(f"\n[bold yellow]{provider_name.capitalize()} Setup Required[/bold yellow]")
            console.print(f"Status: {status}")
            console.print("\nFalling back to Google Translate...\n")
            translation_method = "google"

        config_output = config_data.get("output", "")
        default_output_choice = "replace"
        if config_output:
            default_output_choice = "new_folder"

        output_choice = questionary.select(
            "Where to save translated mods?",
            choices=[
                {"name": "Replace original mods", "value": "replace"},
                {"name": "Save to a different folder", "value": "new_folder"},
            ],
            default={"name": "Save to a different folder", "value": "new_folder"}
            if default_output_choice == "new_folder"
            else {"name": "Replace original mods", "value": "replace"},
            instruction="(Use ↑↓ and Enter, or type to search)",
            style=QUESTIONARY_STYLE,
            use_jk_keys=False,
            use_search_filter=True,
        ).ask()

        if output_choice is None:
            sys.exit(0)

        output_path = mods_path
        if output_choice == "new_folder":
            default_output = (
                config_output if config_output else os.path.join(os.path.dirname(mods_path), "translated_mods")
            )
            output_path = questionary.text("Output folder path:", default=default_output, style=QUESTIONARY_STYLE).ask()

            if output_path is None:
                sys.exit(0)

            os.makedirs(output_path, exist_ok=True)

        os.system("cls" if os.name == "nt" else "clear")

        console.print("\n[bold]Please confirm your choices:[/bold]")

        confirmation_table = Table(show_header=False, box=box.SIMPLE)
        confirmation_table.add_column("Parameter", style="secondary")
        confirmation_table.add_column("Value", style="primary")

        confirmation_table.add_row("Mods path", mods_path)
        confirmation_table.add_row("Source language", language_names.get(source_lang, source_lang))
        confirmation_table.add_row("Target language", language_names.get(target_lang, target_lang))
        confirmation_table.add_row("Translation method", translation_method.capitalize())
        confirmation_table.add_row("Output path", output_path)

        console.print(confirmation_table)
        console.print()

        confirmed = questionary.confirm(
            "Continue with these settings?",
            default=True,
            style=QUESTIONARY_STYLE,
        ).ask()

        if confirmed is None or not confirmed:
            sys.exit(0)

        os.system("cls" if os.name == "nt" else "clear")

        return {
            "path": mods_path,
            "source": source_lang,
            "target": target_lang,
            "output": output_path,
            "provider": translation_method,
        }
    except KeyboardInterrupt:
        sys.exit(0)


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def _build_mod_choice(mod: ModInfo) -> str:
    size = _format_size(mod.size_bytes)
    if mod.has_lang_files:
        mc_info = f", {mod.mcfunction_count} mcfunc" if mod.mcfunction_count else ""
        return f"{mod.name}  [{mod.lang_file_count} files{mc_info}, ~{mod.estimated_entries} entries, {size}]"
    return f"{mod.name}  [no translatable content, {size}]"


def select_mods(mods: list[ModInfo]) -> list[str]:
    if not mods:
        console.print("[bold yellow]No JAR files found in the mods folder.[/bold yellow]")
        console.print()
        input("Press Enter to exit...")
        sys.exit(0)

    translatable = [m for m in mods if m.has_lang_files]
    if not translatable:
        console.print("[bold yellow]No translatable mods found. All mods lack language files.[/bold yellow]")
        console.print()
        input("Press Enter to exit...")
        sys.exit(0)

    total = len(translatable)
    mode = questionary.select(
        f"Found {len(mods)} JAR(s), {total} with translatable content. How to proceed?",
        choices=[
            {"name": f"Translate all {total} mods", "value": "all"},
            {"name": "Select individually", "value": "select"},
        ],
        style=QUESTIONARY_STYLE,
    ).ask()

    if mode is None:
        sys.exit(0)

    if mode == "all":
        return [m.name for m in translatable]

    choices = []
    for mod in mods:
        choices.append(
            questionary.Choice(
                title=_build_mod_choice(mod),
                value=mod.name,
                checked=False,
            )
        )

    selected = questionary.checkbox(
        "Select mods to translate (Space to toggle, Enter to confirm):",
        choices=choices,
        style=QUESTIONARY_STYLE,
    ).ask()

    if selected is None:
        sys.exit(0)

    return list(selected) if isinstance(selected, list) else []


def _render_rich_summary(console: Console, stats: OverallStats, output_path: str) -> None:
    table = Table(title=None, box=box.SIMPLE, header_style="bold")
    table.add_column("Mod", style="white", no_wrap=True)
    table.add_column("Entries", justify="right", style="bright_black")
    table.add_column("Files", justify="right", style="bright_black")
    table.add_column("Time", justify="right", style="bright_black")

    for m in stats.mods:
        status = " [SKIPPED]" if m.skipped else ""
        time_s = f"{m.duration_ms / 1000:.1f}s"
        table.add_row(m.name[:35] + status, str(m.total_entries), str(len(m.files)), time_s)

    table.add_section()
    total_time = f"{stats.total_duration_ms / 1000:.1f}s"
    table.add_row(
        "TOTAL",
        str(stats.total_entries),
        str(sum(len(m.files) for m in stats.mods)),
        total_time,
        style="bold",
    )

    provider_text = Text.assemble(
        ("  Provider: ", "bright_black"),
        (stats.provider, "white"),
        ("  |  ", "bright_black"),
        ("Source → Target: ", "bright_black"),
        (f"{stats.source_lang} → {stats.target_lang}", "white"),
    )

    fail_style = "bold yellow" if stats.failed_entries > 0 else "white"
    fail_text = Text.assemble(
        ("  Failed: ", "bright_black"),
        (f"{stats.failed_entries} entries", fail_style),
    )

    console.print()
    console.print(table)
    console.print(provider_text)
    console.print(fail_text)


def run_translation(params: dict[str, Any], selected_mods: list[str]) -> None:
    live_log_lines: list[str] = []
    console_handler_id: int | None = None
    live_sink_id: int | None = None

    try:
        debug = params.get("debug", False)
        console_level = "DEBUG" if debug else "INFO"
        setup_logging(console_level=console_level)

        console_handler_id = None
        for hid, handler in logger._core.handlers.items():  # type: ignore[attr-defined]
            if getattr(handler, "_sink", None) is sys.stderr:
                console_handler_id = hid
                break

        class Args(argparse.Namespace):
            def __init__(self, **kwargs: Any):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        args = Args(**params)

        reporter = ProgressReporter()
        live_stats: dict[str, Any] = {
            "phase": "Initializing...",
            "mod_name": "",
            "file_path": "",
            "mods_done": 0,
            "mods_total": 0,
            "entries_done": 0,
            "entries_total": 0,
        }

        def _on_progress(event: str, **kw: Any) -> None:
            if event == "title":
                live_stats["phase"] = kw.get("text", "")
            elif event == "mod_start":
                live_stats["mod_name"] = kw.get("mod_name", "")
                live_stats["file_path"] = ""
            elif event == "mod_file_start":
                live_stats["file_path"] = kw.get("file_path", "")
            elif event == "mod_complete":
                live_stats["mods_done"] += 1
                live_stats["mod_name"] = ""
            elif event == "overall_progress":
                live_stats["mods_done"] = kw.get("completed_mods", live_stats["mods_done"])
                live_stats["mods_total"] = kw.get("total_mods", live_stats["mods_total"])
                live_stats["entries_done"] = kw.get("completed_entries", live_stats["entries_done"])
                live_stats["entries_total"] = kw.get("total_entries", live_stats["entries_total"])
            elif event == "repack_progress":
                live_stats["phase"] = f"Repacking: {kw.get('name', '')} ({kw.get('current', 0)}/{kw.get('total', 0)})"
            elif event in ("scan_start", "scan_progress"):
                live_stats["phase"] = f"Scanning mods: {kw.get('current', 0)}/{kw.get('total', 0)}"

        reporter.subscribe(_on_progress)

        def _build_progress_renderable() -> Table:
            t = Table.grid()
            t.add_column()

            phase_color = "bold yellow"
            if "Repacking" in live_stats["phase"]:
                phase_color = "bold green"
            elif "Translating" in live_stats["phase"] or live_stats["mod_name"]:
                phase_color = "bold red"

            t.add_row(Text(live_stats["phase"], style=phase_color))

            if live_stats["mod_name"]:
                t.add_row(Text("  Mod: ", style="white")
                          + Text(live_stats["mod_name"], style="white"))
            if live_stats["file_path"]:
                short_path = live_stats["file_path"]
                if len(short_path) > 60:
                    short_path = "..." + short_path[-57:]
                t.add_row(Text(f"  File: {short_path}", style="bright_black"))

            mod_progress = f"Mod {live_stats['mods_done']}/{live_stats['mods_total']}"
            entry_progress = f"Entries {live_stats['entries_done']}/{live_stats['entries_total']}"
            if live_stats["entries_total"] > 0:
                pct = live_stats["entries_done"] / live_stats["entries_total"] * 100
                bar_width = 30
                filled = int(bar_width * live_stats["entries_done"] / live_stats["entries_total"])
                bar = "█" * filled + "░" * (bar_width - filled)
                t.add_row(Text(f"  {entry_progress} [{bar}] {pct:.0f}%", style="bright_black"))
            if live_stats["mods_total"] > 0:
                t.add_row(Text(f"  {mod_progress}", style="bright_black"))

            if live_log_lines:
                t.add_row(Text("─" * 40, style="bright_black"))
                for line in live_log_lines:
                    t.add_row(Text(f"  {line}", style="bright_black", overflow="crop"))

            return t

        live = Live(_build_progress_renderable(), console=console, refresh_per_second=4, transient=False)

        if console_handler_id is not None:
            logger.remove(console_handler_id)

        def _live_sink(message: Any) -> None:
            line = str(message).rstrip("\n")
            live_log_lines.append(line)
            if len(live_log_lines) > 3:
                live_log_lines.pop(0)

        live_sink_id = logger.add(_live_sink, level=console_level, format="{time:HH:mm:ss} {message}")

        try:
            with live:
                reporter.report_title("Starting translation...")

                try:
                    stats = handle_translate_command(args, return_stats=True, reporter=reporter)
                except KeyboardInterrupt:
                    sys.exit(0)

            if stats:
                _render_rich_summary(console, stats, params.get("output", "./translated_mods"))

            success_message = "[bold]Translation completed successfully![/bold]\n"
            success_message += f"Translated mods can be found at: [white]{params['output']}[/white]"

            console.print(
                Panel(success_message, title="Success", border_style="green", title_align="center", box=box.DOUBLE)
            )

        finally:
            if live_sink_id is not None:
                logger.remove(live_sink_id)
            logger.add(
                sys.stderr,
                level=console_level,
                format="{time:HH:mm:ss} | {level: <8} | {message}",
                colorize=True,
            )

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        console.print(
            Panel(f"[bold]{str(e)}[/bold]", title="Error", border_style="red", title_align="center", box=box.DOUBLE)
        )
        console.print_exception()


def main(debug: bool = False) -> None:
    """Main entry point for the console app."""
    try:
        display_title()

        try:
            from deep_translator import GoogleTranslator  # noqa: F401
        except ImportError:
            console.print(
                Panel(
                    "[bold]deep_translator package is required for translation.[/bold]\n"
                    "Please install it with: [cyan]pip install deep_translator[/cyan]",
                    title="Missing Dependency",
                    border_style="red",
                    title_align="center",
                    box=box.DOUBLE,
                )
            )
            console.print()
            input("Press Enter to exit...")
            return

        params = get_user_input(load_config(config_path) if (config_path := find_config_file("./mods")) else None)

        if params.get("provider") != "google":
            from ..core.provider_check import check_provider_available

            available, status = check_provider_available(params["provider"])
            if not available:
                console.print(
                    Panel(
                        f"[bold]{params['provider'].capitalize()} not available: {status}[/bold]",
                        title="Provider Setup Required",
                        border_style="red",
                        title_align="center",
                        box=box.DOUBLE,
                    )
                )
                console.print()
                input("Press Enter to exit...")
                return

        console.print("[bold]Scanning mods...[/bold]")
        scanner = ModScanner(params["path"])
        mods = scanner.discover_mods()

        selected_mods = select_mods(mods)

        if not selected_mods:
            console.print("[bold yellow]No mods selected. Exiting.[/bold yellow]")
            console.print()
            input("Press Enter to exit...")
            return

        params["debug"] = debug
        params["selected_mods"] = selected_mods
        run_translation(params, selected_mods)

        console.print()
        input("Press Enter to exit...")

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        console.print(
            Panel(f"[bold]{str(e)}[/bold]", title="Error", border_style="red", title_align="center", box=box.DOUBLE)
        )
        console.print_exception()

        console.print()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
