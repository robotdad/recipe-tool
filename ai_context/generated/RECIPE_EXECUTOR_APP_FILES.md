# apps/recipe-executor/recipe_executor_app

[collect-files]

**Search:** ['apps/recipe-executor/recipe_executor_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 5/23/2025, 12:34:00 PM
**Files:** 6

=== File: apps/recipe-executor/recipe_executor_app/__init__.py ===
"""Recipe Executor Gradio App package."""

__version__ = "0.1.0"


=== File: apps/recipe-executor/recipe_executor_app/app.py ===
"""Gradio web app for the Recipe Executor."""

import argparse
from typing import Any, Dict, Optional

import gradio as gr
import gradio.themes
from recipe_executor.logger import init_logger

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.ui_components import (
    build_examples_tab,
    build_execute_recipe_tab,
    setup_example_events,
    setup_execute_recipe_events,
)

# Set up logging
logger = init_logger(settings.log_dir)
# Set logger level from settings
logger.setLevel(settings.log_level.upper())


def create_executor_block(recipe_core: Optional[RecipeExecutorCore] = None, include_header: bool = True) -> gr.Blocks:
    """Create a Recipe Executor block that can be embedded in other apps.

    Args:
        recipe_core: Optional RecipeExecutorCore instance. If None, a new one will be created.
        include_header: Whether to include the header (title and description)

    Returns:
        gr.Blocks: Gradio Blocks interface that can be embedded in other apps
    """
    # Initialize core if not provided
    if recipe_core is None:
        recipe_core = RecipeExecutorCore()

    # Apply theme
    theme = gradio.themes.Soft() if settings.theme == "soft" else settings.theme

    with gr.Blocks(theme=theme) as block:
        if include_header:
            gr.Markdown("# Recipe Executor")
            gr.Markdown("A web interface for executing recipes.")

        # Examples area (not in a tab)
        with gr.Accordion("Examples", open=False):
            examples_components = build_examples_tab()
            example_paths, load_example_btn, example_desc = examples_components

        # Execute Recipe components
        execute_components = build_execute_recipe_tab()
        (
            recipe_file,
            recipe_text,
            context_vars,
            execute_btn,
            progress,
            result_output,
            logs_output,
            context_json,
        ) = execute_components

        # Set up event handlers for execute recipe
        setup_execute_recipe_events(
            recipe_core,
            recipe_file,
            recipe_text,
            context_vars,
            execute_btn,
            progress,
            result_output,
            logs_output,
            context_json,
        )

        # Set up example loading events
        setup_example_events(
            recipe_core,
            example_paths,
            load_example_btn,
            example_desc,
            recipe_text,
            context_vars,
        )

    return block


def create_app() -> gr.Blocks:
    """Create and return the Gradio app."""
    # Initialize the core functionality
    recipe_core = RecipeExecutorCore()

    # Create the app with a title
    with gr.Blocks(title=settings.app_title) as app:
        # Use the component approach - clean and reusable
        create_executor_block(recipe_core)

    return app


def get_components(recipe_core: Optional[RecipeExecutorCore] = None) -> Dict[str, Any]:
    """Return individual components for embedding in other apps.

    Args:
        recipe_core: Optional RecipeExecutorCore instance. If None, a new one will be created.

    Returns:
        Dict[str, Any]: Dictionary of components and functions that can be reused
    """
    # Initialize core if not provided
    if recipe_core is None:
        recipe_core = RecipeExecutorCore()

    return {
        "create_executor_block": create_executor_block,
        "core": recipe_core,
        "execute_recipe": recipe_core.execute_recipe,
        "load_recipe": recipe_core.load_recipe,
    }


def main() -> None:
    """Entry point for the application."""
    # Parse command line arguments to override settings
    parser = argparse.ArgumentParser(description=settings.app_description)
    parser.add_argument("--host", help=f"Host to listen on (default: {settings.host})")
    parser.add_argument("--port", type=int, help=f"Port to listen on (default: {settings.port})")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP server functionality")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Override settings with command line arguments if provided
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.no_mcp:
        settings.mcp_server = False
    if args.debug:
        settings.debug = True

    # Create and launch the app with settings
    app = create_app()

    # Get launch kwargs from settings
    launch_kwargs = settings.to_launch_kwargs()
    app.launch(**launch_kwargs)


if __name__ == "__main__":
    main()


=== File: apps/recipe-executor/recipe_executor_app/config.py ===
"""Configuration settings for the Recipe Executor app."""

from typing import Any, Dict, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Recipe Executor app."""

    # App settings
    app_title: str = "Recipe Executor"
    app_description: str = "A web interface for executing recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: Optional[int] = None  # Let Gradio find an available port

    # MCP settings
    mcp_server: bool = True

    # Recipe executor settings
    log_dir: str = "logs"
    log_level: str = "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL

    # Example recipes paths
    example_recipes: List[str] = [
        "../../recipes/example_simple/test_recipe.json",
        "../../recipes/example_content_writer/generate_content.json",
        "../../recipes/example_brave_search/search.json",
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_EXEC_APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables like PYTHONPATH
    )

    def to_launch_kwargs(self) -> Dict[str, Any]:
        """Convert settings to kwargs for gradio launch() method."""
        return {
            "server_name": self.host,
            "server_port": self.port,
            "share": False,
            "pwa": True,
            "debug": self.debug,
            "mcp_server": self.mcp_server,
        }


# Create global settings instance
settings = Settings()


=== File: apps/recipe-executor/recipe_executor_app/core.py ===
"""Core functionality for the Recipe Executor app."""

import json
import logging
import os
from typing import Dict, Optional, Union, Any

from recipe_executor.context import Context
from recipe_executor.executor import Executor

from recipe_executor_app.utils import (
    create_temp_file,
    format_context_for_display,
    format_recipe_results,
    get_repo_root,
    log_context_paths,
    parse_context_vars,
    parse_recipe_json,
    read_file,
    resolve_path,
)

# Initialize logger
logger = logging.getLogger(__name__)


class RecipeExecutorCore:
    """Core functionality for Recipe Executor operations."""

    def __init__(self, executor: Optional[Executor] = None):
        """Initialize with the executor.

        Args:
            executor: Optional Executor instance. If None, a new one will be created.
        """
        # Ensure logger is properly configured
        self.logger = logger
        self.logger.info("Initializing RecipeExecutorCore")

        # Create executor with logger
        self.executor = executor if executor is not None else Executor(logger)

    async def execute_recipe(
        self, recipe_file: Optional[str], recipe_text: Optional[Union[Dict[str, Any], str]], context_vars: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute a recipe from a file upload or text input.

        Args:
            recipe_file: Optional path to a recipe JSON file
            recipe_text: Optional JSON string containing the recipe
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            dict: Contains formatted_results (markdown) and raw_json keys
        """
        try:
            # Parse context variables
            context_dict = parse_context_vars(context_vars)

            # Prepare context
            context = Context(artifacts=context_dict)

            # Determine recipe source
            recipe_source = None
            if recipe_file:
                recipe_source = recipe_file
                logger.info(f"Executing recipe from file: {recipe_file}")
            elif recipe_text:
                # Convert recipe_text to string if it's a dictionary
                recipe_content = json.dumps(recipe_text) if isinstance(recipe_text, dict) else recipe_text
                # Create a temporary file for the recipe text
                recipe_source, cleanup_fn = create_temp_file(recipe_content, prefix="recipe_", suffix=".json")
                logger.info(f"Executing recipe from text input (saved to {recipe_source})")
            else:
                return {
                    "formatted_results": "### Error\nNo recipe provided. Please upload a file or paste the recipe JSON.",
                    "raw_json": "{}",
                    "debug_context": {},
                }

            # Log important paths
            log_context_paths(context_dict)

            # Execute the recipe
            start_time = os.times().elapsed  # More accurate than time.time()
            await self.executor.execute(recipe_source, context)
            execution_time = os.times().elapsed - start_time

            # Get all artifacts from context to display in raw tab
            all_artifacts = context.dict()

            # Log the full context for debugging
            logger.debug(f"Final context: {context.dict()}")

            # Extract result entries from context
            results = {}
            # Always include output_root if it exists
            if "output_root" in all_artifacts:
                results["output_root"] = all_artifacts["output_root"]

            for key, value in all_artifacts.items():
                # Only include string results or keys that look like outputs
                if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
                    results[key] = value

            # Format the results for display
            markdown_output = format_recipe_results(results, execution_time)

            # Format the raw JSON for display
            raw_json = format_context_for_display(all_artifacts)

            return {"formatted_results": markdown_output, "raw_json": raw_json, "debug_context": all_artifacts}
        except Exception as e:
            logger.error(f"Error executing recipe: {e}", exc_info=True)
            return {
                "formatted_results": f"### Error Executing Recipe\n\n```\n{str(e)}\n```",
                "raw_json": "{}",
                "debug_context": {"error": str(e)},
            }

    async def load_recipe(self, recipe_path: str) -> Dict[str, str]:
        """Load a recipe file.

        Args:
            recipe_path: Path to the recipe file

        Returns:
            dict: Contains recipe_content and structure_preview keys
        """
        try:
            # Find the recipe file
            potential_paths = [
                recipe_path,  # Direct path
                os.path.abspath(recipe_path),  # Absolute path
                os.path.join(get_repo_root(), recipe_path),  # Relative to repo root
                os.path.join(get_repo_root(), "recipes", recipe_path),  # In recipes directory
            ]

            # Try each path until one exists
            for path in potential_paths:
                if os.path.exists(path):
                    logger.info(f"Found recipe at: {path}")
                    recipe_content = read_file(path)

                    # Parse the recipe to verify it's valid JSON
                    recipe_json = parse_recipe_json(recipe_content)

                    # Generate a preview of the structure
                    step_count = len(recipe_json.get("steps", []))
                    recipe_name = recipe_json.get("name", os.path.basename(path))
                    recipe_desc = recipe_json.get("description", "No description available")

                    structure_preview = f"""### Recipe: {recipe_name}

**Description**: {recipe_desc}

**Steps**: {step_count}

**Path**: {path}
"""

                    return {
                        "recipe_content": recipe_content,
                        "structure_preview": structure_preview,
                    }

            # If none of the paths exist
            logger.warning(f"Could not find recipe at any of these paths: {potential_paths}")
            return {
                "recipe_content": "",
                "structure_preview": f"### Error\nCould not find recipe at: {recipe_path}",
            }
        except Exception as e:
            logger.error(f"Error loading recipe: {e}", exc_info=True)
            return {
                "recipe_content": "",
                "structure_preview": f"### Error\n{str(e)}",
            }

    def find_examples_in_directory(self, directory: str) -> Dict[str, str]:
        """Find all JSON recipe examples in a directory.

        Args:
            directory: Directory to search in

        Returns:
            Dict[str, str]: Map of display names to file paths
        """
        examples = {}

        # Resolve the directory path
        directory = resolve_path(directory)

        # Check if the directory exists
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.warning(f"Example directory not found: {directory}")
            return {}

        # Find all JSON files
        repo_root = get_repo_root()

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, repo_root)

                    # Try to read the file to extract name if it's a recipe
                    try:
                        # Read and parse the file content as JSON
                        content = json.loads(read_file(full_path))
                        name = content.get("name", file)
                        examples[f"{name} ({rel_path})"] = full_path
                    except Exception as e:
                        # If we can't parse it as JSON, just use the filename
                        logger.debug(f"Could not parse {full_path} as JSON: {e}")
                        examples[f"{file} ({rel_path})"] = full_path

        return examples


