# Main Component Usage

## Command-Line Interface

The Recipe Executor is used from the command line like this:

```bash
# Basic usage
python -m recipe_executor.main recipes/my_recipe.json

# With custom log directory
python -m recipe_executor.main recipes/my_recipe.json --log-dir custom_logs

# With context values
python -m recipe_executor.main recipes/my_recipe.json --context key1=value1 --context key2=value2
```

## Command-Line Arguments

The Main component supports these arguments:

1. `recipe_path` (required positional): Path to the recipe file to execute
2. `--log-dir` (optional): Directory for log files (default: "logs")
3. `--context` (optional, multiple): Context values as key=value pairs

## Context Parsing

The Main component parses context values from the command line:

```python
def parse_context(context_args: List[str]) -> Dict[str, Any]:
    """
    Parse context key=value pairs from the CLI arguments.

    Args:
        context_args: List of context arguments as key=value strings.

    Returns:
        A dictionary with key-value pairs parsed from the arguments.

    Raises:
        ValueError: If any argument does not follow key=value format.
    """
```

For example:

```bash
# These arguments:
--context name=John --context age=30 --context active=true

# Will create this context:
{
    "name": "John",
    "age": "30",
    "active": "true"
}
```

## Main Execution Flow

The main function serves as the entry point:

```python
def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    """
```

Implementation details:

```python
def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Executes a recipe with additional context information."
    )
    parser.add_argument("recipe_path", help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Additional context values as key=value pairs")
    args = parser.parse_args()

    # Parse context key=value pairs
    try:
        cli_context = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Initialize logging
    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Create the Context object with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        # Execute the recipe
        executor = RecipeExecutor()
        executor.execute(args.recipe_path, context, logger=logger)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.exit(1)
```

## Programmatic Usage

While typically used as a command-line tool, the Main component can be used programmatically:

```python
from recipe_executor.main import parse_context
from recipe_executor.context import Context
from recipe_executor.executor import RecipeExecutor
from recipe_executor.logger import init_logger

# Parse context from strings
context_args = ["name=Project", "version=1.0"]
context_dict = parse_context(context_args)

# Initialize logger
logger = init_logger("logs")

# Create context and execute recipe
context = Context(artifacts=context_dict)
executor = RecipeExecutor()
executor.execute("recipes/my_recipe.json", context, logger=logger)
```

## Exit Codes

The Main component uses these exit codes:

- `0`: Successful execution
- `1`: Error during execution (parsing errors, missing files, execution failures)

## Error Messages

Error messages are written to stderr and the log files:

```python
# Context parsing error
sys.stderr.write(f"Context Error: {str(e)}\n")

# Recipe execution error
logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
```

## Important Notes

1. The recipe path must point to a valid recipe file
2. Context values from the command line are stored as strings
3. Logs are written to the specified log directory
4. All steps in the recipe share the same context
5. The executable exits with non-zero status on error
