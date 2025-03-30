from typing import Any

from liquid import Template

from recipe_executor.context import Context


def _convert_values_to_str(value: Any) -> Any:
    """
    Recursively convert all values in the provided data structure to strings.

    Args:
        value: The input value, which may be a dict, list, or primitive.

    Returns:
        The data structure with all values converted to strings.
    """
    if isinstance(value, dict):
        return {k: _convert_values_to_str(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_convert_values_to_str(item) for item in value]
    else:
        return str(value)


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    try:
        # Get artifacts from the context and convert all values to strings
        raw_context = context.as_dict()
        str_context = _convert_values_to_str(raw_context)

        # Create and render the Liquid template with the provided context
        template = Template(text)
        rendered_text = template.render(**str_context)
        return rendered_text
    except Exception as e:
        raise ValueError(f"Template rendering failed: {e}") from e