=== File: apps/recipe-executor/recipe_executor_app/ui_components.py ===
"""UI components for the Recipe Executor Gradio app."""

import logging
import os
import io
import json
from typing import Optional, Tuple

import gradio as gr

from recipe_executor_app.config import settings
from recipe_executor_app.core import RecipeExecutorCore
from recipe_executor_app.utils import safe_json_serialize

# Initialize logger
logger = logging.getLogger(__name__)


def build_execute_recipe_tab() -> Tuple[
    gr.File, gr.Code, gr.Textbox, gr.Button, gr.Progress, gr.Markdown, gr.Textbox, gr.JSON
]:
    """Build the Execute Recipe tab UI components.

    Returns:
        Tuple: (recipe_file, recipe_text, context_vars, execute_btn,
               progress, result_output, logs_output, context_json)
    """
    # Create a progress bar first to ensure it's properly initialized
    progress = gr.Progress(track_tqdm=True)

    # No tab needed since this is the only component
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            recipe_file = gr.File(label="Recipe JSON File", file_types=[".json"])
            recipe_text = gr.Code(label="Recipe JSON", language="json", interactive=True, wrap_lines=True, lines=25)

            with gr.Accordion("Context Variables", open=False):
                context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs, separated by commas",
                )

            execute_btn = gr.Button("Execute Recipe", variant="primary", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            # No status indicator needed here

            with gr.Tabs():
                with gr.TabItem("Results"):
                    # The main results output
                    result_output = gr.Markdown(label="Results")

                    # Add context variables below the results
                    gr.Markdown("### Context Variables", visible=True)
                    context_json = gr.JSON(label="Context")

                with gr.TabItem("Logs"):
                    logs_output = gr.Textbox(label="Execution Logs", interactive=False, lines=20, max_lines=30)

    return (
        recipe_file,
        recipe_text,
        context_vars,
        execute_btn,
        progress,
        result_output,
        logs_output,
        context_json,
    )


def build_examples_tab() -> Tuple[gr.Dropdown, gr.Button, gr.Markdown]:
    """Build the Examples tab UI components.

    Returns:
        Tuple: (example_paths, load_example_btn, example_desc)
    """
    # Create components directly - no Tab or Markdown headings needed
    example_paths = gr.Dropdown(
        settings.example_recipes,
        label="Example Recipes",
    )
    load_example_btn = gr.Button("Load Example")
    example_desc = gr.Markdown()

    return example_paths, load_example_btn, example_desc


def setup_execute_recipe_events(
    recipe_core: RecipeExecutorCore,
    recipe_file: gr.File,
    recipe_text: gr.Code,
    context_vars: gr.Textbox,
    execute_btn: gr.Button,
    progress: gr.Progress,
    result_output: gr.Markdown,
    logs_output: gr.Textbox,
    context_json: gr.JSON,
) -> None:
    """Set up event handlers for execute recipe tab.

    Args:
        recipe_core: RecipeExecutorCore instance
        recipe_file: File upload component
        recipe_text: Recipe JSON component
        context_vars: Context variables textbox
        execute_btn: Execute button
        progress: Progress indicator
        result_output: Results markdown output
        logs_output: Logs textbox output
        context_json: Context variables JSON component
    """

    async def execute_recipe_formatted(
        file: Optional[str], recipe_text: Optional[str], ctx: Optional[str], progress=gr.Progress()
    ) -> Tuple[str, str, str]:
        """Format execute_recipe output for Gradio UI."""
        # Create a log capture handler
        log_capture = io.StringIO()
        log_handler = logging.StreamHandler(log_capture)
        log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.INFO)  # Capture INFO level and above

        # Add the handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)

        try:
            # Update progress bar
            progress(0, desc="Starting recipe execution...")

            # Parse the recipe text to JSON if needed
            recipe_json = json.loads(recipe_text) if recipe_text else None
            # Execute the recipe with log capturing
            result = await recipe_core.execute_recipe(file, recipe_json, ctx)

            # Update progress to indicate completion
            progress(1, desc="Recipe execution complete!")

            # Extract the individual fields for Gradio UI
            formatted_results = result.get("formatted_results", "")

            # Get the captured logs
            log_handler.flush()
            log_content = log_capture.getvalue()

            # Use the log content directly since we're using gr.Code with language="log"
            logs_formatted = log_content

            # Format the context as JSON string for gr.Code using our safe serializer
            debug_context_dict = result.get("debug_context", {})
            safe_context = safe_json_serialize(debug_context_dict)
            context_json_str = json.dumps(safe_context, indent=2)

            return formatted_results, logs_formatted, context_json_str
        finally:
            # Remove our handler to avoid duplication and memory leaks
            root_logger.removeHandler(log_handler)
            log_capture.close()

    # Using the global progress bar instead of a local indicator

    # Function to enable/disable execute button based on recipe content
    def update_execute_btn(recipe_content):
        # Enable button if recipe_content is not empty
        return gr.update(interactive=bool(recipe_content))

    # Set up event handler for recipe execution
    execute_btn.click(
        fn=execute_recipe_formatted,
        inputs=[recipe_file, recipe_text, context_vars],
        outputs=[result_output, logs_output, context_json],
        api_name="execute_recipe",
        show_progress="full",  # Show the progress bar during execution
    )

    # Enable execute button when recipe is loaded
    recipe_text.change(
        fn=update_execute_btn,
        inputs=[recipe_text],
        outputs=[execute_btn],
    )

    # When a file is uploaded, read the content and update the recipe_text
    def handle_file_upload(file_path):
        if file_path is None or not file_path:
            return "", gr.update(interactive=False)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            # Validate JSON
            json.loads(content)
            return content, gr.update(interactive=True)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error parsing uploaded file: {e}")
            return "", gr.update(interactive=False)

    # Handle file upload to update JSON content and button state
    recipe_file.change(
        fn=handle_file_upload,
        inputs=[recipe_file],
        outputs=[recipe_text, execute_btn],
    )


