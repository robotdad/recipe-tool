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

The app will be available at http://127.0.0.1:7861 by default.

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

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| RECIPE_APP_APP_TITLE | Title of the application | "Recipe Executor" |
| RECIPE_APP_APP_DESCRIPTION | Description of the application | "A web interface for executing and creating recipes" |
| RECIPE_APP_DEBUG | Enable debug mode | false |
| RECIPE_APP_HOST | Host to listen on | "0.0.0.0" |
| RECIPE_APP_PORT | Port to listen on | 7861 |
| RECIPE_APP_MCP_SERVER | Enable MCP server | true |
| RECIPE_APP_RECIPE_CREATOR_PATH | Path to recipe creator recipe | "recipes/recipe_creator/create.json" |
| RECIPE_APP_LOG_DIR | Directory for logs | "logs" |
| RECIPE_APP_THEME | Gradio theme | "soft" |

## Development

- Run tests: `make test`
- Format code: `make format`
- Check linting: `make lint`
- Type check: `make type-check`

## MCP Server Integration

The app functions as an MCP (Model Context Protocol) server, providing tools for AI assistants to execute and create recipes. To use with an AI assistant that supports MCP, configure it to use the endpoint:

```
http://your-server:7861/gradio_api/mcp/sse
```

The following MCP tools are exposed:
- execute_recipe - Execute a recipe from JSON content
- create_recipe - Create a recipe from a text description

## Documentation

For more detailed information, see:

- [Usage Guide](docs/usage.md) - Detailed instructions for users
- [Development Guide](docs/development.md) - Information for developers

## License

See the project root for license information.