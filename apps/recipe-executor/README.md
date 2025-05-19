# Recipe Executor App

A Gradio web interface for the Recipe Executor, allowing users to execute recipes through a simple browser interface.

## Features

- **Execute Recipes**: Run recipes from uploaded files or pasted JSON
- **Context Variables**: Pass custom variables to recipes
- **Example Recipes**: Load and run pre-configured examples
- **Debug Tools**: View raw output and full execution context
- **Path Resolution**: Intelligent path handling for recipe files

## Installation

1. Install dependencies:

```bash
cd apps/recipe-executor
make install
```

2. Activate the virtual environment:

```bash
# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

## Usage

### Starting the App

```bash
python -m recipe_executor_app.app
```

or:

```bash
cd apps/recipe-executor
make run
```

### Command Line Options

- `--host`: Host to listen on (default: 0.0.0.0)
- `--port`: Port to listen on (default: auto-selected by Gradio)
- `--no-mcp`: Disable MCP server functionality
- `--debug`: Enable debug mode

Example:

```bash
python -m recipe_executor_app.app --host 127.0.0.1 --port 7861 --debug
```

### Using the App

1. **Upload Recipe**: Upload a recipe JSON file or paste recipe JSON directly into the text area
2. **Add Context Variables**: Optionally add context variables as key=value pairs
3. **Execute Recipe**: Click the "Execute Recipe" button to run the recipe
4. **View Results**: See the results in the "Results" tab, raw output in the "Raw Output" tab, and full context in the "Debug Context" tab

### Context Variables

Context variables can be passed to recipes in the format `key1=value1,key2=value2`. These will be available in the recipe context.

Example:

```
model=gpt-4-1106-preview,input=data/input.txt,output_root=./output
```

## Development

### Project Structure

```
apps/recipe-executor/
├── recipe_executor_app/      # Main application code
│   ├── __init__.py
│   ├── app.py                # App entry point
│   ├── config.py             # Configuration settings
│   ├── core.py               # Core functionality
│   ├── ui_components.py      # Gradio UI components
│   └── utils.py              # Utility functions
├── docs/                     # Documentation
├── tests/                    # Tests
├── logs/                     # Log files
├── README.md                 # This file
├── pyproject.toml            # Project configuration
└── Makefile                  # Build scripts
```

### Testing

Run tests with:

```bash
make test
```

### Code Style

Run linting and formatting checks with:

```bash
make lint
make format
```

## Known Issues

### Websockets Legacy Deprecation Warnings

The application filters out deprecation warnings from the websockets.legacy module. These warnings come from Gradio's internal dependencies using the older websockets API. The warnings have been filtered in the pytest configuration since they are not actionable within our codebase, as the issue needs to be fixed in Gradio's dependencies.

## Next Steps

- Add ability to download generated recipes
- Implement recipe versioning or history
- Add visualization for complex recipe structures
- Enhance error messages to be more user-friendly
- Add more debug tools for complex recipes
