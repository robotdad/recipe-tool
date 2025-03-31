# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Component Dependencies

The ExecuteRecipeStep component depends on:

- **Steps Base** - Extends BaseStep with a specific config type
- **Context** - Shares context between main recipe and sub-recipes
- **Executor** - Uses RecipeExecutor to run the sub-recipe
- **Utils** - Uses render_template for dynamic content resolution

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include sub-recipe path in error messages for debugging

## Future Considerations

- Support for recipe content passed directly in configuration
- Context isolation options for sub-recipes
- Result mapping from sub-recipes back to parent recipes
- Conditional sub-recipe execution
