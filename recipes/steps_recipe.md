# Step Implementations Module Recipe

This recipe generates the Python modules for the step implementations used in the recipe_executor tool. It will produce the following files under `output/recipe_executor/steps/`:

1. **base.py:** Defines the BaseStep and StepConfig classes.
2. **read_file.py:** Implements the ReadFileStep and its configuration.
3. **write_files.py:** Implements the WriteFileStep and its configuration.
4. **generate_llm.py:** Implements the GenerateWithLLMStep and its configuration.
5. **execute_recipe.py:** Implements the ExecuteRecipeStep and its configuration.
6. **registry.py:** Initializes a STEP_REGISTRY dictionary mapping step type strings to their corresponding classes.
7. \***\*init**.py:\*\* Imports all step modules to expose them as a package.

```json
[
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'base.py' that defines an abstract BaseStep class (with a generic type for configuration) and a base StepConfig class. The BaseStep should require an __init__ method that accepts a configuration and logger, and define an abstract execute(context) method. Include type annotations and clear docstrings.",
      "target_artifact": "generated_steps_base"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_steps_base",
    "root": "output/recipe_executor/steps"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'read_file.py' that implements the ReadFileStep. Include a ReadFileConfig class with fields for the file path and artifact name, and a ReadFileStep class that reads a file (using templating for the path) and stores its content in the context. Ensure proper logging, type annotations, and docstrings.",
      "target_artifact": "generated_read_file_step"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_read_file_step",
    "root": "output/recipe_executor/steps"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'write_files.py' that implements the WriteFileStep. Include a WriteFilesConfig class with fields for the artifact key and output root. The WriteFileStep should retrieve a FileGenerationResult or list of FileSpec objects from the context and write each file to disk (using templated file paths). Include proper error handling, type annotations, and docstrings.",
      "target_artifact": "generated_write_files_step"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_write_files_step",
    "root": "output/recipe_executor/steps"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'generate_llm.py' that implements the GenerateWithLLMStep. Include a GenerateLLMConfig class with fields for the prompt and artifact name. The GenerateWithLLMStep should call an LLM to generate code based on the provided prompt, store the structured result in the context, and log the process. Include type annotations and clear docstrings.",
      "target_artifact": "generated_generate_llm_step"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_generate_llm_step",
    "root": "output/recipe_executor/steps"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'execute_recipe.py' that implements the ExecuteRecipeStep. Include an ExecuteRecipeConfig class with a field for the recipe path, and an ExecuteRecipeStep class that reads a sub-recipe from the specified path, verifies its existence, and executes it using the RecipeExecutor with the current context. Include logging, proper error handling, type annotations, and docstrings.",
      "target_artifact": "generated_execute_recipe_step"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_execute_recipe_step",
    "root": "output/recipe_executor/steps"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'registry.py' that initializes a STEP_REGISTRY dictionary. This module should import the step classes (ReadFileStep, WriteFileStep, GenerateWithLLMStep, ExecuteRecipeStep) from their respective modules and map each corresponding step type string to its class.",
      "target_artifact": "generated_steps_registry"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_steps_registry",
    "root": "output/recipe_executor/steps"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "code_generation_wrapper_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module with the filename '__init__.py' (do not include any directory paths in the output) for the steps package. This file should import all step modules so that the STEP_REGISTRY is properly populated and the package is initialized correctly.",
      "target_artifact": "generated_steps_init"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_steps_init",
    "root": "output/recipe_executor/steps"
  }
]
```
