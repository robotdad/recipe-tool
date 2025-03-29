from context import Context
from liquid import Template


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.
    """
    template = Template(text)
    # Convert all context values to strings
    str_context = {k: str(v) for k, v in context.as_dict().items()}
    return template.render(**str_context)
