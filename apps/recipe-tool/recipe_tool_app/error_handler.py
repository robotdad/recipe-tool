"""Error handling utilities for the Recipe Tool app."""

import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional

# Initialize logger
logger = logging.getLogger(__name__)


def format_error_response(error: Exception, function_name: str) -> Dict[str, Any]:
    """Format an error response based on the type of operation.

    Args:
        error: The exception that was raised
        function_name: The name of the function that raised the exception

    Returns:
        Dict[str, Any]: Formatted error response
    """
    error_msg = f"### Error\n\n```\n{str(error)}\n```"

    # Use appropriate result format based on function name
    if "execute" in function_name:
        return {"formatted_results": error_msg, "raw_json": "{}", "debug_context": {"error": str(error)}}
    else:
        return {"recipe_json": "", "structure_preview": error_msg, "debug_context": {"error": str(error)}}


def log_error_with_context(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with additional context information.

    Args:
        logger: Logger instance
        error: The exception that was raised
        context: Optional context dictionary
    """
    logger.error(f"Error: {error}", exc_info=True)

    if context:
        # Log key context variables that might help debugging
        log_context = {k: v for k, v in context.items() if k in ["recipe_root", "output_root", "input", "target_file"]}
        logger.error(f"Context at error time: {log_context}")


def handle_recipe_error(func: Callable) -> Callable:
    """Decorator to standardize error handling for recipe operations.

    Args:
        func: The function to decorate

    Returns:
        Callable: Decorated function
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            log_error_with_context(logger, e)
            return format_error_response(e, func.__name__)

    # Handle non-async functions
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return asyncio.run(async_wrapper(*args, **kwargs))
        except Exception as e:
            log_error_with_context(logger, e)
            return format_error_response(e, func.__name__)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def is_recipe_execution_error(error: Exception) -> bool:
    """Check if an error is related to recipe execution.

    Args:
        error: The exception to check

    Returns:
        bool: True if the error is related to recipe execution
    """
    error_str = str(error).lower()

    # Check for common recipe execution error patterns
    execution_patterns = ["recipe", "executor", "step", "context", "llm", "generate", "invalid json", "missing field"]

    return any(pattern in error_str for pattern in execution_patterns)


def create_user_friendly_error(error: Exception) -> str:
    """Create a user-friendly error message.

    Args:
        error: The exception

    Returns:
        str: User-friendly error message
    """
    error_str = str(error)

    # Check for specific error types and provide friendly messages
    if "FileNotFoundError" in error_str:
        return "File not found. Please check that the file exists and the path is correct."
    elif "JSONDecodeError" in error_str:
        return "Invalid JSON format. Please check your recipe JSON syntax."
    elif "PermissionError" in error_str:
        return "Permission denied. Please check file permissions."
    elif is_recipe_execution_error(error):
        return f"Recipe execution error: {error_str}"
    else:
        return f"An error occurred: {error_str}"


class RecipeToolError(Exception):
    """Base exception class for Recipe Tool errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize with message and optional context.

        Args:
            message: Error message
            context: Optional context dictionary
        """
        super().__init__(message)
        self.context = context or {}

    def get_formatted_response(self) -> Dict[str, Any]:
        """Get formatted error response.

        Returns:
            Dict[str, Any]: Formatted error response
        """
        error_msg = f"### Error\n\n```\n{str(self)}\n```"
        return {"formatted_results": error_msg, "raw_json": "{}", "debug_context": {"error": str(self), **self.context}}


class RecipeNotFoundError(RecipeToolError):
    """Exception raised when a recipe file cannot be found."""

    pass


class RecipeParsingError(RecipeToolError):
    """Exception raised when a recipe cannot be parsed."""

    pass


class RecipeExecutionError(RecipeToolError):
    """Exception raised when a recipe execution fails."""

    pass
