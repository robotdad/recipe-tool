# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, executes the specified recipe, and handles top-level error reporting.

## Core Requirements

1. Provide a command-line interface for executing recipes
2. Parse arguments for recipe path and context values
3. Initialize the logging system
4. Create the context with command-line supplied values
5. Execute the specified recipe with proper error handling
6. Follow minimal design with clear user-facing error messages

## Implementation Considerations

- Use argparse for command-line argument parsing
- Initialize logging early in execution flow
- Parse context values from key=value pairs
- Create a clean context for recipe execution
- Keep the main function focused on orchestration
- Provide meaningful exit codes and error messages

## Component Dependencies

The Main component depends on:

1. **Context** - Creates the Context object with CLI-supplied values
2. **Executor** - Uses RecipeExecutor to run the specified recipe
   - **IMPORTANT** - Must be imported with the full path to avoid circular imports
   - Example: `from recipe_executor.executor import RecipeExecutor`
3. **Logger** - Uses init_logger to set up the logging system

## Error Handling

- Validate command-line arguments
- Provide clear error messages for missing or invalid recipe files
- Handle context parsing errors gracefully
- Log all errors before exiting
- Use appropriate exit codes for different error conditions

## Future Considerations

1. Support for environment variable configuration
2. Interactive mode or REPL
3. Support for directory-based recipes
4. Plugin system for extending functionality
