# Executor Component Usage

## Importing

```python
from recipe_executor.executor import RecipeExecutor
```

## Basic Usage

The RecipeExecutor has a single primary method: `execute()`. This method loads and runs a recipe with a given context:

```python
# Method signature
def execute(
    self,
    recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]],
    context: Context,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Execute a recipe with the given context.

    Args:
        recipe: Recipe to execute, can be a file path, JSON string, or dict
        context: Context instance to use for execution
        logger: Optional logger to use, creates a default one if not provided

    Raises:
        ValueError: If recipe format is invalid or step execution fails
        TypeError: If recipe type is not supported
    """
```

Examples:

```python
# Create context and executor
context = Context()
executor = RecipeExecutor()

# Execute a recipe from a file
executor.execute("path/to/recipe.json", context)

# Or from a JSON string
json_string = '{"steps": [{"type": "read_file", "path": "example.txt", "artifact": "content"}]}'
executor.execute(json_string, context)

# Or from a dictionary
recipe_dict: Dict[str, List[Dict[str, Any]]] = {
    "steps": [
        {"type": "read_file", "path": "example.txt", "artifact": "content"}
    ]
}
executor.execute(recipe_dict, context)
```

## Recipe Formats

The executor supports three recipe input formats:

### 1. File Path

```python
# JSON file
executor.execute("recipes/my_recipe.json", context)

# Markdown file with JSON code block
executor.execute("recipes/my_recipe.md", context)
```

### 2. JSON String

```python
json_string = '''
{
  "steps": [
    {
      "type": "read_file",
      "path": "input.txt",
      "artifact": "input_content"
    },
    {
      "type": "generate",
      "prompt": "Generate based on: {{input_content}}",
      "model": "openai:o3-mini",
      "artifact": "generation_result"
    }
  ]
}
'''
executor.execute(json_string, context)
```

### 3. Dictionary

```python
recipe: Dict[str, List[Dict[str, Any]]] = {
    "steps": [
        {
            "type": "read_file",
            "path": "input.txt",
            "artifact": "input_content"
        }
    ]
}
executor.execute(recipe, context)
```

## Custom Logging

You can provide a custom logger to the executor:

```python
import logging

logger = logging.getLogger("my_custom_logger")
logger.setLevel(logging.DEBUG)

executor.execute(recipe, context, logger=logger)
```

## Error Handling

The executor provides detailed error messages:

```python
try:
    executor.execute(recipe, context)
except ValueError as e:
    print(f"Recipe execution failed: {e}")
except TypeError as e:
    print(f"Unsupported recipe type: {e}")
```

## Integration with Steps

The executor uses the Step Registry to instantiate steps based on their type:

```python
# Each step in a recipe must have a "type" field:
step: Dict[str, Any] = {
    "type": "read_file",  # Must match a key in STEP_REGISTRY
    "path": "input.txt",
    "artifact": "content"
}
```

Steps are looked up in the STEP_REGISTRY by their type name:

```python
# Simplified example of what happens inside the executor
from recipe_executor.steps.registry import STEP_REGISTRY

step_type = step["type"]
step_class = STEP_REGISTRY[step_type]
step_instance = step_class(step, logger)
step_instance.execute(context)
```

## Important Notes

1. Recipes must contain valid steps with "type" fields
2. All step types must be registered in the STEP_REGISTRY before use
3. Each step receives the same context object
4. Execution is sequential by default
