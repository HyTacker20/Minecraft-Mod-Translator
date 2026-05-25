import sys
import argparse
from unittest.mock import MagicMock, patch, PropertyMock

from app.commands.command_line import build_argument_parser, main


class TestCommandLineExtended:
    def test_main_no_args_shows_help(self):
        with patch("sys.argv", ["mod-translator"]):
            with patch.object(sys.stdout, "write") as mock_write:
                main()
                mock_write.assert_called()

    def test_main_app_command(self):
        with patch("sys.argv", ["mod-translator", "app"]):
            with patch("app.commands.app.main") as mock_app_main:
                main()
                mock_app_main.assert_called_once()

    def test_main_cli_subcommand(self):
        with patch("sys.argv", ["mod-translator", "cli", "-s", "en_US", "-t", "uk_UA"]):
            with patch("app.commands.command_line.handle_translate_command") as mock_handle:
                main()
                mock_handle.assert_called_once()

    def test_main_error_handling(self):
        with patch("sys.argv", ["mod-translator", "cli", "-s", "en_US"]):
            with patch("app.commands.command_line.handle_translate_command", side_effect=Exception("test error")):
                with patch("app.commands.command_line.logger") as mock_logger:
                    main()
                    mock_logger.exception.assert_called_once()

    def test_backward_compatibility(self):
        with patch("sys.argv", ["mod-translator", "-s", "en_US", "-t", "uk_UA"]):
            with patch("app.commands.command_line.handle_translate_command") as mock_handle:
                main()
                mock_handle.assert_called_once()
                call_args = mock_handle.call_args[0][0]
                assert call_args.source == "en_US"
                assert call_args.target == "uk_UA"

    def test_parser_subparsers_exist(self):
        parser = build_argument_parser()
        with patch("sys.argv", ["mod-translator", "cli", "-s", "en_US"]):
            args = parser.parse_args(["cli", "-s", "en_US"])
            assert args.command == "cli"
