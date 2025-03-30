# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler building blocks, following the LEGO-inspired approach to recipe construction.

## Core Requirements

1. Execute sub-recipes from a specified file path
2. Share the current context with sub-recipes
3. Support context overrides for sub-recipe execution
4. Apply template rendering to recipe paths and context overrides
5. Include appropriate logging for sub-recipe execution
6. Follow minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Component Dependencies

The ExecuteRecipeStep component depends on:

1. **Steps Base** - Extends BaseStep with a specific config type
2. **Context** - Shares context between main recipe and sub-recipes
3. **Executor** - Uses RecipeExecutor to run the sub-recipe
4. **Utils** - Uses render_template for dynamic content resolution

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include sub-recipe path in error messages for debugging

## Future Considerations

1. Support for recipe content passed directly in configuration
2. Context isolation options for sub-recipes
3. Result mapping from sub-recipes back to parent recipes
4. Conditional sub-recipe execution
