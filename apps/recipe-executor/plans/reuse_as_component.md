# Reusing Recipe Executor App as a Component in Other Gradio Apps

This guide outlines how to use the Recipe Executor Gradio app as a component within another Gradio application, such as the main Recipe Tool app.

## Approach 1: Using the create_executor_block Function

The Recipe Executor app provides a `create_executor_block` function that returns a Gradio Blocks component that can be embedded directly in another app:

```python
import gradio as gr
import sys
from pathlib import Path

# Add recipe-executor app to the Python path
executor_app_path = str(Path(__file__).parent.parent.parent / "recipe-executor")
if executor_app_path not in sys.path:
    sys.path.append(executor_app_path)

# Import components from recipe-executor app
from recipe_executor_app.app import create_executor_block, get_components
from recipe_executor_app.core import RecipeExecutorCore

# Create the main app
with gr.Blocks(title="My App with Recipe Executor") as app:
    gr.Markdown("# My App with Recipe Executor")

    with gr.Tab("My Features"):
        # Your custom UI components
        text_input = gr.Textbox(label="Text Input")
        button = gr.Button("Process")
        output = gr.Textbox(label="Output")

        # Your custom function
        def process_text(text):
            return f"Processed: {text}"

        button.click(fn=process_text, inputs=text_input, outputs=output)

    with gr.Tab("Recipe Executor"):
        # Create a recipe executor core
        executor_core = RecipeExecutorCore()

        # Add the executor block
        create_executor_block(executor_core)

# Launch the app
app.launch()
```

This approach embeds the Recipe Executor UI directly within your app, with full functionality.

## Approach 2: Using Individual Components and Functions

If you need more control over the UI, you can use the `get_components` function to access individual components and functions:

```python
import gradio as gr
import sys
from pathlib import Path

# Add recipe-executor app to the Python path
executor_app_path = str(Path(__file__).parent.parent.parent / "recipe-executor")
if executor_app_path not in sys.path:
    sys.path.append(executor_app_path)

# Import components from recipe-executor app
from recipe_executor_app.app import get_components

# Get the components
components = get_components()
executor_core = components["core"]
create_executor_block = components["create_executor_block"]
execute_recipe = components["execute_recipe"]
load_recipe = components["load_recipe"]

# Create the main app
with gr.Blocks(title="My App with Recipe Executor") as app:
    gr.Markdown("# My App with Recipe Executor")

    # Create a custom UI that uses the Recipe Executor functionality
    recipe_text = gr.Code(label="Recipe JSON", language="json", interactive=True, wrap_lines=True)
    execute_btn = gr.Button("Execute Recipe")
    result = gr.Markdown(label="Result")

    # Use the execute_recipe function from the Recipe Executor
    async def execute_recipe_wrapper(text):
        result = await execute_recipe(None, text, None)
        return result.get("formatted_results", "")

    execute_btn.click(fn=execute_recipe_wrapper, inputs=recipe_text, outputs=result)

# Launch the app
app.launch()
```

This approach gives you more control over the UI while still using the core functionality of the Recipe Executor.

## Using In Recipe Tool App

The Recipe Executor app has been specifically designed to be used as a component in the Recipe Tool app. The Recipe Tool app checks for the availability of the Recipe Executor app and uses it if available:

```python
# In recipe_tool_app/ui_components.py

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

# In the build_ui function
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

This pattern allows the Recipe Tool app to use the dedicated Recipe Executor app if it's available, but fall back to its own implementation if needed.

## Benefits of Component Reuse

Reusing the Recipe Executor as a component has several benefits:

1. **Code Reuse**: The same code is used in both the standalone Recipe Executor app and when embedded in the Recipe Tool app
2. **Maintainability**: Changes to the Recipe Executor code are automatically reflected in both apps
3. **Consistency**: Users get the same experience whether using the standalone app or the embedded component
4. **Modularity**: The codebase is more modular and easier to maintain

## Future Improvements

Future improvements to the component reuse approach could include:

1. **More Granular Components**: Breaking down the Recipe Executor into even more granular components that can be reused independently
2. **Configuration Options**: Adding more configuration options to the `create_executor_block` function to customize the UI
3. **Event Hooks**: Adding event hooks that allow the parent app to respond to events in the Recipe Executor component
4. **Theme Customization**: Adding better support for theme customization when used as a component
