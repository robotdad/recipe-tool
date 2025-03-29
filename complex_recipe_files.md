Scanning patterns: ['recipes/complex_recipe.md', 'recipes/sub_recipe.md', 'specs/main_spec.txt', 'specs/auxiliary_spec.txt', 'specs/sub_spec.txt']
Excluding patterns: ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc']
Including patterns: []
Found 5 files.

=== File: recipes/complex_recipe.md ===
# Complex Code Generation Recipe

This recipe demonstrates a multi-step workflow that:

1. Reads two specification files.
2. Uses an LLM step to generate a comprehensive Python module that integrates both core and auxiliary functionalities.
3. Writes the generated module to disk.
4. Executes a sub-recipe to generate an additional utility module.

```json
[
  {
    "type": "read_file",
    "path": "specs/main_spec.txt",
    "artifact": "main_spec"
  },
  {
    "type": "read_file",
    "path": "specs/auxiliary_spec.txt",
    "artifact": "aux_spec"
  },
  {
    "type": "generate",
    "prompt": "Using the following main specification:\n\n{main_spec}\n\nand the auxiliary details:\n\n{aux_spec}\n\nGenerate a comprehensive Python module that contains a main function printing 'Hello from Main!' and an auxiliary function returning a greeting. Return a JSON object with keys 'files' (a list of file objects with 'path' and 'content') and 'commentary'.",
    "artifact": "generated_module"
  },
  {
    "type": "write_file",
    "artifact": "generated_module",
    "root": "output/main_module"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/sub_recipe.md"
  }
]
```



=== File: recipes/sub_recipe.md ===
# Sub-Recipe: Utility Module Generation

This sub-recipe generates a Python utility module based on additional requirements.

```json
[
  {
    "type": "read_file",
    "path": "specs/sub_spec.txt",
    "artifact": "sub_spec"
  },
  {
    "type": "generate",
    "prompt": "Based on the following sub-specification:\n\n{sub_spec}\n\nGenerate a Python utility module that defines a function called get_logger (which returns a configured logger) and another function process_data(data) that simply returns data unchanged. Return a JSON object with 'files' (a list of file objects with 'path' and 'content') and 'commentary'.",
    "artifact": "generated_util"
  },
  {
    "type": "write_file",
    "artifact": "generated_util",
    "root": "output/utility_module"
  }
]
```



=== File: specs/auxiliary_spec.txt ===
This auxiliary specification provides additional details for extra features. Include a helper function that returns a greeting string.



=== File: specs/main_spec.txt ===
This is the primary specification for the main module. It should describe the core functionality, including a function that prints "Hello from Main!".



=== File: specs/sub_spec.txt ===
This sub-specification outlines requirements for a utility module. It should provide utility functions for logging and data processing.



