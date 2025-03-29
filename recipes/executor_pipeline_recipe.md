# Executor Pipeline Module Recipe

```json
[
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/code_generation_recipe.md",
    "context_overrides": {
      "scenario_prompt": "A Python module that defines a RecipeExecutor class for a recipe execution framework. The class should be able to accept recipes as a file path, JSON string, or dictionary. If the input is a file path, it should read the file and attempt to extract a JSON code block. Do not include literal triple backticks in the output; ensure that the JSON snippet is complete and self-contained. If no code block is found, it should try to parse the entire content as JSON. The recipe data should be either a dict with a 'steps' key or a list of step definitions. The RecipeExecutor should iterate over each step, logging the start and completion of each one. For every step, it should determine the step type, retrieve the corresponding implementation from a step registry, instantiate the step with its configuration, and execute it using a provided context. Include proper type annotations, docstrings, and error handling that logs and re-raises exceptions. Finally, return a JSON object with 'files' (a list of file objects with 'path' and 'content') and 'commentary' (a string with additional comments).",
      "target_artifact": "generated_executor_pipeline_module"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_executor_pipeline_module",
    "root": "output/recipe_executor"
  }
]
```
