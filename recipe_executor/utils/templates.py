"""
Templates utility component for rendering Liquid templates with context.
"""

from typing import Dict
import liquid
from liquid.exceptions import LiquidError

from recipe_executor.protocols import ContextProtocol


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    # Prepare the context values as strings
    values: Dict[str, str] = {}
    try:
        # Attempt to get a full dict representation of the context
        try:
            raw_context = context.dict()
        except Exception:
            # Fallback: iterate keys
            raw_context = {key: context[key] for key in context.keys()}

        for key, val in raw_context.items():
            # Convert None to empty string, otherwise cast to str
            values[key] = "" if val is None else str(val)

        # Create a new Liquid environment and render the template
        env = liquid.Environment()
        template = env.from_string(text)
        return template.render(**values)

    except LiquidError as le:
        raise ValueError(
            f"Liquid template rendering error for template {text!r} "
            f"with context {values!r}: {le}"
        ) from le
    except Exception as e:
        raise ValueError(
            f"Error rendering template {text!r} with context {values!r}: {e}"
        ) from e
