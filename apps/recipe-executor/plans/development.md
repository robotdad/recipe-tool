# Recipe Executor App Developer Guide

This guide is for developers who want to contribute to the Recipe Executor App or extend it for their own purposes.

## Project Structure

```
apps/recipe-executor/
├── recipe_executor_app/      # Main application code
│   ├── __init__.py           # Package initialization
│   ├── app.py                # App entry point
│   ├── config.py             # Configuration settings
│   ├── core.py               # Core functionality
│   ├── ui_components.py      # Gradio UI components
│   └── utils.py              # Utility functions
├── docs/                     # Documentation
│   ├── README.md             # Documentation overview
│   ├── usage.md              # User guide
│   └── development.md        # This file
├── tests/                    # Tests
│   ├── __init__.py           # Test package initialization
│   └── test_app.py           # Tests for app.py
├── logs/                     # Log files
├── README.md                 # Project overview
├── pyproject.toml            # Project configuration
└── Makefile                  # Build scripts
```

## Development Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/recipe-tool.git
   cd recipe-tool
   ```

2. Set up the development environment:
   ```bash
   cd apps/recipe-executor
   make install
   ```

3. Activate the virtual environment:
   ```bash
   # Linux/macOS
   source .venv/bin/activate
   
   # Windows
   .\.venv\Scripts\activate
   ```

## Key Components

### app.py

This is the entry point for the application. It parses command line arguments, initializes the logger, creates the app, and launches it.

### config.py

This contains the configuration settings for the app, including:
- App title and description
- Server host and port
- Log directory and level
- Example recipe paths
- Theme settings

Settings can be overridden with environment variables prefixed with `RECIPE_EXEC_APP_`.

### core.py

This contains the `RecipeExecutorCore` class, which is the core of the application. It provides methods for:
- Executing recipes
- Loading recipe files
- Finding example recipes

### ui_components.py

This contains functions for building the Gradio UI components and setting up event handlers.

### utils.py

This contains utility functions used throughout the application, including:
- Path resolution
- File reading and writing
- Context variable parsing
- Recipe JSON parsing and extraction
- Result formatting

## Adding a New Feature

To add a new feature to the Recipe Executor App:

1. Identify where the feature should be added:
   - New UI component: Add to `ui_components.py`
   - New core functionality: Add to `core.py`
   - New utility function: Add to `utils.py`
   - New configuration option: Add to `config.py`

2. Add tests for the new feature in the `tests` directory.

3. Update documentation in the `docs` directory.

4. Run linting, formatting, and type checking to ensure code quality:
   ```bash
   make lint
   make format
   make type-check
   ```

5. Run tests to ensure your feature works as expected:
   ```bash
   make test
   ```

## Example: Adding a New Tab

Let's walk through an example of adding a new tab to the UI:

1. Add a new function to `ui_components.py` to build the tab:
   ```python
   def build_new_tab() -> Tuple[gr.Component, ...]:
       """Build the New Tab UI components."""
       with gr.TabItem("New Tab"):
           # Add UI components here
           text_input = gr.Textbox(label="Input")
           button = gr.Button("Submit")
           output = gr.Textbox(label="Output")
       
       return text_input, button, output
   ```

2. Add a new function to set up event handlers for the tab:
   ```python
   def setup_new_tab_events(
       recipe_core: RecipeExecutorCore,
       text_input: gr.Textbox,
       button: gr.Button,
       output: gr.Textbox,
   ) -> None:
       """Set up event handlers for the new tab."""
       def process_input(text: str) -> str:
           # Process the input and return output
           return f"Processed: {text}"
       
       button.click(
           fn=process_input,
           inputs=[text_input],
           outputs=[output],
           api_name="process_input",
       )
   ```

3. Update the `build_ui` function to include the new tab:
   ```python
   def build_ui(recipe_core: RecipeExecutorCore) -> gr.Blocks:
       """Build the complete Gradio UI."""
       # ... existing code ...
       
       with gr.Tabs():
           # ... existing tabs ...
           
           # New Tab
           new_tab_components = build_new_tab()
           text_input, button, output = new_tab_components
       
       # ... existing event setup ...
       
       # Set up events for the new tab
       setup_new_tab_events(recipe_core, text_input, button, output)
       
       # ... existing code ...
   ```

4. Add tests for the new tab in `tests/test_ui_components.py`.

5. Update documentation to include information about the new tab.

## Adding a New Core Function

To add a new core function to the `RecipeExecutorCore` class:

1. Add the function to `core.py`:
   ```python
   async def new_function(self, param1: str, param2: int) -> Dict:
       """
       Description of what this function does.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           dict: Description of return value
       """
       try:
           # Implementation
           result = {}
           
           # ... function logic ...
           
           return result
       except Exception as e:
           logger.error(f"Error in new_function: {e}", exc_info=True)
           return {
               "error": f"Error: {str(e)}",
           }
   ```

2. Add tests for the new function in `tests/test_core.py`.

3. Update documentation to include information about the new function.

## Testing

### Running Tests

Run all tests:
```bash
make test
```

Run tests with coverage:
```bash
make coverage
```

### Adding Tests

Add tests in the `tests` directory. Tests should use pytest and follow the pattern:

```python
def test_something():
    """Test description."""
    # Arrange
    # ... set up test data ...
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == expected_result
```

For async functions, use:

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test description."""
    # Arrange
    # ... set up test data ...
    
    # Act
    result = await async_function_to_test()
    
    # Assert
    assert result == expected_result
```

## Code Quality

Maintain code quality with:

```bash
make lint     # Check for linting issues
make format   # Format code
make type-check # Check for type issues
```

## Documentation

Update documentation in the `docs` directory to reflect changes:

- `README.md`: Overview of the documentation
- `usage.md`: User guide
- `development.md`: Developer guide (this file)

## Release Process

To release a new version:

1. Update the version in `pyproject.toml`
2. Update the CHANGELOG.md file
3. Commit your changes
4. Create a tag for the new version
5. Push the tag to the repository