def setup_example_events(
    recipe_core: RecipeExecutorCore,
    example_paths: gr.Dropdown,
    load_example_btn: gr.Button,
    example_desc: gr.Markdown,
    recipe_text: gr.Code,
    context_vars: Optional[gr.Textbox] = None,
) -> None:
    """Set up event handlers for examples tab.

    Args:
        recipe_core: RecipeExecutorCore instance
        example_paths: Example paths dropdown
        load_example_btn: Load example button
        example_desc: Example description markdown
        recipe_text: Recipe JSON component
        context_vars: Optional context variables textbox
    """

    async def load_example_formatted(path: str) -> Tuple[str, str, Optional[str]]:
        """Format load_example output for Gradio UI."""
        result = await recipe_core.load_recipe(path)
        # Extract the individual fields for Gradio UI
        recipe_content_str = result.get("recipe_content", "")
        structure_preview = result.get("structure_preview", "")

        # Return the string content directly for gr.Code component
        recipe_content = recipe_content_str

        # Validate that it's valid JSON
        try:
            if recipe_content_str:
                json.loads(recipe_content_str)
        except json.JSONDecodeError:
            recipe_content = ""
            structure_preview = "### Error\nInvalid JSON in recipe file"

        # Set recipe_root context variable for examples
        recipe_context_vars = None
        if context_vars is not None and path:
            # Get the directory containing the recipe
            recipe_dir = os.path.dirname(path)
            recipe_context_vars = f"recipe_root={recipe_dir}"

        return recipe_content, structure_preview, recipe_context_vars

    outputs = [recipe_text, example_desc]
    if context_vars is not None:
        outputs.append(context_vars)

    load_example_btn.click(
        fn=load_example_formatted,
        inputs=[example_paths],
        outputs=outputs,
        api_name="load_example",
    )


