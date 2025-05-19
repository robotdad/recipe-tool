"""Test configuration for recipe-executor-app."""

import os
import pytest
import logging
from unittest.mock import patch


def pytest_configure(config):
    """Configure pytest environment before running tests."""
    # Set environment variable to disable Gradio analytics
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    
    # Disable all logging during tests
    logging.basicConfig(level=logging.CRITICAL)
    
    # Configure specific loggers to be silent
    for logger_name in [
        "gradio", "gradio.analytics", "httpx", "threading", 
        "asyncio", "websockets", "matplotlib"
    ]:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
        logging.getLogger(logger_name).propagate = False


@pytest.fixture(scope="session", autouse=True)
def disable_gradio_analytics():
    """Disable Gradio's analytics during testing to avoid the logging error."""
    # Patch the gradio analytics version_check function to do nothing
    with patch('gradio.analytics.version_check'):
        yield
    
    # Also ensure we catch and swallow I/O errors in logging handlers
    for handler in logging.getLogger().handlers:
        try:
            handler.flush()
        except Exception:
            pass