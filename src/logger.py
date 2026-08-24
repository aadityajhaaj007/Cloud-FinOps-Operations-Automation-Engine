import logging
from pathlib import Path


LOGGER_NAME = "finops_pipeline"
DEFAULT_LOG_FILE = "logs/finops_pipeline.log"


def setup_logger(
    log_file=DEFAULT_LOG_FILE
):
    """
    Configure the FinOps pipeline logger.

    Logs are written to:
    1. Console
    2. logs/finops_pipeline.log

    The logger is protected against duplicate handlers.
    """

    log_path = Path(log_file)

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(
        LOGGER_NAME
    )

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    # Prevent duplicate handlers when the
    # logger is initialized multiple times.
    if logger.handlers:
        return logger

    # ========================================
    # Log format
    # ========================================

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )

    # ========================================
    # File handler
    # ========================================

    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8"
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        formatter
    )

    # ========================================
    # Console handler
    # ========================================

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.INFO
    )

    console_handler.setFormatter(
        formatter
    )

    # ========================================
    # Register handlers
    # ========================================

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    return logger


def get_logger():
    """
    Return the existing FinOps logger.

    If the logger has not been configured yet,
    initialize it automatically.
    """

    logger = logging.getLogger(
        LOGGER_NAME
    )

    if not logger.handlers:
        logger = setup_logger()

    return logger