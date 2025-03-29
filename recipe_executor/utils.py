from context import Context
from liquid import Template


def render_template(text: str, context: Context) -> str:
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

    template = Template(text)
    return template.render(**context.as_dict())
