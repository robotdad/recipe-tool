import logging
import os
import sys
from typing import Optional


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    This function sets up separate handlers for debug, info, and error log files as well
    as a console handler for stdout. Each file is truncated (using mode='w') on each
    run to prevent unbounded growth of log files.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If the log directory cannot be created or log file handlers cannot be initialized.
    """
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all logs at or above DEBUG

    # Remove any existing handlers to ensure a clean configuration
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define the common log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Ensure the log directory exists
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Set up file handlers with mode 'w' to clear previous logs
    try:
        # Debug file handler: logs all messages (DEBUG and above)
        debug_file = os.path.join(log_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_file, mode="w")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)

        # Info file handler: logs INFO and above
        info_file = os.path.join(log_dir, "info.log")
        info_handler = logging.FileHandler(info_file, mode="w")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)

        # Error file handler: logs ERROR and above
        error_file = os.path.join(log_dir, "error.log")
        error_handler = logging.FileHandler(error_file, mode="w")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    except Exception as e:
        raise Exception(f"Failed to initialize file handlers: {e}")

    # Console Handler: logs INFO and above to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    # Example usage of the logger component
    try:
        logger = init_logger()
        logger.debug("Debug message: Detailed info for diagnosing problems")
        logger.info("Info message: Confirmation that things are working as expected")
        logger.warning("Warning message: Something unexpected happened")
        logger.error("Error message: A function could not be performed")
        logger.critical("Critical message: The program may be unable to continue running")
    except Exception as e:
        print(f"Logger initialization failed: {e}")
