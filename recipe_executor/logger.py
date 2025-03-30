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
    # Ensure the log directory exists
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"Failed to create log directory {log_dir}: {e}", file=sys.stderr)
        raise

    # Create a custom logger
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Prevent message propagation to the root logger

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define a consistent log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Configure the console handler (stdout) for INFO level and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Configure file handler for debug.log (DEBUG and above)
    debug_log_path = os.path.join(log_dir, "debug.log")
    try:
        debug_handler = logging.FileHandler(debug_log_path, mode="w")
    except Exception as e:
        print(f"Failed to create debug log file {debug_log_path}: {e}", file=sys.stderr)
        raise
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # Configure file handler for info.log (INFO and above)
    info_log_path = os.path.join(log_dir, "info.log")
    try:
        info_handler = logging.FileHandler(info_log_path, mode="w")
    except Exception as e:
        print(f"Failed to create info log file {info_log_path}: {e}", file=sys.stderr)
        raise
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)

    # Configure file handler for error.log (ERROR and above)
    error_log_path = os.path.join(log_dir, "error.log")
    try:
        error_handler = logging.FileHandler(error_log_path, mode="w")
    except Exception as e:
        print(f"Failed to create error log file {error_log_path}: {e}", file=sys.stderr)
        raise
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger
