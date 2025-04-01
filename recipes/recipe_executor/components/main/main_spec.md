# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, executes the specified recipe, and handles top-level error reporting.

## Core Requirements

- Provide a command-line interface for executing recipes
- Load environment variables from .env files using python-dotenv
  - python-dotenv is already installed as a dependency of the project
- Parse arguments for recipe path and context values
- Initialize the logging system
- Create the context with command-line supplied values
- Execute the specified recipe with proper error handling
- Follow minimal design with clear user-facing error messages

## Implementation Considerations

- Call load_dotenv() early in the main function before any other initialization
- Use argparse for command-line argument parsing
- Initialize logging early in execution flow
- Parse context values from key=value pairs
- Create a clean context for recipe execution
- Keep the main function focused on orchestration
- Provide meaningful exit codes and error messages

## Component Dependencies

The Main component depends on:

- **python-dotenv** - Uses load_dotenv to load environment variables from .env files
- **Context** - Creates the Context object with CLI-supplied values
- **Executor** - Uses RecipeExecutor to run the specified recipe
- **Logger** - Uses init_logger to set up the logging system

## Error Handling

- Validate command-line arguments
- Provide clear error messages for missing or invalid recipe files
- Handle context parsing errors gracefully
- Log all errors before exiting
- Use appropriate exit codes for different error conditions

## Implementation Details

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

## Future Considerations

- Support for environment variable configuration
- Support for directory-based recipes
