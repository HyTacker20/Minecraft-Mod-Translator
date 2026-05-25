import os
from pathlib import Path

from app.logging_config import get_logger, setup_logging
from loguru import logger


class TestLoggingConfig:
    def test_setup_logging_creates_file_handler(self, tmp_path: Path):
        log_dir = str(tmp_path / "app_logs")
        setup_logging(log_dir=log_dir, console_level="WARNING")
        log_file = os.path.join(log_dir, "translation.log")
        assert os.path.exists(log_dir)
        Path(log_file).write_text("test", encoding="utf-8")
        assert os.path.exists(log_file)

    def test_get_logger_returns_loguru_logger(self):
        lg = get_logger()
        assert lg is logger

    def test_setup_logging_clears_previous_handlers(self, tmp_path: Path):
        log_dir = str(tmp_path / "logs_clear")
        setup_logging(log_dir=log_dir, console_level="INFO")
        initial_count = len(logger._core.handlers)
        setup_logging(log_dir=log_dir, console_level="ERROR")
        assert len(logger._core.handlers) == initial_count
