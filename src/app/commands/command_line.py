"""
Main command-line interface for Mod Translator.
"""

import logging
import sys
from argparse import ArgumentParser

from ..commands.translate import add_translate_arguments, handle_translate_command

logger = logging.getLogger("mod_translator")


def build_argument_parser() -> ArgumentParser:
    """
    Build the argument parser for the command-line interface.

    Returns:
        ArgumentParser object
    """
    parser = ArgumentParser(prog="mod-translator")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create the CLI command (default)
    cli_parser = subparsers.add_parser("cli", help="Use traditional command-line arguments")
    add_translate_arguments(cli_parser)

    # Create the app command
    app_parser = subparsers.add_parser("app", help="Launch interactive form interface")
    app_parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging to console")

    # For backward compatibility, also add translate arguments to the main parser
    add_translate_arguments(parser)

    return parser


def main() -> None:
    """Main entry point for the command-line interface."""
    try:
        parser = build_argument_parser()

        # If no arguments provided, show help
        if len(sys.argv) == 1:
            parser.print_help()
            return

        args = parser.parse_args()

        # Handle different commands
        if getattr(args, "command", None) == "app":
            # Import app module here to avoid circular imports
            from ..commands.app import main as app_main
            debug = getattr(args, "debug", False)
            app_main(debug=debug)
        else:
            # Default to translate command for backward compatibility
            handle_translate_command(args)
    except Exception as e:
        logger.exception("Error: %s", e)


if __name__ == "__main__":
    main()