# Note: The build_ui function has been moved to app.py as create_executor_block
# to better support component reuse in other Gradio applications


=== File: apps/recipe-executor/recipe_executor_app/utils.py ===
"""Utility functions for the Recipe Executor app."""

import json
import logging
import os
import tempfile
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Initialize logger
logger = logging.getLogger(__name__)


def get_repo_root() -> str:
    """Get the repository root directory.

    Returns:
        str: Path to the repository root
    """
    # Start from the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Keep going up until we find the repository root (where the pyproject.toml file is)
    while True:
        if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
            return current_dir

        # Move up one directory
        parent_dir = os.path.dirname(current_dir)

        # If we've reached the root of the file system, stop
        if parent_dir == current_dir:
            # If we can't find the repository root, return the current directory
            return os.path.dirname(os.path.abspath(__file__))

        current_dir = parent_dir


def resolve_path(path: str, root: Optional[str] = None, attempt_fixes: bool = True) -> str:
    """Resolve a path to an absolute path, optionally relative to a root.

    Args:
        path: Path to resolve
        root: Optional root directory to resolve relative to
        attempt_fixes: Whether to attempt fixing common path issues

    Returns:
        str: Absolute path
    """
    # First, check if it's already an absolute path
    if os.path.isabs(path):
        return path

    # Try multiple resolution strategies
    potential_paths = []

    # Base scenario: path relative to cwd
    potential_paths.append(os.path.abspath(path))

    # If root is provided, try relative to root
    if root:
        # Make sure root is absolute
        if not os.path.isabs(root):
            root = os.path.abspath(root)
        potential_paths.append(os.path.join(root, path))

    # Try relative to repo root
    repo_root = get_repo_root()
    potential_paths.append(os.path.join(repo_root, path))

    # Also try relative to repo root's parent (in case it's in a parent directory)
    parent_root = os.path.dirname(repo_root)
    potential_paths.append(os.path.join(parent_root, path))

    # If attempt_fixes is True, also try other common path patterns
    if attempt_fixes:
        # Handle paths that assume app root
        potential_paths.append(os.path.join(repo_root, "apps", "recipe-executor", path))

        # Try replacing excessive relative paths (../../) with direct repo root
        if path.startswith("../"):
            # Count the number of ../ at the beginning
            parts = path.split("/")
            up_count = 0
            for part in parts:
                if part == "..":
                    up_count += 1
                else:
                    break

            if up_count > 0:
                # Create a path relative to repo root instead
                relative_path = "/".join(parts[up_count:])
                potential_paths.append(os.path.join(repo_root, relative_path))

    # Try each potential path in order
    for potential_path in potential_paths:
        if os.path.exists(potential_path):
            logger.debug(f"Resolved path '{path}' to '{potential_path}'")
            return potential_path

    # If none of the paths exist, return the first one (best guess)
    logger.warning(f"Could not find path '{path}' (tried {potential_paths}), using best guess")
    return potential_paths[0]


