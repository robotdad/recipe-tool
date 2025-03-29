from typing import Any, Dict

from liquid import Template


def render_template(text: str, context: Dict[str, Any]) -> str:
    """
    Render the given text as a Liquid template using the provided context.

    If the context object has an 'as_dict' method, it will be used to convert
    the context to a plain dictionary.

    Args:
        text (str): The template text to render.
        context (Dict[str, Any]): The context for rendering the template.

    Returns:
        str: The rendered text.
    """
    # Always convert context if it has an as_dict() method.
    if hasattr(context, "as_dict") and callable(context.as_dict):
        context = context.as_dict()
    template = Template(text)
    return template.render(**context)
