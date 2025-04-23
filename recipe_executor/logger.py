import os
import sys
import logging
from typing import Tuple

def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR" (case-insensitive).

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Prepare logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Reset existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create log directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Formatter for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handlers configuration
    paths: Tuple[str, str, str] = (
        os.path.join(log_dir, "debug.log"),
        os.path.join(log_dir, "info.log"),
        os.path.join(log_dir, "error.log"),
    )

    levels = (logging.DEBUG, logging.INFO, logging.ERROR)
    names = ("debug", "info", "error")

    for fname, level, name in zip(paths, levels, names):
        try:
            fh = logging.FileHandler(fname, mode="w", encoding="utf-8")
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            raise Exception(f"Failed to set up {name} log file '{fname}': {e}")

    # Console handler
    lvl_name = stdio_log_level.upper()
    if lvl_name == "WARN":
        lvl_name = "WARNING"
    if lvl_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        lvl_name = "INFO"
    console_level = getattr(logging, lvl_name)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Initialization logs
    logger.debug("Logger initialized: log_dir='%s', stdio_log_level='%s'", log_dir, lvl_name)
    logger.info("Logger initialized successfully")

    return logger
