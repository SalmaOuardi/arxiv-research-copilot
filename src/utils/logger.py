"""Logging configuration module.

Sets up structured logging for the application with configurable
log levels and formats.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "arxiv_copilot",
    level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Logger name (typically the application or module name).
        level: Log level string ("DEBUG", "INFO", "WARNING", "ERROR").
            Defaults to LOG_LEVEL env var or "INFO".
        log_file: Optional path to a log file. If provided, logs are
            written to both console and file.

    Returns:
        Configured logger instance.

    Example:
        >>> logger = setup_logger("arxiv_copilot", level="DEBUG")
        >>> logger.info("Application started")
    """
    import os

    log_level = level or os.getenv("LOG_LEVEL", "INFO")

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Module-level convenience logger
logger = setup_logger()
