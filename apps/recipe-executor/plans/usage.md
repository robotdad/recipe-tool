# Recipe Executor App User Guide

This guide explains how to use the Recipe Executor App to execute recipes through a web interface.

## Starting the App

1. Ensure you have installed the Recipe Executor App as described in the [README](../README.md).

2. Start the app:
   ```bash
   cd apps/recipe-executor
   make run
   ```
   
   Or directly with Python:
   ```bash
   python -m recipe_executor_app.app
   ```

3. Open the URL displayed in the terminal (usually something like `http://localhost:7860`) in your web browser.

## Web Interface Overview

The Recipe Executor App interface consists of the following tabs:

1. **Execute Recipe**: The main tab for executing recipes
2. **Examples**: A tab for loading example recipes

### Execute Recipe Tab

The Execute Recipe tab is divided into two sections:

#### Input Section

- **Recipe JSON File**: Upload a recipe JSON file here
- **Recipe JSON**: Alternatively, paste the recipe JSON directly into this text area
- **Context Variables** (in the accordion): Add context variables as key=value pairs, separated by commas

#### Output Section

- **Results**: View the results of the recipe execution in a formatted markdown display
- **Raw Output**: View the raw JSON output from the recipe execution
- **Debug Context**: View the full context variables after recipe execution (useful for debugging)

## Using the App

### Executing a Recipe

1. **Provide a Recipe**:
   - Either upload a recipe JSON file using the "Recipe JSON File" uploader, or
   - Paste the recipe JSON directly into the "Recipe JSON" text area

2. **Add Context Variables** (optional):
   - Open the "Context Variables" accordion
   - Enter context variables as comma-separated key=value pairs
   - Example: `model=gpt-4-1106-preview,input_path=data/sample.txt,output_root=./output`

3. **Execute the Recipe**:
   - Click the "Execute Recipe" button
   - The recipe will be executed, and the results will be displayed in the output section

### Loading an Example Recipe

1. Go to the "Examples" tab
2. Select an example recipe from the dropdown
3. Click the "Load Example" button
4. The example recipe will be loaded into the "Recipe JSON" text area in the Execute Recipe tab
5. Return to the Execute Recipe tab to execute the loaded recipe

## Context Variables

Context variables are key-value pairs that provide input to the recipe. They are added to the recipe context and can be accessed within the recipe steps.

Common context variables include:

- `input`: Path to an input file or directory
- `output_root`: Root directory for output files
- `model`: LLM model to use for generation (e.g., `gpt-4-1106-preview`)
- `prompt`: A prompt template for LLM generation
- Custom variables: Any other variables needed by your recipe

Format example:
```
input=data/input.txt,output_root=./output,model=gpt-4-1106-preview
```

## Interpreting Results

After executing a recipe, you'll see the results in the output section:

- **Results**: Shows the formatted output of the recipe execution, including execution time
- **Raw Output**: Shows the raw JSON output, useful for seeing all generated content
- **Debug Context**: Shows the full context after execution, useful for debugging

## Troubleshooting

### Common Issues

1. **Recipe Not Found Error**:
   - Ensure the recipe file path is correct
   - Try using an absolute path instead of a relative path
   - Check if the file exists in the expected location

2. **Context Variable Errors**:
   - Ensure context variables are formatted correctly as `key=value` pairs
   - Separate multiple variables with commas
   - Make sure there are no spaces around the equals sign

3. **Recipe Execution Errors**:
   - Check the error message in the Results output
   - Look at the Debug Context to see the state when the error occurred
   - Ensure all required files exist and paths are correct

### Logs

If you're encountering issues, check the log files in the `logs` directory for more detailed error information:

- `logs/info.log`: Contains general information about the app's operation
- `logs/error.log`: Contains error messages
- `logs/debug.log`: Contains detailed debug information (if debug logging is enabled)

## Advanced Usage

### Command Line Options

The Recipe Executor App supports several command line options:

- `--host`: Host to listen on (default: 0.0.0.0)
- `--port`: Port to listen on (default: auto-selected by Gradio)
- `--no-mcp`: Disable MCP server functionality
- `--debug`: Enable debug mode

Example:
```bash
python -m recipe_executor_app.app --host 127.0.0.1 --port 7861 --debug
```

### Using the API

The Gradio app provides an API at `/api` that can be used to programmatically execute recipes. See the Gradio documentation for more information on using the API.