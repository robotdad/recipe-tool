from typing import Any

from liquid import Template

from recipe_executor.context import Context


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The Liquid template text to be rendered.
        context (Context): The context containing values for substitution.

    Returns:
        str: The rendered template string.

    Raises:
        ValueError: When there is an error during template rendering.
    """
    try:
        # Retrieve all artifacts from the context as a dictionary.
        # Convert each value to a string to ensure compatibility with the Liquid engine.
        context_dict = context.as_dict()
        safe_context = {key: str(value) for key, value in context_dict.items()}
        
        # Create the Liquid template and render it using the prepared safe context.
        template = Template(text)
        rendered = template.render(**safe_context)
        return rendered
    except Exception as e:
        # Raise a ValueError wrapping the original error with a clear error message.
        raise ValueError(f"Error rendering template: {e}") from e
