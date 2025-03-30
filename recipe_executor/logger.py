import logging
import os
import sys


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Create log directory if it does not exist
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Create a logger with a consistent name
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Set lowest level to capture all messages

    # Remove existing handlers, if any, to avoid duplicate logs in re-initializations
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Setup file handlers and ensure logs are cleared (mode="w")
    try:
        # Debug file: logs everything (DEBUG and above)
        debug_file = os.path.join(log_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_file, mode="w")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        # Info file: logs info and above
        info_file = os.path.join(log_dir, "info.log")
        info_handler = logging.FileHandler(info_file, mode="w")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        # Error file: logs error and above
        error_file = os.path.join(log_dir, "error.log")
        error_handler = logging.FileHandler(error_file, mode="w")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
    except Exception as e:
        raise Exception(f"Failed to set up file handlers: {e}")

    # Console handler: logs info and above to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger
