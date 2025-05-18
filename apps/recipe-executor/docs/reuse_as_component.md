# Reusing Recipe Executor App as a Component in Another Gradio App

This guide outlines several approaches for integrating the Recipe Executor Gradio app as a component within another Gradio application.

## Approach 1: Using gr.load() with Spaces/Hosted App

If your Recipe Executor app is hosted (either on Hugging Face Spaces or elsewhere):

```python
import gradio as gr

# Load the Recipe Executor app
recipe_executor = gr.load("username/recipe-executor")  # If hosted on Hugging Face Spaces
# Or
recipe_executor = gr.load("http://localhost:7860")  # If hosted locally

# Build a new app that incorporates the Recipe Executor
with gr.Blocks() as demo:
    gr.Markdown("# Super App with Recipe Executor Integration")
    
    with gr.Tab("My Custom Features"):
        # Your custom UI components
        input_text = gr.Textbox(label="Text Input")
        output_text = gr.Textbox(label="Text Output")
        button = gr.Button("Process")
        
        # Your custom function
        def process_text(text):
            # Do something with the text
            return f"Processed: {text}"
        
        button.click(process_text, inputs=input_text, outputs=output_text)
    
    with gr.Tab("Recipe Executor"):
        # Here you embed the loaded Recipe Executor app
        # You can call the API endpoints of the loaded app
        recipe_text = gr.Textbox(label="Recipe JSON")
        execute_btn = gr.Button("Execute Recipe")
        result = gr.Markdown(label="Result")
        
        execute_btn.click(
            recipe_executor.execute_recipe,  # Call the API endpoint by its name
            inputs=[None, recipe_text, None],  # Pass appropriate arguments
            outputs=result
        )

# Launch the combined app
demo.launch()
```

## Approach 2: Direct Integration of the Components

If you have direct access to the Recipe Executor code, you can import and use the `create_app()` function from your app.py file:

```python
import gradio as gr
from recipe_executor_app.app import create_app  # Import the function that creates your app

# Create a new app that incorporates the Recipe Executor
with gr.Blocks() as demo:
    gr.Markdown("# Super App with Recipe Executor Integration")
    
    with gr.Tab("My Custom Features"):
        # Your custom UI components and functionality
        # ...as in the previous example...
    
    with gr.Tab("Recipe Executor"):
        # Directly use the app object
        recipe_app = create_app()  # This returns a gr.Blocks object
        
        # You can also access and modify components of the recipe_app if needed
        # (This would require modifying the original app.py to expose components)

# Launch the combined app
demo.launch()
```

## Approach 3: Component-Level Reuse

For the most flexible integration, you could modify your Recipe Executor app to expose its individual components and functions:

```python
# In recipe_executor_app/app.py

def create_app() -> gr.Blocks:
    """Create and return the Gradio app."""
    app = RecipeExecutorApp()
    return app.build_ui()

def get_components():
    """Return individual components for embedding in other apps."""
    app = RecipeExecutorApp()
    # Return UI components and functions that can be reused
    return {
        "execute_recipe": app.execute_recipe,
        "create_recipe": app.create_recipe,
        # Include UI building functions too
    }

# Then in your main app:
import gradio as gr
from recipe_executor_app.app import get_components

components = get_components()

with gr.Blocks() as demo:
    # Use the components directly
    # ...
```

## Best Practice: Use Interface or Blocks as Functions

The most elegant way to reuse Gradio apps is to design them with reusability in mind from the start:

```python
# In the recipe app, make sure to return your main function:
def create_recipe_executor_block():
    """Create a Recipe Executor block that can be embedded in other apps."""
    app = RecipeExecutorApp()
    
    with gr.Blocks() as block:
        # Build UI components
        # ...
        
    return block

# In the main app:
import gradio as gr
from recipe_executor_app.app import create_recipe_executor_block

with gr.Blocks() as demo:
    gr.Markdown("# My Super App")
    
    with gr.Tab("Home"):
        # Home tab content
        
    with gr.Tab("Recipe Executor"):
        recipe_block = create_recipe_executor_block()
        
demo.launch()
```

## Implementation in the Recipe Executor App

To make the Recipe Executor app more reusable, we could refactor app.py to expose individual components:

```python
# Add this function to recipe_executor_app/app.py

def create_recipe_executor_block():
    """Create a Recipe Executor block that can be embedded in other apps."""
    app = RecipeExecutorApp()
    
    with gr.Blocks() as block:
        # Copy the UI building code from the existing build_ui method,
        # but without the outer Blocks context (which is created here)
        gr.Markdown("# Recipe Executor")
        gr.Markdown("A web interface for executing and creating recipes.")
        
        with gr.Tabs():
            # ... rest of the UI components
    
    return block
```

This would allow other applications to reuse the Recipe Executor functionality at a more granular level, while still maintaining the app's ability to run standalone.

## References

- [Gradio Docs: Using Blocks Like Functions](https://www.gradio.app/guides/using-blocks-like-functions)
- [Gradio Docs: Other Gradio Guides](https://www.gradio.app/guides)