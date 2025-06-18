"""Import settings sidebar from shared components."""

import sys
from pathlib import Path

# Add shared directory to Python path
shared_path = Path(__file__).resolve().parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Re-export from shared module
from gradio_components.settings_sidebar import SettingsConfig, create_settings_sidebar, get_model_string_from_env
from gradio_components.config_manager import (
    get_model_string, 
    get_setting, 
    load_settings, 
    save_settings,
    get_env_or_default,
    is_override
)

__all__ = [
    "SettingsConfig", 
    "create_settings_sidebar", 
    "get_model_string_from_env",
    "get_model_string",
    "get_setting",
    "load_settings",
    "save_settings",
    "get_env_or_default",
    "is_override"
]