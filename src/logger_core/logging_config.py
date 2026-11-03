"""
Конфигурация логирования проекта. Этот модуль настраивает систему логирования.
"""

import logging
from pathlib import Path
import os
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

LOGGER_NAME = "app"

_LOG_DIR = Path(os.getenv("LOG_DIR", Path(__file__).resolve().parent.parent / "logs"))
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "app.log"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.handlers:
    console_formatter = ColoredFormatter(
        fmt="%(log_color)s%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )


    file_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)


    file_handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)


    logger.addHandler(console_handler)
    logger.addHandler(file_handler)