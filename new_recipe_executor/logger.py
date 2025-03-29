import logging
import os


def init_logger(log_dir: str):
    logger = logging.getLogger('RecipeExecutor')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Debug log handler
    debug_handler = logging.FileHandler(os.path.join(log_dir, 'debug.log'))
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # Info log handler
    info_handler = logging.FileHandler(os.path.join(log_dir, 'info.log'))
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)

    # Error log handler
    error_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger
