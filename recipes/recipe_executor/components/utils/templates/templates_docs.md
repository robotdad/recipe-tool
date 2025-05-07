# Template Utility Component Usage

## Importing

```python
from recipe_executor.utils.templates import render_template
```

## Template Rendering

The Templates utility component provides a `render_template` function that renders [Python Liquid](https://jg-rp.github.io/liquid/) templates using values from a context object implementing the ContextProtocol:

```python
def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Python Liquid template using the provided context.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.utils.templates import render_template

# Create a context with some values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template string using the context
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Python Liquid syntax. Here are some common features:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains nested dictionaries)
template = "Author: {{book.author}}"
```

### Conditionals

```python
template = "{% if user_count > 0 %}Users: {{user_count}}{% else %}No users{% endif %}"
```

### Loops

```python
template = "{% for item in items %}Item: {{item}}{% endfor %}"
```

## Custom Filters

In addition to the [built-in Python Liquid filters](https://jg-rp.github.io/liquid/filter_reference/), we have provided some additional custom filters for specific use cases:

- `snakecase`: Converts a string to snake_case.
  - Syntax: `<string> | snakecase`
  - Example: `{{ "Hello World" | snakecase }}` results in `hello_world`.

The following "extra filters" are also available:

- `json`: Return the input object serialized to a JSON (JavaScript Object Notation) string.
  - Syntax: `<object> | json[: <indent>]`
  - Example: `{{ {"name": "John", "age": 30} | json: indent: 2 }}` results in:
    ```json
    {
      "name": "John",
      "age": 30
    }
    ```
- `datetime`: Date and time formatting. Return the input datetime formatted according to the current locale. If `dt` is a `datetime.datetime` object `datetime.datetime(2007, 4, 1, 15, 30)`.
  - Syntax: `<object> | datetime[: <format>]`
  - Valid formats:
    - `short`: Short date format.
    - `medium`: Medium date format.
    - `long`: Long date format.
    - `full`: Full date format.
    - Custom formats using [CLDR](https://cldr.unicode.org/translation/date-time/date-time-patterns) format (e.g., `MMM d, y`).
  - Example: `{{ dt | datetime }}` results in `Apr 1, 2007, 3:30:00 PM` (default format).
  - Example: `{{ dt | datetime: format: 'MMM d, y' }}` results in `2007-04-01`.
  - Example: `{{ dt | datetime: format: 'short' }}` results in `01/04/2007, 03:30`.
