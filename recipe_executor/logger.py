import logging
import os
import sys


def init_logger(log_dir: str, use_file_handlers: bool = True) -> logging.Logger:
    """
    Initialize and return the main logger.

    This logger logs to stdout and optionally to separate file handlers for debug, info, and error levels.

    Args:
        log_dir (str): Directory where log files will be stored.
        use_file_handlers (bool): Whether to add file handlers. Defaults to True.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger("recipe_executor")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Clear any existing handlers to avoid duplicate logs.
    if logger.hasHandlers():
        logger.handlers.clear()

    # Stream handler for stdout (info level and above)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if use_file_handlers:
        os.makedirs(log_dir, exist_ok=True)

        def create_file_handler(filename: str, level: int) -> logging.FileHandler:
            file_path = os.path.join(log_dir, filename)
            handler = logging.FileHandler(file_path, mode="w")
            handler.setLevel(level)
            handler.setFormatter(formatter)
            return handler

        logger.addHandler(create_file_handler("debug.log", logging.DEBUG))
        logger.addHandler(create_file_handler("info.log", logging.INFO))
        logger.addHandler(create_file_handler("error.log", logging.ERROR))

    return logger
