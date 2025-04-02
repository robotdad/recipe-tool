from typing import Any

from liquid import Template
# Depending on the version of the liquid library, errors might originate from different submodules.
# For now, we catch all exceptions during rendering.

from recipe_executor.context import Context


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
        # Retrieve artifacts from the context and convert all values to strings to avoid type issues
        context_dict = context.as_dict()
        safe_context = { key: str(value) for key, value in context_dict.items() }
        
        # Create the Liquid template and render it using the safe_context
        template = Template(text)
        rendered = template.render(**safe_context)
        return rendered

    except Exception as e:
        # Wrap and raise a ValueError with additional context
        raise ValueError(f"Error rendering template: {e}") from e
