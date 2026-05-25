import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = "logs", console_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("mod_translator")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)-7s] %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "translation.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s [%(levelname)-7s] %(name)s %(filename)s:%(lineno)d %(message)s")
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger


_logger = logging.getLogger("mod_translator")
_logger.addHandler(logging.NullHandler())


def get_logger() -> logging.Logger:
    return _logger
