# Recipe Tool App Usage Guide

This guide provides detailed information on how to use the Recipe Tool Gradio app.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Executing Recipes](#executing-recipes)
4. [Creating Recipes](#creating-recipes)
5. [Loading Examples](#loading-examples)
6. [Configuration](#configuration)
7. [API Integration](#api-integration)
8. [MCP Server Integration](#mcp-server-integration)

## Introduction

The Recipe Tool App is a web interface for the Recipe Tool library, providing a user-friendly way to execute and create recipes. It is built with Gradio and provides easy access to all the functionality of the Recipe Tool.

## Getting Started

### Installation

1. Make sure you have Python 3.11 or higher installed.
2. Navigate to the app directory:
   ```bash
   cd apps/recipe-tool
   ```
3. Install dependencies:
   ```bash
   make
   ```

### Running the App

Start the app with:

```bash
make run
```

The app will be available at the URL displayed in the console after launching.

## Executing Recipes

The "Execute Recipe" tab allows you to run recipe JSON files:

1. Upload a recipe JSON file using the file uploader, or
2. Paste recipe JSON directly into the code editor
3. (Optional) Add context variables in the format: `key1=value1,key2=value2` (note that `recipe_root`, `ai_context_root`, and `output_root` are automatically provided)
4. Click the "Execute Recipe" button
5. View the results in the output panel:
   - The "Results" tab shows formatted results
   - The "Raw Output" tab shows all context artifacts as JSON

### Example

Here's a simple example of executing a recipe:

1. Upload a recipe file or paste this JSON:

   ```json
   {
     "name": "Simple Test Recipe",
     "description": "A test recipe that echos some input",
     "steps": [
       {
         "type": "set_context",
         "config": {
           "key": "output",
           "value": "Hello from the recipe!"
         }
       }
     ]
   }
   ```

2. Click "Execute Recipe"
3. You should see the output: "Hello from the recipe!"

## Creating Recipes

The "Create Recipe" tab allows you to generate new recipes from text descriptions:

1. Enter your recipe idea in the text area, or
2. Upload an idea file (.md or .txt)
3. (Optional) Add reference files for context
4. (Optional) Add context variables in the format: `key1=value1,key2=value2` (note that `recipe_root`, `ai_context_root`, and `output_root` are automatically provided)
5. Click the "Create Recipe" button
6. View the generated recipe in the output panel:
   - The "Generated Recipe" tab shows the recipe JSON
   - The "Preview" tab shows a structured overview of the recipe

### Example Idea Input

```
Create a recipe that reads a Markdown file, extracts code blocks, and writes them to separate files.
The recipe should:
1. Read a Markdown file input from a path
2. Find all code blocks with language specifiers
3. Extract code from each block
4. Create individual files for each code block, named by order of appearance
5. Output the paths of generated files
```

## Loading Examples

The "Examples" tab provides access to pre-built example recipes:

1. Select an example recipe from the dropdown
2. Click "Load Example"
3. The example will be loaded into the recipe editor
4. Information about the example will be displayed

## Configuration

### Environment Variables

You can configure the app through environment variables or a `.env` file:

1. Copy the example configuration:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to customize settings:

| Environment Variable           | Description                   | Default Value                              |
| ------------------------------ | ----------------------------- | ------------------------------------------ |
| RECIPE_APP_APP_TITLE           | Title of the application      | "Recipe Tool"                              |
| RECIPE_APP_DEBUG               | Enable debug mode             | false                                      |
| RECIPE_APP_HOST                | Host to listen on             | "0.0.0.0"                                  |
| RECIPE_APP_PORT                | Port to listen on             | None (auto-selected)                       |
| RECIPE_APP_MCP_SERVER          | Enable MCP server             | true                                       |
| RECIPE_APP_RECIPE_CREATOR_PATH | Path to recipe creator recipe | "../../recipes/recipe_creator/create.json" |

### Command-Line Options

Override settings with command-line options:

```bash
# Show help
python -m recipe_tool_app.app --help

# Run on a specific host and port
python -m recipe_tool_app.app --host 127.0.0.1 --port 8000

# Disable MCP server functionality
python -m recipe_tool_app.app --no-mcp

# Enable debug mode
python -m recipe_tool_app.app --debug
```

## API Integration

The app exposes named API endpoints for programmatic access.

### Using the API

You can interact with the API using the [Gradio Client](https://www.gradio.app/guides/getting-started-with-the-python-client) library:

```python
from gradio_client import Client

client = Client("http://127.0.0.1:[PORT]")  # Replace [PORT] with the actual port

# Execute a recipe
result = client.predict(
    None,                      # recipe_file
    '{"name": "Test Recipe"}', # recipe_text
    "key1=value1",             # context_vars
    api_name="execute_recipe"
)

# Create a recipe
result = client.predict(
    "Create a recipe that processes text files", # idea_text
    None,                                       # idea_file
    None,                                       # reference_files
    "model=gpt-4",                              # context_vars
    api_name="create_recipe"
)

# Load an example
result = client.predict(
    "../../recipes/example_simple/test_recipe.json",  # example_path
    api_name="load_example"
)
```

For complete API documentation, please see the [API Documentation](api.md).

## MCP Server Integration

The app functions as an MCP (Model Context Protocol) server, providing tools for AI assistants to execute and create recipes.

### Setting Up the MCP Server

The MCP server is enabled by default. The endpoint for AI assistants is:

```
http://your-server:[PORT]/gradio_api/mcp/sse  # Replace [PORT] with the actual port
```

### Available MCP Tools

The following MCP tools are exposed:

- **execute_recipe** - Execute a recipe from a file or text input

  - Parameters:
    - file (str, optional): Path to a recipe JSON file to execute
    - text (str, optional): Recipe JSON content as text
    - ctx (str, optional): Context variables as comma-separated key=value pairs (e.g., "key1=value1,key2=value2")

- **create_recipe** - Create a new recipe from an idea description

  - Parameters:
    - text (str): Text describing the recipe idea
    - file (str, optional): Path to an idea file (.md or .txt)
    - refs (list, optional): List of reference file paths to include
    - ctx (str, optional): Context variables as comma-separated key=value pairs

- **load_example** - Load an example recipe from the examples directory
  - Parameters:
    - path (str): Path to the example recipe file

### Using with AI Assistants

To use with Claude or another AI assistant that supports MCP:

1. Configure the assistant to connect to:

   ```
   http://your-server:[PORT]/gradio_api/mcp/sse  # Replace [PORT] with the actual port
   ```

2. The assistant can now use the tools to execute and create recipes.
