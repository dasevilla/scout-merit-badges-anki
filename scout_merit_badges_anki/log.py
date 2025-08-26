"""Logging setup for scout-merit-badges-anki."""

import logging
import sys
from typing import ClassVar


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to log levels."""

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        if sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(quiet: bool = False, verbose: int = 0) -> logging.Logger:
    """Setup logging with appropriate level and formatting.

    Args:
        quiet: If True, only show errors
        verbose: Verbosity level (0=info, 1=debug, 2+=debug with more detail)

    Returns:
        Configured logger
    """
    logger = logging.getLogger("scout_merit_badges_anki")

    # Clear any existing handlers
    logger.handlers.clear()

    # Set level based on flags
    if quiet:
        level = logging.ERROR
    elif verbose >= 1:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.setLevel(level)

    # Create handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter
    if verbose >= 2:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        fmt = "%(levelname)s: %(message)s"

    formatter = ColoredFormatter(fmt)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger() -> logging.Logger:
    """Get the configured logger."""
    return logging.getLogger("scout_merit_badges_anki")