def get_potential_paths(path: str) -> List[str]:
    """Get a list of potential paths that might correspond to the given path.

    Args:
        path: Path to resolve

    Returns:
        List[str]: List of potential paths
    """
    potential_paths = []

    # Direct path (as is)
    potential_paths.append(path)

    # Absolute path
    if not os.path.isabs(path):
        potential_paths.append(os.path.abspath(path))

    # Relative to repo root
    repo_root = get_repo_root()
    potential_paths.append(os.path.join(repo_root, path))

    # Try to handle paths with excessive "../"
    if path.startswith("../"):
        # Count the number of ../ at the beginning
        parts = path.split("/")
        up_count = 0
        for part in parts:
            if part == "..":
                up_count += 1
            else:
                break

        if up_count > 0:
            # Create a path relative to repo root instead
            relative_path = "/".join(parts[up_count:])
            potential_paths.append(os.path.join(repo_root, relative_path))

    # Try to handle common locations
    potential_paths.append(os.path.join(repo_root, "recipes", path))

    # Try with examples directory
    potential_paths.append(os.path.join(repo_root, "recipes", "example_simple", path))

    # Add more locations as needed

    # Remove any duplicates
    unique_paths = []
    for p in potential_paths:
        if p not in unique_paths:
            unique_paths.append(p)

    return unique_paths


