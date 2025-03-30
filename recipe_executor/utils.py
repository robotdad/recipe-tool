from context import Context
from liquid import Template


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template. It should provide artifacts via the as_dict() method.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    try:
        # Convert all context values to strings to ensure safe template rendering
        context_data = {key: str(value) for key, value in context.as_dict().items()}

        # Create a Liquid template from the provided text
        template = Template(text)

        # Render the template with the stringified context data
        return template.render(**context_data)
    except Exception as e:
        raise ValueError(f"Error rendering template: {e}") from e
