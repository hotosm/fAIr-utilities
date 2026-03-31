import logging

from rich.logging import RichHandler
from rich.progress import track as rich_track


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(show_path=False, markup=True)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def track(sequence, description: str = "Processing..."):
    return rich_track(sequence, description=description)
