# Context & Configuration Module Recipe

```json
[
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/code_generation_recipe.md",
    "context_overrides": {
      "scenario_prompt": "A Python module that defines a Context dataclass for managing artifacts and configuration. The Context dataclass must:\n\n- Implement __init__ with optional 'artifacts' and 'config' dictionaries (set as empty if not provided).\n- Support dict-like access via __getitem__ and __setitem__ methods for the artifacts.\n- Include a get(key, default=None) method to safely retrieve artifact values.\n- Provide an as_dict() method that returns a shallow copy of the artifacts dictionary.\n- Implement __iter__, __len__, and keys() methods for iterating over and checking the number of artifacts",
      "target_artifact": "generated_context_module"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_context_module",
    "root": "output/recipe_executor"
  }
]
```
