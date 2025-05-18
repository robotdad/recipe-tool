# Recipe Executor App - Developer Guide

This guide provides information for developers who want to extend or modify the Recipe Executor App.

## Project Structure

```
apps/recipe-executor/
├── docs/                    # Documentation
├── recipe_executor_app/     # Main package
│   ├── __init__.py          # Package version
│   ├── app.py               # Main application code
│   ├── config.py            # Configuration settings
│   └── types.py             # Type definitions
├── tests/                   # Test files
│   ├── __init__.py
│   └── test_app.py          # Tests for the app
├── .env.example             # Example environment variables
├── .ruff.toml               # Ruff linter configuration
├── Makefile                 # Build commands
├── README.md                # Project readme
└── pyproject.toml           # Python package configuration
```

## Architecture

The app is designed with the following components:

1. **RecipeExecutorApp** - Main class that handles UI and recipe execution
2. **Settings** - Configuration management using Pydantic
3. **Gradio UI** - Interface built with Blocks API
4. **MCP Server** - Model Context Protocol integration

### Class Diagram

```
┌─────────────────┐         ┌───────────┐
│RecipeExecutorApp│─────────►Executor   │
└────────┬────────┘         └───────────┘
         │                  ┌───────────┐
         └──────────────────►Context    │
                            └───────────┘
┌─────────────────┐
│Settings         │
└─────────────────┘         ┌───────────┐
         ▲                  │Gradio     │
         │                  │Interface  │
┌────────┴────────┐         └───────────┘
│Environment Vars │                 ▲
└─────────────────┘                 │
                                    │
                            ┌───────┴───┐
                            │build_ui() │
                            └───────────┘
```

## Key Components

### RecipeExecutorApp Class

The `RecipeExecutorApp` class provides methods for:

- `execute_recipe()` - Runs recipes from file or text input
- `create_recipe()` - Generates recipes from text descriptions
- `build_ui()` - Constructs the Gradio interface

### Settings 

The `Settings` class in `config.py` manages configuration using Pydantic settings.
It loads from environment variables, dotenv files, and defaults.

### Main Module

The main entrypoint handles command-line arguments and launches the Gradio app.

## Extending the App

### Adding a New Tab

To add a new tab to the interface:

```python
# In app.py, inside the build_ui method
with gr.Tabs():
    # ... existing tabs
    
    # Add your new tab
    with gr.TabItem("New Feature"):
        with gr.Row():
            with gr.Column():
                # Input components
                my_input = gr.Textbox(label="My Input")
                my_button = gr.Button("Process")
            
            with gr.Column():
                # Output components
                my_output = gr.Textbox(label="Results")
        
        # Connect components
        my_button.click(
            fn=my_processing_function,
            inputs=[my_input],
            outputs=[my_output]
        )
```

### Adding Configuration Options

To add new configuration options:

1. Update the `Settings` class in `config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings
    
    # Add your new settings
    my_new_setting: str = "default_value"
    another_setting: bool = False
```

2. Use the settings in your code:

```python
from recipe_executor_app.config import settings

# Access your settings
if settings.my_new_setting == "special_value":
    # Do something
```

### Creating a New Feature

To implement a new feature:

1. Add a method to the `RecipeExecutorApp` class:

```python
async def my_new_feature(self, input_param: str) -> str:
    """
    Implement a new feature.
    
    Args:
        input_param: Description of the input
        
    Returns:
        The result of the operation
    """
    # Implementation here
    return "Result"
```

2. Add UI components and connect them in the `build_ui` method

### Adding MCP Tools

To expose a new feature as an MCP tool:

1. Ensure your method is well-documented with proper type annotations
2. The MCP server will automatically expose methods that are connected to UI components

## Testing

### Running Tests

Run the tests with:

```bash
make test
```

### Adding Tests

Add new tests in the `tests` directory. Example:

```python
# tests/test_new_feature.py
from unittest.mock import patch, MagicMock

def test_my_new_feature():
    # Test setup
    with patch("recipe_executor_app.app.Executor") as mock_executor:
        mock_executor.return_value = MagicMock()
        
        # Import after patching
        from recipe_executor_app.app import RecipeExecutorApp
        
        # Create instance and test
        app = RecipeExecutorApp()
        result = app.my_new_feature("test_input")
        
        # Assertions
        assert result == "expected_result"
        mock_executor.assert_called_once()
```

## Code Style and Guidelines

This project follows these guidelines:

1. Use type hints consistently
2. Add docstrings for all functions and methods
3. Follow PEP 8 style conventions
4. Run `make format` and `make lint` before committing
5. Write tests for new functionality
6. Keep the UI simple and intuitive

## Build Process

The app is built and packaged using standard Python tooling:

- `uv` for dependency management
- `ruff` for linting and formatting
- `pyright` for type checking
- `pytest` for testing

## Deployment

The app can be deployed as:

1. A standalone web application
2. An MCP server for AI assistants
3. Embedded in other Gradio applications

## Release Process

To create a new release:

1. Update version in `recipe_executor_app/__init__.py`
2. Update changelog
3. Run tests: `make test`
4. Create a release commit
5. Tag the release: `git tag v0.1.0`
6. Push to the repository