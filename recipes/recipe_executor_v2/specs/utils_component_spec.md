# Utils Component Specification

## Purpose

The Utils component provides utility functions for the Recipe Executor system, primarily focusing on template rendering. It enables steps to use dynamic values from the context in their configuration through a simple templating mechanism.

## Core Requirements

The Utils component should:

1. Provide a template rendering function using the Liquid templating engine
   - The Liquid library is already installed in the environment
   - The component should not include any additional dependencies beyond the Liquid library
2. Support substituting values from the Context into templates
   - `from context import Context`
   - The Context object is a dictionary-like object that contains artifacts and other values
   - The component should use the Context's `as_dict()` method to extract all artifacts
3. Handle all context values by converting them to strings
4. Follow a minimal design approach with focused functionality
5. Ensure template rendering is reliable and error-resistant

## Component Structure

The Utils component should consist of a single module with a `render_template` function:

```python
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
```

## Template Rendering Logic

The template rendering function should:

1. Accept a string template and a Context object
2. Extract all artifacts from the Context using its as_dict() method
3. Convert all values to strings to ensure they can be safely used in templates
4. Use the Liquid template engine to render the template
5. Return the rendered string

## Usage Example

The component should support usage patterns like:

```python
# Example of how template rendering would be used in a step
path = render_template(self.config.path, context)
prompt = render_template(self.config.prompt, context)
```

## Implementation Philosophy

The Utils component should follow these principles:

1. **Ruthless Simplicity**: Provide only what's needed without extra complexity
2. **Direct Library Usage**: Use the Liquid library directly with minimal wrapping
3. **Error Resilience**: Handle edge cases gracefully (e.g., non-string values)

## Integration Points

The Utils component integrates with:

1. **Context**: Uses the Context's as_dict() method to access artifacts
2. **Steps**: All steps use the render_template function for dynamic configuration

## Future Considerations

1. Support for additional template filters or functions
2. Error handling for invalid templates
3. Template caching for performance optimization
4. Support for more complex data types in templates