def read_file(path: str) -> str:
    """Read content from a file.

    Args:
        path: Path to the file

    Returns:
        str: Content of the file
    """
    logger.info(f"Reading file: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.info(f"Successfully read {len(content)} bytes from {path}")
            return content
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise


def create_temp_file(content: str, prefix: str = "temp_", suffix: str = ".txt") -> Tuple[str, Callable[[], None]]:
    """Create a temporary file with the given content.

    Args:
        content: Content to write to the file
        prefix: Prefix for the temporary file name
        suffix: Suffix for the temporary file name

    Returns:
        Tuple[str, callable]: Path to the temporary file and a cleanup function
    """
    logger.info(f"Creating temporary file with prefix='{prefix}', suffix='{suffix}'")
    try:
        temp_file = tempfile.NamedTemporaryFile(mode="w+", prefix=prefix, suffix=suffix, delete=False, encoding="utf-8")
        temp_file.write(content)
        temp_file.close()
        logger.info(f"Created temporary file: {temp_file.name}")

        # Return the path and a cleanup function
        def cleanup_fn():
            try:
                os.unlink(temp_file.name)
                logger.info(f"Removed temporary file: {temp_file.name}")
            except OSError as e:
                logger.warning(f"Failed to remove temporary file {temp_file.name}: {e}")
                # Ignore errors when trying to remove the file
                pass

        return temp_file.name, cleanup_fn
    except Exception as e:
        logger.error(f"Error creating temporary file: {e}")
        raise


def parse_context_vars(context_str: Optional[str]) -> Dict[str, Any]:
    """Parse context variables from a string.

    Args:
        context_str: String of comma-separated key=value pairs

    Returns:
        Dict[str, Any]: Dictionary of context variables
    """
    if not context_str:
        return {}

    context_dict = {}
    pairs = context_str.split(",")

    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Try to parse as JSON if it looks like a JSON value
            if value.startswith("{") or value.startswith("[") or value.lower() in ("true", "false", "null"):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    # If it fails to parse as JSON, just use the string value
                    pass

            context_dict[key] = value
        else:
            # If there's no =, use the value as a key with an empty string value
            context_dict[pair.strip()] = ""

    return context_dict


def safe_json_serialize(obj: Any) -> Dict[str, Any]:
    """Convert a potentially complex object to a JSON-serializable dictionary.

    Args:
        obj: Object to serialize

    Returns:
        Dict[str, Any]: JSON-serializable dictionary
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Handle non-string keys
            safe_key = str(key)
            try:
                # Try normal JSON serialization
                json.dumps(value)
                result[safe_key] = value
            except (TypeError, OverflowError):
                # Fall back to string representation
                result[safe_key] = str(value)
        return result
    else:
        # For non-dict objects, convert to a dict with limited attributes
        try:
            # First try direct serialization
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            # Fall back to string representation
            if hasattr(obj, "__dict__"):
                return {
                    "__str__": str(obj),
                    "__type__": type(obj).__name__,
                    "__attrs__": safe_json_serialize(obj.__dict__),
                }
            else:
                return {"__str__": str(obj), "__type__": type(obj).__name__}


def parse_recipe_json(recipe_text: str) -> Dict[str, Any]:
    """Parse recipe JSON from text.

    Args:
        recipe_text: Recipe JSON as a string

    Returns:
        Dict[str, Any]: Parsed recipe JSON
    """
    try:
        return json.loads(recipe_text)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing recipe JSON: {e}")
        raise ValueError(f"Invalid recipe JSON: {e}")


def extract_recipe_content(content: Union[str, List[Any], Dict[str, Any]]) -> Optional[str]:
    """Extract recipe content from various formats.

    Args:
        content: Recipe content in various formats

    Returns:
        Optional[str]: Recipe content as a string, or None if not found
    """
    # If content is already a string, return it
    if isinstance(content, str):
        try:
            # Verify it's valid JSON
            json.loads(content)
            return content
        except json.JSONDecodeError:
            logger.warning("Content is a string but not valid JSON")
            return None

    # If content is a list with dictionaries that have 'content' key
    elif isinstance(content, list) and len(content) > 0:
        # Extract the first item
        item = content[0]
        if isinstance(item, dict) and "content" in item:
            # Extract content from the item
            return item["content"]

    # If content is a dictionary with a 'content' key
    elif isinstance(content, dict) and "content" in content:
        return content["content"]

    # No valid recipe found
    logger.warning(f"Could not extract recipe content from {type(content)}")
    return None


def format_context_for_display(context_dict: Dict[str, Any]) -> str:
    """Format context variables for display.

    Args:
        context_dict: Dictionary of context variables

    Returns:
        str: Formatted context variables as a JSON string
    """
    try:
        # Filter out oversized context values
        filtered_dict = {}
        for key, value in context_dict.items():
            # If it's a string and very large, truncate it for display
            if isinstance(value, str) and len(value) > 1000:
                filtered_dict[key] = value[:1000] + "... [truncated]"
            else:
                filtered_dict[key] = value

        # Format as JSON
        return json.dumps(filtered_dict, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error formatting context for display: {e}")
        return json.dumps({"error": f"Could not format context: {str(e)}"})


def format_recipe_results(results: Dict[str, str], execution_time: float = 0.0) -> str:
    """Format recipe execution results as markdown.

    Args:
        results: Dictionary of result strings
        execution_time: Execution time in seconds

    Returns:
        str: Formatted results as markdown
    """
    markdown = [f"### Recipe Execution Results\n\n**Execution Time**: {execution_time:.2f} seconds\n"]

    # Always display output_root if it's in the context
    # (This matches the behavior of the original Recipe Tool app)
    if "output_root" in results:
        markdown.append(f"**output_root**: {results['output_root']}\n")

    if not results:
        # Just show the execution time if no results were produced
        return "\n".join(markdown)

    # Add results
    for key, value in results.items():
        # Skip output_root as it's already displayed above
        if key == "output_root":
            continue

        # Format key as heading
        formatted_key = key.replace("_", " ").title()
        markdown.append(f"#### {formatted_key}\n")

        # Add the value
        if value:
            # Check if the value is already markdown
            if value.startswith("#") or "```" in value or "**" in value:
                # If so, add it directly
                markdown.append(value)
            else:
                # Otherwise, format as code block if it looks like code
                if (
                    value.startswith("{")
                    or value.startswith("[")
                    or "function" in value.lower()
                    or "class" in value.lower()
                ):
                    markdown.append(f"```\n{value}\n```")
                else:
                    markdown.append(value)
        else:
            markdown.append("*Empty result*")

        markdown.append("\n")

    return "\n".join(markdown)


def log_context_paths(context_dict: Dict[str, Any]) -> None:
    """Log important paths from context for debugging.

    Args:
        context_dict: Dictionary of context variables
    """
    # Log relevant path-related variables for debugging
    path_keys = ["input", "input_path", "output_root", "output_path", "recipe_path", "repo_root"]
    for key in path_keys:
        if key in context_dict:
            logger.debug(f"Context path '{key}': {context_dict[key]}")

    # Also log any other keys that look like paths
    for key, value in context_dict.items():
        if isinstance(value, str) and ("path" in key.lower() or "root" in key.lower() or "dir" in key.lower()):
            if key not in path_keys:  # Avoid duplicates
                logger.debug(f"Context path '{key}': {value}")


def find_recent_json_file(directory: str, max_age_seconds: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """Find the most recently modified JSON file in a directory.

    Args:
        directory: Directory to search in
        max_age_seconds: Maximum age of the file in seconds

    Returns:
        Tuple[Optional[str], Optional[str]]: Content and path of the file if found, (None, None) otherwise
    """
    import os
    import time

    # Resolve the directory path
    directory = resolve_path(directory)

    # Check if the directory exists
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.warning(f"Directory not found: {directory}")
        return None, None

    # Find all JSON files
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]
    if not json_files:
        logger.info(f"No JSON files found in directory: {directory}")
        return None, None

    # Get the newest file
    newest_file = max(json_files, key=os.path.getmtime)
    mod_time = os.path.getmtime(newest_file)
    current_time = time.time()

    # Check if it's recent enough
    if current_time - mod_time > max_age_seconds:
        logger.info(f"Most recent JSON file is older than {max_age_seconds} seconds: {newest_file}")
        return None, None

    # Read the file content
    try:
        content = read_file(newest_file)
        return content, newest_file
    except Exception as e:
        logger.error(f"Error reading recent JSON file {newest_file}: {e}")
        return None, None


