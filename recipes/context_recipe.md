# Context & Configuration Module Recipe

This recipe generates the Python module that defines the `Context` class. The `Context` class should:

- Hold two dictionaries: one for `artifacts` and one for `config`.
- Provide dict-like access to artifacts using:
  - `__getitem__` and `__setitem__`
  - A safe `get` method with a default value.
  - An `as_dict` method to return a shallow copy of artifacts.
  - `__iter__`, `__len__`, and `keys` methods to support iteration and length checking.
- Include proper type annotations and docstrings.

The generated output must be a JSON object with two keys:

- `files`: a list of file objects (each with a `path` and `content` field).
- `commentary`: a string with additional comments on the generation.

```json
[
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module that defines a Context class for managing artifacts and configuration. The Context class must:\n\n- Initialize with optional 'artifacts' and 'config' dictionaries.\n- Support dict-like access via __getitem__ and __setitem__ methods for the artifacts.\n- Include a get(key, default=None) method to safely retrieve artifact values.\n- Provide an as_dict() method that returns a shallow copy of the artifacts dictionary.\n- Implement __iter__, __len__, and keys() methods for iterating over and checking the number of artifacts.\n\nInclude clear type annotations and docstrings. The final output should be a JSON object with two keys: 'files' (a list of file objects with 'path' and 'content') and 'commentary'.",
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
