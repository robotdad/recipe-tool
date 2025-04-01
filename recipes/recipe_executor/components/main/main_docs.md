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

The Main component parses context values from the command line. For example:

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
