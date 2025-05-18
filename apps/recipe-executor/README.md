# Recipe Executor Gradio App

A Gradio web interface for the Recipe Executor library, providing a user-friendly way to execute and create recipes.

## Features

- Execute recipes from files or pasted JSON
- Create recipes from simple text descriptions
- Add context variables and reference files
- MCP server integration for AI tools
- Browse and load example recipes
- Configurable through environment variables and command-line options

## Installation

### Development Setup

1. Clone the repository (if you haven't already)
2. Navigate to the app directory:
   ```bash
   cd apps/recipe-executor
   ```
3. Create and activate a virtual environment:
   ```bash
   make
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

## Usage

Start the Gradio app:

```bash
make run
```

The app will be available at the URL displayed in the console after launching.

### Command-line Options

The application supports several command-line options to override configuration:

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

### Configuration

The app can be configured through environment variables or a `.env` file:

1. Copy the example configuration:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to customize settings:

| Environment Variable           | Description                    | Default Value                                        |
| ------------------------------ | ------------------------------ | ---------------------------------------------------- |
| RECIPE_APP_APP_TITLE           | Title of the application       | "Recipe Executor"                                    |
| RECIPE_APP_APP_DESCRIPTION     | Description of the application | "A web interface for executing and creating recipes" |
| RECIPE_APP_DEBUG               | Enable debug mode              | false                                                |
| RECIPE_APP_HOST                | Host to listen on              | "0.0.0.0"                                            |
| RECIPE_APP_PORT                | Port to listen on              | None (auto-selected)                                 |
| RECIPE_APP_MCP_SERVER          | Enable MCP server              | true                                                 |
| RECIPE_APP_RECIPE_CREATOR_PATH | Path to recipe creator recipe  | "../../recipes/recipe_creator/create.json"           |
| RECIPE_APP_LOG_DIR             | Directory for logs             | "logs"                                               |
| RECIPE_APP_THEME               | Gradio theme                   | "soft"                                               |

## Development

- Run tests: `make test`
- Format code: `make format`
- Check linting: `make lint`
- Type check: `make type-check`

## API & MCP Server Integration

### API Endpoints

The app exposes named API endpoints for programmatic access:

```python
# Python Client Example
from gradio_client import Client

client = Client("http://127.0.0.1:[PORT]")  # Replace [PORT] with the actual port

# Execute a recipe
result = client.predict(
    None,                      # recipe_file (None if using text)
    '{"name": "Test"}',        # recipe_text
    "key1=value1,key2=value2", # context_vars
    api_name="execute_recipe"
)
# Returns: {"formatted_results": "...", "raw_json": "..."}

# Create a recipe
result = client.predict(
    "Create a recipe that processes text files",  # idea_text
    None,                                        # idea_file
    None,                                        # reference_files
    "model=gpt-4",                               # context_vars
    api_name="create_recipe"
)
# Returns: {"recipe_json": "...", "structure_preview": "..."}

# Load an example
result = client.predict(
    "/path/to/example.json",  # example_path
    api_name="load_example"
)
# Returns: {"recipe_content": "...", "description": "..."}
```

### MCP Server Integration

The app functions as an MCP (Model Context Protocol) server, providing tools for AI assistants to execute and create recipes. To use with an AI assistant that supports MCP, configure it to use the endpoint:

```
http://your-server:[PORT]/gradio_api/mcp/sse  # Replace [PORT] with the actual port
```

The following MCP tools are exposed:

- **execute_recipe** - Execute a recipe from a file or text input

  - Parameters: file (recipe file), text (JSON content), ctx (context variables)

- **create_recipe** - Create a new recipe from an idea description

  - Parameters: text (idea description), file (idea file), refs (reference files), ctx (context variables)

- **load_example** - Load an example recipe from the examples directory
  - Parameters: path (example recipe path)

For detailed documentation of the MCP tools, see the [Usage Guide](docs/usage.md#available-mcp-tools).

## Documentation

For more detailed information, see:

- [Usage Guide](docs/usage.md) - Detailed instructions for users
- [API Documentation](docs/api.md) - Detailed API reference
- [Development Guide](docs/development.md) - Information for developers
- [Reuse as Component](docs/reuse_as_component.md) - How to reuse this app in other Gradio apps

## License

See the project root for license information.
