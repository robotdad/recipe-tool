# Shared Components

This directory contains shared components used across multiple Recipe Tool applications.

## Structure

- `gradio_components/` - Shared Gradio UI components
  - `settings_sidebar.py` - Reusable settings sidebar for model configuration

## Usage

The shared components are automatically added to the Python path by the import wrappers in each app.

Example:
```python
from recipe_executor_app.settings_sidebar import create_settings_sidebar

# Use as before
create_settings_sidebar(on_save=callback_function)
```

## Design Philosophy

Following the "ruthless simplicity" principle from our implementation philosophy, this shared module:
- Provides a single source of truth for common components
- Avoids complex abstractions or future-proofing
- Uses simple Python imports without additional build steps
- Maintains backward compatibility with existing app code