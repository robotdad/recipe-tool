# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building-block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current execution context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow a minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- When processing context overrides
  - Process all **string** values (including those within lists or dictionaries) using the template engine
  - All non-string values in context overrides should be passed as-is
  - String value may contain JSON objects or lists of JSON objects with mixed, escaped quotes, use `ast.literal_eval` to parse them
  - If a string value is a valid JSON object, it should be parsed and passed as a dictionary
  - If a string value is a list of valid JSON objects, it should be parsed and passed as a list of dictionaries
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Implementation Hints

- Import the `Executor` within the `execute` method to avoid circular dependencies

## Logging

- Debug: None
- Info: Log the path of the sub-recipe being executed at both the start and end of execution

## Component Dependencies

### Internal Components

- **Protocols**: Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Interface**: Implements the step execution interface (via the StepProtocol)
- **Context**: Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor**: Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils/Templates**: Uses render_template for dynamic content resolution in paths and context overrides

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include the sub-recipe path in error messages for debugging

## Output Files

- `recipe_executor/steps/execute_recipe.py`
