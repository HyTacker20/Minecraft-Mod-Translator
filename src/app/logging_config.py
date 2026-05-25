import os
import sys

from loguru import logger


def setup_logging(log_dir: str = "logs", console_level: str = "INFO") -> None:
    logger.remove()
    os.makedirs(log_dir, exist_ok=True)

    logger.add(
        os.path.join(log_dir, "translation.log"),
        rotation="5 MB",
        retention=3,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8",
    )

    logger.add(
        sys.stderr,
        level=console_level,
        format="{time:HH:mm:ss} | {level: <8} | {message}",
        colorize=True,
    )


def get_logger():
    return logger
