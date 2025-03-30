# Top-Level Build Tool Recipe: Regenerate Recipe Executor Tool

This recipe coordinates the regeneration of the entire recipe_executor tool by executing the following sub-recipes:

1. **Context & Configuration Module**
2. **Executor Pipeline Module**
3. **Step Implementations Module**
4. **Logging & Templating Module**
5. **LLM Integration Module**

```json
[
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/recipe_executor/context_recipe.md"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/recipe_executor/executor_pipeline_recipe.md"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/recipe_executor/steps_recipe.md"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/recipe_executor/logging_templating_recipe.md"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/recipe_executor/llm_integration_recipe.md"
  }
]
```
