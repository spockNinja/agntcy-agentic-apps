import logging
import logging.config
import os
from pathlib import Path
from typing import Dict


def get_log_dir() -> Path:
    """
    Returns the log directory path.

    Ensures the directory exists before returning it.

    Returns:
        Path: The path to the logs directory (app/logs/)
    """
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_log_file() -> Path:
    """
    Returns the log file path.

    Ensures that the file is removed on every startup to keep logs fresh.

    Returns:
        Path: The path to the log file (app/logs/remote_graphs.log)
    """
    log_file = get_log_dir() / "remote_graphs.log"

    # Remove the existing log file on startup
    if log_file.exists():
        log_file.unlink()

    return log_file


def get_log_level() -> str:
    """
    Retrieves the log level from environment variables.

    Defaults to "INFO" if LOG_LEVEL is not set.

    Returns:
        str: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    return os.getenv("LOG_LEVEL", "INFO").upper()


def get_logging_config(log_file: Path, log_level: str) -> Dict:
    """
    Generates the logging configuration dictionary.

    Args:
        log_file (Path): Path to the log file.
        log_level (str): Logging level (DEBUG, INFO, etc.).

    Returns:
        dict: Logging configuration dictionary.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(levelname)s - %(name)s [%(filename)s:%(lineno)d] - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "file": {
                "level": log_level,
                "class": "logging.FileHandler",
                "filename": str(log_file),
                "formatter": "detailed",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "remote_graphs": {  # Keep for compatibility
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {"handlers": ["console", "file"], "level": log_level},
    }


def configure_logging() -> None:
    """
    Configures logging for the FastAPI application.

    - Initializes logging configuration.
    - Removes old log files to ensure clean logs on every restart.
    - Applies logging settings globally.
    """
    log_file = get_log_file()
    log_level = get_log_level()
    logging_config = get_logging_config(log_file, log_level)

    logging.config.dictConfig(logging_config)

    logger = logging.getLogger("app")
    logger.info("Logging is initialized. This should appear in the log file.")
