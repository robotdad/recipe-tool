# Logging & Templating Module Recipe

```json
[
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/code_generation_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module for logging configuration named 'logger.py'. This module should define a function 'init_logger' that takes a 'log_dir' argument (defaulting to 'logs'). The function should create the log directory if it does not exist, clear existing log files, and configure a logger with a stream handler (to stdout) and file handlers for 'debug.log', 'info.log', and 'error.log'. The logger should use a consistent formatter with timestamps and log levels, and the module should include proper type annotations and docstrings.",
      "target_artifact": "generated_logger_module"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_logger_module",
    "root": "output/recipe_executor"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/code_generation_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module for templating named 'utils.py'. This module should define a function 'render_template' that takes a text string and a context object. It should render the text as a Liquid template using the context's 'as_dict()' method to provide variables. Include proper type annotations, error handling, and a clear docstring explaining its usage.",
      "target_artifact": "generated_templating_module"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_templating_module",
    "root": "output/recipe_executor"
  }
]
```
