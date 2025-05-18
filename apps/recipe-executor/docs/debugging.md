# Debugging Guide for Recipe Executor App

This guide provides information on debugging issues with the Recipe Executor app, focusing on common problems and troubleshooting techniques.

## Table of Contents

1. [Debug Features](#debug-features)
2. [Common Issues](#common-issues)
3. [Logging Configuration](#logging-configuration)
4. [Recipe Format Issues](#recipe-format-issues)
5. [Context Variable Problems](#context-variable-problems)
6. [Advanced Troubleshooting](#advanced-troubleshooting)

## Debug Features

The Recipe Executor app includes several debugging features:

### Debug Context Tab

Both the "Execute Recipe" and "Create Recipe" tabs include a "Debug Context" tab that shows the complete context object after execution, including all variables, artifacts, and generated content.

To use this feature:

1. Execute a recipe or create a new recipe
2. Click on the "Debug Context" tab in the output area
3. Examine the JSON content to see the complete state of the context

### Enhanced Logging

The app includes detailed logging with configurable levels. Logs include:

- Recipe execution steps
- Context variables at key points
- File operations
- Error details with stack traces

### Error Reporting

When an error occurs, the app provides:

- Descriptive error messages in the UI
- Detailed error information in the logs
- Context state at the time of the error

## Common Issues

### Recipe Not Showing After Creation

**Symptoms**: Recipe is created (file exists in output directory) but doesn't appear in the UI.

**Possible Causes**:

1. Format of `generated_recipe` in context doesn't match expected format
2. Non-serializable objects in the context
3. Invalid JSON format in the recipe

**Solution**:

1. Check the Debug Context tab to see the structure of `generated_recipe`
2. Look at the app logs for detailed error messages
3. Verify the output file format by opening it directly

### Context Variable Parsing Issues

**Symptoms**: Context variables not being applied correctly.

**Possible Causes**:

1. Incorrect format (should be `key1=value1,key2=value2`)
2. Special characters in values that need escaping
3. Variables not being passed to the executor

**Solution**:

1. Check the Debug Context tab to see which variables are set
2. Try simpler variable names and values to isolate the issue
3. Look for logging messages about context initialization

### File Path Problems

**Symptoms**: Recipe execution fails with file not found errors.

**Possible Causes**:

1. Relative paths not resolving correctly
2. Context root variables not set correctly
3. Permissions issues on target directories

**Solution**:

1. Use the Debug Context tab to check the values of `recipe_root`, `ai_context_root`, and `output_root`
2. Try using absolute paths in your recipe
3. Check logs for file operation errors

## Logging Configuration

The app uses Python's built-in logging module with additional formatting. Logs are written to the location specified in the configuration.

### Setting Log Level

The log level can be set in several ways:

1. In the code: `logger.setLevel("DEBUG")` (currently set)
2. Environment variable: `RECIPE_APP_LOG_LEVEL=DEBUG`
3. Command line: `python -m recipe_executor_app.app --debug`

### Log Locations

Logs are stored in:

1. Console output when running the app directly
2. Log file in the configured log directory (default: `../../logs`)

### Viewing Logs

To view logs while the app is running:

```bash
# Follow the log file
tail -f ../../logs/recipe_executor_app.log
```

## Recipe Format Issues

The Recipe Executor app expects recipes in a specific JSON format. Common format issues include:

### Generated Recipe Format

When creating recipes, the `generated_recipe` field in the context can have several formats:

1. **List format** (most common):

   ```json
   "generated_recipe": [
     {
       "path": "file_name.json",
       "content": "{\n  \"steps\": [...]\n}"
     }
   ]
   ```

2. **String format**:

   ```json
   "generated_recipe": "{\n  \"steps\": [...]\n}"
   ```

3. **Dictionary format**:
   ```json
   "generated_recipe": {
     "content": "{\n  \"steps\": [...]\n}"
   }
   ```

The app has been updated to handle all these formats.

### JSON Validation

The app performs JSON validation on recipes. Issues that can occur:

1. Malformed JSON syntax
2. Missing required fields (`steps` array)
3. Invalid step types or configurations

If JSON validation fails, check:

1. The Debug Context tab for the raw recipe content
2. The logs for specific JSON parsing errors
3. The recipe file directly using a JSON validator

## Context Variable Problems

Context variables allow passing data to recipes, but can cause issues.

### Standard Context Variables

The app automatically adds these context variables:

- `recipe_root`: Path to the recipes directory
- `ai_context_root`: Path to the AI context directory
- `output_root`: Path to the output directory

If these variables are incorrect, check:

1. The app's working directory
2. Environment variables or configuration settings
3. The Debug Context tab to see the actual values

### Complex Value Serialization

Context variables with complex values (objects, nested structures) may not serialize properly.

- For complex values, consider encoding them as JSON strings
- Use the Debug Context tab to verify the value was set correctly
- Check logs for serialization errors

## Advanced Troubleshooting

For more advanced issues:

### Debugging Recipe Execution Flow

To debug the execution flow of a recipe:

1. Add `set_context` steps with debug information at key points
2. Include descriptive comments in your recipe
3. Add explicit error-handling steps

### Recipe Creator Debugging

When debugging recipe creation:

1. Examine the recipe creator recipe itself
2. Check the LLM prompt and response
3. Verify the model and parameters being used

### Code Inspection

For the most difficult issues, inspect the code:

1. The main app logic is in: `recipe-tool/apps/recipe-executor/recipe_executor_app/app.py`
2. Recipe execution logic is in: `recipe-tool/recipe_executor/`
3. MCP server configuration is in the app configuration files

### Checking Component Versions

Version mismatches can cause issues:

1. Check the Recipe Executor version
2. Verify Gradio version compatibility
3. Confirm Python environment version
