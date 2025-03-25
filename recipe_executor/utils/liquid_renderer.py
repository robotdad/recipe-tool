"""Liquid template rendering utilities."""

import json
from typing import Any, Dict

from liquid.environment import Environment
from liquid.exceptions import LiquidSyntaxError

from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("template")


class LiquidRenderer:
    """Liquid template renderer for recipe executor."""

    def __init__(self):
        """Initialize the liquid template renderer with custom filters."""
        self.env = Environment()
        self._register_custom_filters()

    def _register_custom_filters(self):
        """Register custom filters for liquid templates."""
        # Register a filter for pretty printing JSON
        def json_pretty(value):
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=2, default=str)
            return str(value)

        # Register a filter for length or size
        def length(value):
            if hasattr(value, '__len__'):
                return len(value)
            return 0

        # Register a filter for safe type conversion
        def to_str(value):
            return str(value) if value is not None else ""

        # Register the filters
        self.env.add_filter('json_pretty', json_pretty)
        self.env.add_filter('length', length)
        self.env.add_filter('to_str', to_str)

    def render(self, template_str: str, variables: Dict[str, Any]) -> str:
        """
        Render a liquid template string with the given variables.

        Args:
            template_str: The template string to render
            variables: Dictionary of variables to use in rendering

        Returns:
            Rendered string

        Raises:
            ValueError: If there's an error in the template syntax
        """
        try:
            # Pre-process variables to handle any non-serializable objects
            processed_vars = self._prepare_variables(variables)

            # Parse and render the template
            template = self.env.parse(template_str)
            result = template.render(**processed_vars)
            return result
        except LiquidSyntaxError as e:
            error_msg = f"Liquid syntax error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error rendering liquid template: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _prepare_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare variables for liquid template rendering.
        Converts complex objects to simpler representations.

        Args:
            variables: Dictionary of variables to prepare

        Returns:
            Processed variables dictionary
        """
        result = {}

        for key, value in variables.items():
            # Handle None values
            if value is None:
                result[key] = ""
            # Handle non-serializable objects by converting to string
            elif hasattr(value, '__dict__') and not isinstance(value, (dict, list)):
                # For custom objects, convert to a dictionary
                try:
                    if hasattr(value, 'model_dump'):
                        # For Pydantic models
                        result[key] = value.model_dump()
                    else:
                        # For other objects with __dict__
                        result[key] = vars(value)
                except:
                    # If all else fails, convert to string
                    result[key] = str(value)
            else:
                # For regular types, use as is
                result[key] = value

        return result


# Singleton instance for global use
_renderer = None


def get_renderer() -> LiquidRenderer:
    """Get the global liquid renderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = LiquidRenderer()
    return _renderer


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """
    Render a liquid template with the given variables.

    This is a convenience function for using the singleton renderer.

    Args:
        template: Template string
        variables: Variables to use in rendering

    Returns:
        Rendered string
    """
    return get_renderer().render(template, variables)