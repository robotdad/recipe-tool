# Logging & Templating Module Recipe

This recipe generates two modules for the recipe_executor tool:

1. **Logging Module:** Defines a function `init_logger` in `output/recipe_executor/logger.py`. This function should:

   - Create a logs directory if it doesn't exist.
   - Clear old log files.
   - Configure a logger with a stream handler (writing to stdout) and file handlers for debug, info, and error logs.
   - Use a consistent formatter and include detailed docstrings and type annotations.

2. **Templating Module:** Defines a function `render_template` in `output/recipe_executor/utils.py`. This function should:
   - Accept a text string (to be rendered as a Liquid template) and a context object.
   - Convert the context to a dictionary using its `as_dict()` method.
   - Render the text template and return the rendered string.
   - Include proper error handling, docstrings, and type annotations.

```json
[
  {
    "type": "generate",
    "prompt": "Generate a Python module for logging configuration named 'logger.py'. This module should define a function 'init_logger' that takes a 'log_dir' argument (defaulting to 'logs'). The function should create the log directory if it does not exist, clear existing log files, and configure a logger with a stream handler (to stdout) and file handlers for 'debug.log', 'info.log', and 'error.log'. The logger should use a consistent formatter with timestamps and log levels, and the module should include proper type annotations and docstrings.",
    "artifact": "generated_logger_module"
  },
  {
    "type": "write_file",
    "artifact": "generated_logger_module",
    "root": "output/recipe_executor"
  },
  {
    "type": "generate",
    "prompt": "Generate a Python module for templating named 'utils.py'. This module should define a function 'render_template' that takes a text string and a context object. It should render the text as a Liquid template using the context's 'as_dict()' method to provide variables. Include proper type annotations, error handling, and a clear docstring explaining its usage.",
    "artifact": "generated_templating_module"
  },
  {
    "type": "write_file",
    "artifact": "generated_templating_module",
    "root": "output/recipe_executor"
  }
]
```
