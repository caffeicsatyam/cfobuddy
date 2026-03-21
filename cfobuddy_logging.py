import logging
import os


_CONFIGURED = False


def configure_logging() -> logging.Logger:
    """Configure app logging once and return the app logger."""
    global _CONFIGURED

    logger = logging.getLogger("cfobuddy")
    if _CONFIGURED:
        return logger

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    _CONFIGURED = True
    return logger
