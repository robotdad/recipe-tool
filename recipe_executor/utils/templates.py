"""
Utility functions for rendering Liquid templates using context data.

This module provides a `render_template` function that uses the Python Liquid templating engine
to render strings with variables sourced from a context object implementing ContextProtocol.
Custom filters (e.g., snakecase) and extra filters (json, datetime) are enabled via the environment.
"""
import re
from typing import Any

from liquid import Environment
from liquid.exceptions import LiquidError

# Import ContextProtocol inside the module to avoid circular dependencies
from recipe_executor.protocols import ContextProtocol

__all__ = ["render_template"]

# Create a module‐level Liquid environment with extra filters enabled
_env = Environment(autoescape=False, extra=True)

# Register a custom `snakecase` filter

def _snakecase(value: Any) -> str:
    """
    Convert a string to snake_case.

    Non-alphanumeric characters are replaced with underscores, camelCase
    boundaries are separated, and result is lowercased.
    """
    s = str(value)
    # Replace spaces and dashes with underscores
    s = re.sub(r"[\s\-]+", "_", s)
    # Insert underscore before capital letters preceded by lowercase/digits
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)
    # Lowercase the string
    s = s.lower()
    # Remove any remaining invalid characters
    s = re.sub(r"[^a-z0-9_]", "", s)
    # Collapse multiple underscores
    s = re.sub(r"__+", "_", s)
    # Strip leading/trailing underscores
    return s.strip("_")

_env.filters["snakecase"] = _snakecase


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Python Liquid template using the provided context.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering,
                    includes details about the template and context.
    """
    try:
        # Parse and render the template with all context values
        template = _env.from_string(text)
        rendered = template.render(**context.dict())
        return rendered
    except LiquidError as e:
        # Liquid-specific errors
        raise ValueError(
            f"Liquid template rendering error: {e}. "
            f"Template: {text!r}. Context: {context.dict()!r}"
        )
    except Exception as e:
        # Generic errors
        raise ValueError(
            f"Error rendering template: {e}. "
            f"Template: {text!r}. Context: {context.dict()!r}"
        )