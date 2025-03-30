# Logger Component Specification

## Purpose

The Logger component provides a consistent logging interface for the Recipe Executor system. It initializes and configures logging, writes logs to appropriate files, and ensures that all components can log messages at different severity levels.

## Core Requirements

The Logger component should:

1. Initialize a logger that writes to both stdout and log files
2. Support different log levels (DEBUG, INFO, ERROR)
3. Create separate log files for each level
4. Clear existing logs on each run to prevent unbounded growth
5. Provide a consistent log format with timestamps and log levels
6. Create log directories if they don't exist
7. Follow a minimal design approach with sensible defaults

## Component Structure

The Logger component should consist of a single module with an `init_logger` function:

```python
def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files.

    Returns:
        logging.Logger: Configured logger instance.
    """
```

## Log Configuration

The Logger should configure the following:

1. A root logger named "RecipeExecutor" with level set to DEBUG
2. A console handler that writes INFO and above messages to stdout
3. File handlers for different log levels:
   - debug.log: All messages (DEBUG and above)
   - info.log: INFO messages and above
   - error.log: ERROR messages and above
4. A consistent log format: `%(asctime)s [%(levelname)s] %(message)s`

## File Management

The Logger should:

1. Create the log directory if it doesn't exist
2. Clear (truncate) existing log files at the start of each run
3. Create separate files for each log level

## Integration Points

The Logger component integrates with:

1. **Main**: The main entry point will initialize the logger
2. **Executor**: The executor will use the logger for execution status
3. **Steps**: All steps will receive and use the logger for their operations

## Future Considerations

1. Log rotation for long-running processes
2. Remote logging options (e.g., syslog, ELK)
3. Customizable log formats
4. Support for structured logging
