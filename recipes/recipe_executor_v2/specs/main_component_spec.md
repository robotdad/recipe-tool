# Main Component Specification

## Purpose

The Main component serves as the command-line interface (CLI) and entry point for the Recipe Executor system. It parses command-line arguments, sets up logging, initializes context, and launches the executor with the appropriate recipe.

## Core Requirements

The Main component should:

1. Provide a clean CLI interface with argument parsing
2. Support specifying a recipe file path as a required argument
3. Allow optional configuration for log directory
4. Support passing additional context values as key=value pairs
5. Initialize logging with appropriate configuration
6. Create and populate the Context object
7. Instantiate the RecipeExecutor and run the specified recipe
8. Follow a minimal design approach with sensible defaults

## Component Structure

The Main component should consist of a main module with a `main()` function as the entry point:

```python
def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments and calls the core runner function.
    """
```

## Command Line Arguments

The Main component should support the following command-line arguments:

1. `recipe_path` (required): Path to the recipe file to execute
2. `--log-dir` (optional): Directory for log files (default: "logs")
3. `--context` (optional, multiple): Additional context values as key=value pairs

Example usage:

```
python -m recipe_executor.main my_recipe.json --log-dir ./logs --context key1=value1 --context key2=value2
```

## Context Initialization

The Main component should:

1. Parse any `--context` arguments into key-value pairs
2. Initialize a Context object with these values
3. Pass this Context to the RecipeExecutor

## Error Handling

The Main component should:

1. Provide clear error messages for missing or invalid arguments
2. Use try/except blocks as appropriate for graceful error handling
3. Ensure all errors are properly logged

## Integration Points

The Main component integrates with:

1. **Context**: Creates and initializes the Context instance
2. **Executor**: Instantiates and calls the RecipeExecutor
3. **Logger**: Sets up the logging system

## Future Considerations

1. Support for environment variable configuration
2. Interactive mode or REPL
3. Support for recipe directories with auto-discovery
4. Plugin system for adding custom step types
