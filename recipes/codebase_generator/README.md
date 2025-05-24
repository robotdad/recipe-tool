# Codebase Generator

Recipes for generating code from blueprints - demonstrates self-generating capability.

## Quick Examples

```bash
# Generate all Recipe Executor code
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json

# Generate specific component
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   component_id=steps.llm_generate
```

See blueprint files in `blueprints/recipe_executor/` for component definitions.
