import logging
import os
from pathlib import Path

from app.logging_config import get_logger, setup_logging


class TestLoggingConfig:
    def test_setup_logging_creates_handlers(self, tmp_path: Path):
        log_dir = str(tmp_path / "app_logs")
        logger = setup_logging(log_dir=log_dir, console_level=logging.WARNING)
        assert len(logger.handlers) >= 2
        log_file = os.path.join(log_dir, "translation.log")
        assert os.path.exists(log_dir)
        os.makedirs(log_dir, exist_ok=True)
        Path(log_file).write_text("test", encoding="utf-8")
        assert os.path.exists(log_file)

    def test_get_logger_returns_logger(self):
        lg = get_logger()
        assert isinstance(lg, logging.Logger)

    def test_setup_logging_console_level(self, tmp_path: Path):
        log_dir = str(tmp_path / "logs2")
        logger = setup_logging(log_dir=log_dir, console_level=logging.ERROR)
        from logging.handlers import RotatingFileHandler
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)]
        assert len(console_handlers) == 1
        assert console_handlers[0].level == logging.ERROR
