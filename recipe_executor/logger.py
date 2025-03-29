import logging
import os
import sys


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Clear old handlers to avoid duplicates (useful during dev reloads)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Stream handler for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File handlers
    def add_file_handler(filename: str, level: int):
        path = os.path.join(log_dir, filename)
        with open(path, "w"):  # truncate file
            pass
        handler = logging.FileHandler(path)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    add_file_handler("debug.log", logging.DEBUG)
    add_file_handler("info.log", logging.INFO)
    add_file_handler("error.log", logging.ERROR)

    return logger
