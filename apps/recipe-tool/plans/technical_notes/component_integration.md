# Recipe Executor Component Integration

This document explains how the Recipe Tool app integrates the Recipe Executor app as a reusable component.

## Overview

The Recipe Tool app now uses the dedicated Recipe Executor app as a component for the "Execute Recipe" tab. This approach follows the modular design philosophy of the project, allowing for better code reuse, maintainability, and consistency.

## Integration Approach

The integration follows the "Component-Level Reuse" pattern, where the Recipe Executor app exposes a function that creates a Gradio Blocks component that can be embedded directly in the Recipe Tool app.

### Key Files

- `apps/recipe-executor/recipe_executor_app/app.py`: Contains the `create_executor_block` function that creates a reusable Gradio Blocks component
- `apps/recipe-tool/recipe_tool_app/ui_components.py`: Imports and uses the `create_executor_block` function in the `build_ui` method

### How It Works

1. **Path Resolution**: The Recipe Tool app adds the Recipe Executor app directory to the Python path
2. **Import Components**: The Recipe Tool app imports the components from the Recipe Executor app
3. **Fallback Mechanism**: If the Recipe Executor app is not available, the Recipe Tool app falls back to its own implementation
4. **Component Creation**: The Recipe Tool app calls the `create_executor_block` function to create the Execute Recipe tab

## Code Example

In the Recipe Executor's `app.py`:

```python
def create_executor_block(recipe_core: RecipeExecutorCore = None) -> gr.Blocks:
    """Create a Recipe Executor block that can be embedded in other apps."""
    # Initialize core if not provided
    if recipe_core is None:
        recipe_core = RecipeExecutorCore()

    # Apply theme
    theme = gradio.themes.Soft() if settings.theme == "soft" else settings.theme

    with gr.Blocks(theme=theme) as block:
        # UI components and event handlers for recipe execution
        # ...

    return block
```

In the Recipe Tool's `ui_components.py`:

```python
# Add recipe-executor app to the Python path
executor_app_path = str(Path(__file__).parent.parent.parent / "recipe-executor")
if executor_app_path not in sys.path:
    sys.path.append(executor_app_path)

# Import recipe-executor components 
try:
    from recipe_executor_app.app import create_executor_block, get_components
    from recipe_executor_app.core import RecipeExecutorCore
    EXECUTOR_AVAILABLE = True
except ImportError:
    logger.warning("Could not import recipe-executor app. Recipe execution tab will use local implementation.")
    EXECUTOR_AVAILABLE = False

def build_ui(recipe_core: RecipeToolCore) -> gr.Blocks:
    # ...
    with gr.Tabs():
        if EXECUTOR_AVAILABLE:
            # Use the dedicated recipe-executor component
            with gr.TabItem("Execute Recipe"):
                executor_core = RecipeExecutorCore()
                executor_block = create_executor_block(executor_core)
        else:
            # Fall back to local implementation
            # ...
```

## Benefits of This Approach

1. **Code Reuse**: The Recipe Executor code is not duplicated in the Recipe Tool app
2. **Maintainability**: Changes to the Recipe Executor code are automatically reflected in both apps
3. **Separation of Concerns**: The Recipe Executor app can be developed and tested independently
4. **Flexibility**: The Recipe Tool app can choose to use the Recipe Executor component or fall back to its own implementation if needed
5. **Consistency**: Users get the same experience whether using the standalone Recipe Executor app or the embedded component in the Recipe Tool app

## Potential Issues and Solutions

### Path Resolution

**Issue**: The Recipe Tool app needs to find the Recipe Executor app directory to import its components.

**Solution**: The code uses relative path resolution with `Path(__file__).parent.parent.parent / "recipe-executor"` to find the Recipe Executor app directory. This works as long as the Recipe Executor app is in the expected location relative to the Recipe Tool app.

### Import Errors

**Issue**: If the Recipe Executor app is not available or cannot be imported, the Recipe Tool app needs to fall back to its own implementation.

**Solution**: The code uses a try-except block to catch import errors and sets an `EXECUTOR_AVAILABLE` flag to determine whether to use the Recipe Executor component or fall back to the local implementation.

### Consistency

**Issue**: The Recipe Executor component may have a different look and feel than the rest of the Recipe Tool app.

**Solution**: The `create_executor_block` function accepts the parent app's theme to ensure consistency in styling.

## Future Improvements

1. **Configuration Options**: Add more configuration options to the `create_executor_block` function to customize the UI
2. **Event Hooks**: Add event hooks that allow the parent app to respond to events in the Recipe Executor component
3. **State Sharing**: Improve the sharing of state between the Recipe Executor component and the parent app
4. **Dynamic Loading**: Add support for dynamically loading the Recipe Executor component at runtime

## Testing

To test the integration:

1. Ensure both the Recipe Executor app and Recipe Tool app are installed
2. Run the Recipe Tool app and verify that the Execute Recipe tab uses the Recipe Executor component
3. Make a change to the Recipe Executor app and verify that it's reflected in the Recipe Tool app
4. Test the fallback mechanism by temporarily renaming the Recipe Executor app directory and verifying that the Recipe Tool app falls back to its own implementation