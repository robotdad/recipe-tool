# Recipe Executor Logging System

The Recipe Executor includes a comprehensive logging system designed to provide visibility into recipe execution, model interactions, and system events at various detail levels.

## Logging Levels

The logging system supports the standard Python logging levels:

- **DEBUG**: Detailed, verbose information useful for debugging
- **INFO**: General information about the execution flow
- **WARNING**: Issues that should be noted but don't prevent execution
- **ERROR**: Errors that prevent a step or recipe from completing
- **CRITICAL**: Critical issues that require immediate attention

## Log Files

Logs are stored in the `logs/` directory with automatic file rotation to prevent excessive growth:

- **info.log**: Contains INFO level and above messages for general execution flow
- **error.log**: Contains ERROR level and above messages for issue diagnosis
- **debug.log**: Contains DEBUG level and all messages for full execution details

Each log file is limited to 10MB with a rotation of up to 5 backup files.

## Specialized Loggers

The system includes several specialized loggers for different components:

- **app**: Main application logger
- **parser**: Recipe parsing and conversion
- **llm**: LLM interactions, including prompts and responses
- **events**: System events (step execution, validation, etc.)
- **context**: Execution context and variable management
- **execution**: Overall execution flow
- **debug**: Detailed debug information

## LLM Interaction Logging

At the DEBUG level, the system logs:

- Complete LLM prompts with system instructions
- Complete model responses
- Context variables (with sensitive information redacted)
- Message history for conversational interactions

Example of an LLM prompt log:
```
2025-03-24 15:36:42,123 - recipe-executor.llm - DEBUG - LLM PROMPT for step generate_content (model: claude-3-7-sonnet-20250219):
--------------------------------------------------------------------------------
Write a 500-word article about AI safety.
--------------------------------------------------------------------------------
```

## Event Logging

The system logs all execution events, including:

- Recipe start/completion
- Step start/execution/completion
- Validation events
- LLM generation events
- User interaction events

## Usage in Code

You can use the logging system in your code with:

```python
from recipe_executor.utils import logging as log_utils

# Get a logger for a specific component
logger = log_utils.get_logger("my_component")

# Log at different levels
logger.debug("Detailed debug message")
logger.info("Standard information")
logger.warning("Warning about a potential issue")
logger.error("Error message")

# Log LLM interactions
log_utils.log_llm_prompt("claude-3-7-sonnet-20250219", "Write a poem about logging", "step_123")
log_utils.log_llm_response("claude-3-7-sonnet-20250219", "Logs, logs, everywhere...", "step_123")

# Log execution context
log_utils.log_execution_context(variables_dict, "step_123")
```

## Setting Up the Logging System

The logging system is automatically initialized when starting the recipe-executor, but you can adjust the log level:

```bash
python recipe_executor/main.py path/to/recipe.yaml --log-level debug
```

## Log File Rotation and Management

The system automatically:

- Creates a new set of log files for each run
- Rotates log files when they reach 10MB
- Keeps up to 5 backup files for each log
- Creates timestamped backup directories for previous logs