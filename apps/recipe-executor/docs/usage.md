# Recipe Executor App Usage Guide

This guide provides detailed information on how to use the Recipe Executor Gradio app.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Executing Recipes](#executing-recipes)
4. [Creating Recipes](#creating-recipes)
5. [Loading Examples](#loading-examples)
6. [Configuration](#configuration)
7. [MCP Server Integration](#mcp-server-integration)

## Introduction

The Recipe Executor App is a web interface for the Recipe Executor library, providing a user-friendly way to execute and create recipes. It is built with Gradio and provides easy access to all the functionality of the Recipe Executor.

## Getting Started

### Installation

1. Make sure you have Python 3.11 or higher installed.
2. Navigate to the app directory:
   ```bash
   cd apps/recipe-executor
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

The app will be available at http://127.0.0.1:7861 by default.

## Executing Recipes

The "Execute Recipe" tab allows you to run recipe JSON files:

1. Upload a recipe JSON file using the file uploader, or
2. Paste recipe JSON directly into the code editor
3. (Optional) Add context variables in the format: `key1=value1,key2=value2`
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
4. (Optional) Add context variables in the format: `key1=value1,key2=value2`
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

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| RECIPE_APP_APP_TITLE | Title of the application | "Recipe Executor" |
| RECIPE_APP_DEBUG | Enable debug mode | false |
| RECIPE_APP_HOST | Host to listen on | "0.0.0.0" |
| RECIPE_APP_PORT | Port to listen on | 7861 |
| RECIPE_APP_MCP_SERVER | Enable MCP server | true |
| RECIPE_APP_RECIPE_CREATOR_PATH | Path to recipe creator recipe | "recipes/recipe_creator/create.json" |

### Command-Line Options

Override settings with command-line options:

```bash
# Show help
python -m recipe_executor_app.app --help

# Run on a specific host and port
python -m recipe_executor_app.app --host 127.0.0.1 --port 8000

# Disable MCP server functionality
python -m recipe_executor_app.app --no-mcp

# Enable debug mode
python -m recipe_executor_app.app --debug
```

## MCP Server Integration

The app functions as an MCP (Model Context Protocol) server, providing tools for AI assistants to execute and create recipes.

### Setting Up the MCP Server

The MCP server is enabled by default. The endpoint for AI assistants is:

```
http://your-server:7861/gradio_api/mcp/sse
```

### Available MCP Tools

The following MCP tools are exposed:

- **execute_recipe** - Execute a recipe from JSON content
  - Parameters:
    - recipe_json: The recipe JSON content
    - context: Optional context variables

- **create_recipe** - Create a recipe from a text description
  - Parameters:
    - idea_text: The recipe idea text
    - reference_files: Optional list of reference file paths
    - context: Optional context variables

### Using with AI Assistants

To use with Claude or another AI assistant that supports MCP:

1. Configure the assistant to connect to:
   ```
   http://your-server:7861/gradio_api/mcp/sse
   ```

2. The assistant can now use the tools to execute and create recipes.