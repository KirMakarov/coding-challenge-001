import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def get_logger(name: str):
    """Returns a logger instance with the specified name."""
    return logging.getLogger(name)
