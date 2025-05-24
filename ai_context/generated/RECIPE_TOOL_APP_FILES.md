# apps/recipe-tool/recipe_tool_app

[collect-files]

**Search:** ['apps/recipe-tool/recipe_tool_app']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 5/23/2025, 12:34:00 PM
**Files:** 12

=== File: apps/recipe-tool/recipe_tool_app/__init__.py ===
"""Gradio web app for the Recipe Tool."""

__version__ = "0.1.0"


=== File: apps/recipe-tool/recipe_tool_app/app.py ===
"""Gradio web app for the Recipe Tool."""

import argparse
from typing import Any

from recipe_executor.logger import init_logger

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore
from recipe_tool_app.ui_components import build_ui

# Set up logging
logger = init_logger(settings.log_dir)
# Set logger level from settings
logger.setLevel(settings.log_level.upper())


def create_app() -> Any:
    """Create and return the Gradio app."""
    # Initialize the core functionality
    recipe_core = RecipeToolCore()

    # Build the UI around the core
    app = build_ui(recipe_core)

    return app


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


=== File: apps/recipe-tool/recipe_tool_app/config.py ===
"""Configuration settings for the Recipe Tool app."""

from typing import Any, Dict, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the Recipe Tool app."""

    # App settings
    app_title: str = "Recipe Tool"
    app_description: str = "A web interface for executing and creating recipes"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: Optional[int] = None  # Let Gradio find an available port
    # Queue is enabled by default in Gradio

    # MCP settings
    mcp_server: bool = True

    # Recipe tool settings
    recipe_creator_path: str = "../../../recipes/recipe_creator/create.json"
    log_dir: str = "logs"
    log_level: str = (
        "DEBUG"  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL - Set to DEBUG for detailed path information
    )

    # Example recipes paths
    example_recipes: List[str] = [
        "../../../recipes/example_simple/test_recipe.json",
        "../../../recipes/example_content_writer/generate_content.json",
        "../../../recipes/example_brave_search/search.json",
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_APP_", env_file=".env", env_file_encoding="utf-8", case_sensitive=False
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


=== File: apps/recipe-tool/recipe_tool_app/context_manager.py ===
"""Context management for the Recipe Tool app."""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from recipe_executor.context import Context

from recipe_tool_app.path_resolver import ensure_directory_exists, get_repo_root

# Initialize logger
logger = logging.getLogger(__name__)


def get_default_context() -> Dict[str, str]:
    """Get the default context dictionary with standard paths.

    Returns:
        Dict[str, str]: Default context with standard paths
    """
    logger.debug("Creating default context")

    repo_root = get_repo_root()
    default_paths = {
        "recipe_root": os.path.join(repo_root, "recipes"),
        "ai_context_root": os.path.join(repo_root, "ai_context"),
        "output_root": os.path.join(repo_root, "output"),
    }

    # Ensure output directory exists
    ensure_directory_exists(default_paths["output_root"])

    logger.debug(f"Default context created with paths: {default_paths}")
    return default_paths


def parse_context_string(context_str: Optional[str]) -> Dict[str, str]:
    """Parse a context string in the format key1=value1,key2=value2.

    Args:
        context_str: Context string in format "key1=value1,key2=value2"

    Returns:
        Dict[str, str]: Parsed context variables
    """
    context_vars = {}

    if not context_str:
        return context_vars

    logger.debug(f"Parsing context string: {context_str}")

    for item in context_str.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()
            context_vars[key] = value

    logger.debug(f"Parsed context variables: {context_vars}")
    return context_vars


def prepare_context(
    context_vars: Optional[str] = None, base_context: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], Context]:
    """Prepare recipe context from context variables string.

    Args:
        context_vars: Optional string of context variables in format "key1=value1,key2=value2"
        base_context: Optional base context to extend

    Returns:
        tuple: (context_dict, Context object)
    """
    logger.debug("Preparing context")

    # Start with empty dictionary or the provided base
    context_dict = base_context.copy() if base_context else {}

    # Add default paths if not already in the base context
    default_paths = get_default_context()
    for key, value in default_paths.items():
        if key not in context_dict:
            context_dict[key] = value

    # Parse user-provided context variables (these will override defaults)
    if context_vars:
        user_vars = parse_context_string(context_vars)

        # Log any overrides of default paths
        for key, value in user_vars.items():
            if key in default_paths:
                logger.debug(f"Overriding default path {key}: {default_paths[key]} -> {value}")

        # Update the context with user variables
        context_dict.update(user_vars)

    # Create Context object
    context = Context(artifacts=context_dict)

    logger.debug(f"Final context prepared with {len(context_dict)} variables")
    return context_dict, context


def update_context_with_files(context_dict: Dict[str, Any], files: Optional[List[str]]) -> Dict[str, Any]:
    """Update context with file references.

    Args:
        context_dict: Current context dictionary
        files: List of file paths

    Returns:
        Dict[str, Any]: Updated context dictionary
    """
    if not files:
        return context_dict

    logger.debug(f"Adding {len(files)} files to context")

    # Deep copy to avoid modifying the original
    updated_context = context_dict.copy()

    # Add reference files to context if provided
    updated_context["files"] = ",".join(files)

    logger.debug(f"Updated context with files: {updated_context['files']}")
    return updated_context


def update_context_with_input(context_dict: Dict[str, Any], input_path: str) -> Dict[str, Any]:
    """Update context with input file path.

    Args:
        context_dict: Current context dictionary
        input_path: Path to input file

    Returns:
        Dict[str, Any]: Updated context dictionary
    """
    logger.debug(f"Adding input path to context: {input_path}")

    # Deep copy to avoid modifying the original
    updated_context = context_dict.copy()

    # Add the idea path as the input context variable
    updated_context["input"] = input_path

    return updated_context


def log_context_paths(context_dict: Dict[str, Any]) -> None:
    """Log important paths from the context for debugging.

    Args:
        context_dict: Context dictionary
    """
    logger.info("Recipe Tool paths:")
    logger.info(f"  - Current working directory: {os.getcwd()}")
    logger.info(f"  - Repository root: {get_repo_root()}")
    logger.info("  - Context paths:")

    for key in ["recipe_root", "ai_context_root", "output_root"]:
        logger.info(f"    - {key}: {context_dict.get(key, 'Not set')}")

    # Log other important paths if they exist
    if "input" in context_dict:
        logger.info(f"    - input: {context_dict['input']}")
    if "output" in context_dict:
        logger.info(f"    - output: {context_dict['output']}")
    if "target_file" in context_dict:
        logger.info(f"    - target_file: {context_dict['target_file']}")


def extract_output_values(context: Dict[str, Any]) -> Dict[str, str]:
    """Extract output and result values from context.

    Args:
        context: Context dictionary

    Returns:
        Dict[str, str]: Dictionary containing only output and result values
    """
    logger.debug("Extracting output values from context")

    output_dict = {}

    for key, value in context.items():
        # Include only string values with output/result keys
        if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
            output_dict[key] = value

    logger.debug(f"Extracted {len(output_dict)} output values")
    return output_dict


=== File: apps/recipe-tool/recipe_tool_app/core.py ===
"""Core functionality for the Recipe Tool app."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from recipe_executor.context import Context
from recipe_executor.executor import Executor

from recipe_tool_app.config import settings
from recipe_tool_app.context_manager import (
    log_context_paths,
    prepare_context,
    update_context_with_files,
    update_context_with_input,
)
from recipe_tool_app.error_handler import handle_recipe_error
from recipe_tool_app.file_operations import (
    create_temp_file,
    find_recent_json_file,
    read_file,
)
from recipe_tool_app.path_resolver import (
    get_repo_root,
    resolve_path,
)
from recipe_tool_app.recipe_processor import (
    extract_recipe_content,
    format_context_for_display,
    format_recipe_results,
    generate_recipe_preview,
    parse_recipe_json,
)

# Initialize logger
logger = logging.getLogger(__name__)


class RecipeToolCore:
    """Core functionality for Recipe Tool operations."""

    def __init__(self, executor: Optional[Executor] = None):
        """Initialize with the executor.

        Args:
            executor: Optional Executor instance. If None, a new one will be created.
        """
        self.executor = executor if executor is not None else Executor(logger)

    @handle_recipe_error
    async def execute_recipe(
        self, recipe_file: Optional[str], recipe_text: Optional[str], context_vars: Optional[str]
    ) -> Dict:
        """
        Execute a recipe from a file upload or text input.

        Args:
            recipe_file: Optional path to a recipe JSON file
            recipe_text: Optional JSON string containing the recipe
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            dict: Contains formatted_results (markdown) and raw_json keys
        """
        # Prepare context from variables
        context_dict, context = prepare_context(context_vars)

        # Determine recipe source
        recipe_source = None
        if recipe_file:
            recipe_source = recipe_file
            logger.info(f"Executing recipe from file: {recipe_file}")
        elif recipe_text:
            recipe_source = recipe_text
            logger.info("Executing recipe from text input")
        else:
            return {
                "formatted_results": "### Error\nNo recipe provided. Please upload a file or paste the recipe JSON.",
                "raw_json": "{}",
                "debug_context": {},
            }

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
        for key, value in all_artifacts.items():
            # Only include string results or keys that look like outputs
            if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
                results[key] = value

        # Format the results for display
        markdown_output = format_recipe_results(results, execution_time)

        # Format the raw JSON for display
        raw_json = format_context_for_display(all_artifacts)

        return {"formatted_results": markdown_output, "raw_json": raw_json, "debug_context": all_artifacts}

    @handle_recipe_error
    async def create_recipe(
        self,
        idea_text: str,
        idea_file: Optional[str],
        reference_files: Optional[List[str]],
        context_vars: Optional[str],
    ) -> Dict:
        """
        Create a recipe from an idea text or file.

        Args:
            idea_text: Text describing the recipe idea
            idea_file: Optional path to a file containing the recipe idea
            reference_files: Optional list of paths to reference files
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            dict: Contains recipe_json and structure_preview keys
        """
        # Determine idea source
        idea_source = None
        cleanup_fn = None

        if idea_file:
            idea_source = idea_file
            logger.info(f"Creating recipe from idea file: {idea_file}")
        elif idea_text:
            # Create a temporary file to store the idea text
            idea_source, cleanup_fn = create_temp_file(idea_text, prefix="idea_", suffix=".md")
            logger.info(f"Creating recipe from idea text (saved to {idea_source})")
        else:
            return {
                "recipe_json": "",
                "structure_preview": "### Error\nNo idea provided. Please upload a file or enter idea text.",
                "debug_context": {"error": "No idea provided"},
            }

        try:
            # Prepare base context
            context_dict, context = prepare_context(context_vars)

            # Update context with reference files and input path
            if reference_files:
                context_dict = update_context_with_files(context_dict, reference_files)

            # Add the idea path as input
            context_dict = update_context_with_input(context_dict, idea_source)

            # Update the context with our new variables
            context = Context(artifacts=context_dict)

            # Path to the recipe creator recipe
            creator_recipe_path = os.path.join(os.path.dirname(__file__), settings.recipe_creator_path)
            creator_recipe_path = os.path.normpath(creator_recipe_path)

            logger.info(f"Looking for recipe creator at: {creator_recipe_path}")

            # Make sure the recipe creator recipe exists
            if not os.path.exists(creator_recipe_path):
                # Try a fallback approach - relative to repo root
                repo_root = get_repo_root()
                fallback_path = os.path.join(repo_root, "recipes/recipe_creator/create.json")
                logger.info(f"First path failed, trying fallback: {fallback_path}")

                if os.path.exists(fallback_path):
                    creator_recipe_path = fallback_path
                    logger.info(f"Found recipe creator at fallback path: {creator_recipe_path}")
                else:
                    return {
                        "recipe_json": "",
                        "structure_preview": f"### Error\nRecipe creator recipe not found at: {creator_recipe_path} or {fallback_path}",
                        "debug_context": {
                            "error": f"Recipe creator recipe not found: {creator_recipe_path} or {fallback_path}"
                        },
                    }

            # Log important paths for debugging
            log_context_paths(context_dict)

            # Execute the recipe creator
            start_time = os.times().elapsed
            await self.executor.execute(creator_recipe_path, context)
            execution_time = os.times().elapsed - start_time

            # Get the context dictionary after execution
            context_dict = context.dict()

            # Log the full context for debugging
            logger.debug(f"Final context after recipe creation: {context_dict}")

            # Try to extract recipe from context or find in files
            output_recipe = self._find_recipe_output(context_dict)

            # If no recipe found after all attempts
            if not output_recipe:
                logger.warning("No output recipe found in any location")
                return {
                    "recipe_json": "",
                    "structure_preview": "### Recipe created successfully\nBut no output recipe was found. Check the output directory for generated files.",
                    "debug_context": context_dict,
                }

            # Log the recipe content for debugging
            logger.info(f"Output recipe found, length: {len(output_recipe)}")
            logger.debug(f"Recipe content: {output_recipe[:500]}...")

            # Parse the recipe JSON
            try:
                recipe_json = parse_recipe_json(output_recipe)

                # Generate a preview of the recipe structure
                preview = generate_recipe_preview(recipe_json, execution_time)

                return {"recipe_json": output_recipe, "structure_preview": preview, "debug_context": context_dict}

            except (json.JSONDecodeError, TypeError) as e:
                # In case of any issues with JSON processing
                logger.error(f"Error parsing recipe JSON: {e}")
                logger.error(f"Recipe content causing error: {output_recipe[:500]}...")

                return {
                    "recipe_json": output_recipe,
                    "structure_preview": f"### Recipe Created\n\n**Execution Time**: {execution_time:.2f} seconds\n\nWarning: Output is not valid JSON format or contains non-serializable objects. Error: {str(e)}",
                    "debug_context": context_dict,
                }

        finally:
            # Clean up temporary file if created
            if cleanup_fn:
                cleanup_fn()

    def _find_recipe_output(self, context_dict: Dict[str, Any]) -> Optional[str]:
        """Find the recipe output from context or files.

        Args:
            context_dict: Context dictionary after recipe execution

        Returns:
            Optional[str]: Recipe content if found, None otherwise
        """
        output_recipe = None

        # 1. Check if generated_recipe is in context
        if "generated_recipe" in context_dict:
            output_recipe = extract_recipe_content(context_dict["generated_recipe"])
            if output_recipe:
                logger.info("Successfully extracted recipe from generated_recipe context variable")
                return output_recipe

        # 2. If not found in context, try looking for target file
        output_root = context_dict.get("output_root", "output")
        target_file = context_dict.get("target_file", "generated_recipe.json")

        # Log what we're looking for
        logger.info(f"Looking for recipe file. output_root={output_root}, target_file={target_file}")

        # Check specific target file first
        file_path = resolve_path(target_file, output_root)

        if os.path.exists(file_path):
            try:
                output_recipe = read_file(file_path)
                logger.info(f"Read recipe from output file: {file_path}")
                return output_recipe
            except Exception as e:
                logger.warning(f"Failed to read output file {file_path}: {e}")
        else:
            logger.warning(f"Output file not found at: {file_path}")

        # 3. If still not found, look for recently modified files
        content, path = find_recent_json_file(output_root)
        if content:
            logger.info(f"Using recipe from recent file: {path}")
            return content

        return None


=== File: apps/recipe-tool/recipe_tool_app/error_handler.py ===
"""Error handling utilities for the Recipe Tool app."""

import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional

# Initialize logger
logger = logging.getLogger(__name__)


def format_error_response(error: Exception, function_name: str) -> Dict[str, Any]:
    """Format an error response based on the type of operation.

    Args:
        error: The exception that was raised
        function_name: The name of the function that raised the exception

    Returns:
        Dict[str, Any]: Formatted error response
    """
    error_msg = f"### Error\n\n```\n{str(error)}\n```"

    # Use appropriate result format based on function name
    if "execute" in function_name:
        return {"formatted_results": error_msg, "raw_json": "{}", "debug_context": {"error": str(error)}}
    else:
        return {"recipe_json": "", "structure_preview": error_msg, "debug_context": {"error": str(error)}}


def log_error_with_context(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with additional context information.

    Args:
        logger: Logger instance
        error: The exception that was raised
        context: Optional context dictionary
    """
    logger.error(f"Error: {error}", exc_info=True)

    if context:
        # Log key context variables that might help debugging
        log_context = {k: v for k, v in context.items() if k in ["recipe_root", "output_root", "input", "target_file"]}
        logger.error(f"Context at error time: {log_context}")


def handle_recipe_error(func: Callable) -> Callable:
    """Decorator to standardize error handling for recipe operations.

    Args:
        func: The function to decorate

    Returns:
        Callable: Decorated function
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            log_error_with_context(logger, e)
            return format_error_response(e, func.__name__)

    # Handle non-async functions
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return asyncio.run(async_wrapper(*args, **kwargs))
        except Exception as e:
            log_error_with_context(logger, e)
            return format_error_response(e, func.__name__)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def is_recipe_execution_error(error: Exception) -> bool:
    """Check if an error is related to recipe execution.

    Args:
        error: The exception to check

    Returns:
        bool: True if the error is related to recipe execution
    """
    error_str = str(error).lower()

    # Check for common recipe execution error patterns
    execution_patterns = ["recipe", "executor", "step", "context", "llm", "generate", "invalid json", "missing field"]

    return any(pattern in error_str for pattern in execution_patterns)


def create_user_friendly_error(error: Exception) -> str:
    """Create a user-friendly error message.

    Args:
        error: The exception

    Returns:
        str: User-friendly error message
    """
    error_str = str(error)

    # Check for specific error types and provide friendly messages
    if "FileNotFoundError" in error_str:
        return "File not found. Please check that the file exists and the path is correct."
    elif "JSONDecodeError" in error_str:
        return "Invalid JSON format. Please check your recipe JSON syntax."
    elif "PermissionError" in error_str:
        return "Permission denied. Please check file permissions."
    elif is_recipe_execution_error(error):
        return f"Recipe execution error: {error_str}"
    else:
        return f"An error occurred: {error_str}"


class RecipeToolError(Exception):
    """Base exception class for Recipe Tool errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize with message and optional context.

        Args:
            message: Error message
            context: Optional context dictionary
        """
        super().__init__(message)
        self.context = context or {}

    def get_formatted_response(self) -> Dict[str, Any]:
        """Get formatted error response.

        Returns:
            Dict[str, Any]: Formatted error response
        """
        error_msg = f"### Error\n\n```\n{str(self)}\n```"
        return {"formatted_results": error_msg, "raw_json": "{}", "debug_context": {"error": str(self), **self.context}}


class RecipeNotFoundError(RecipeToolError):
    """Exception raised when a recipe file cannot be found."""

    pass


class RecipeParsingError(RecipeToolError):
    """Exception raised when a recipe cannot be parsed."""

    pass


class RecipeExecutionError(RecipeToolError):
    """Exception raised when a recipe execution fails."""

    pass


=== File: apps/recipe-tool/recipe_tool_app/example_handler.py ===
"""Example handling functionality for the Recipe Tool app."""

import json
import logging
import os
from typing import Dict, Tuple

from recipe_tool_app.error_handler import handle_recipe_error
from recipe_tool_app.file_operations import read_file
from recipe_tool_app.path_resolver import get_potential_paths, get_repo_root

# Initialize logger
logger = logging.getLogger(__name__)


@handle_recipe_error
async def load_example(example_path: str) -> Dict[str, str]:
    """Load an example recipe from the examples directory.

    Args:
        example_path: Path to the example recipe file

    Returns:
        dict: Contains recipe_content and description keys
    """
    if not example_path:
        return {"recipe_content": "", "description": "No example selected."}

    try:
        # Log the original path for debugging
        logger.info(f"Loading example from path: {example_path}")

        # Try to find the file using potential paths

        # Generate potential paths to try
        potential_paths = get_potential_paths(example_path)

        # Try each path until we find one that exists
        full_path = None
        for path in potential_paths:
            if os.path.exists(path):
                full_path = path
                logger.info(f"Found example at: {full_path}")
                break

        if not full_path:
            # Log all attempted paths for debugging
            logger.error(f"Failed to find example recipe. Tried the following paths: {potential_paths}")
            return {
                "recipe_content": "",
                "description": f"Error: Could not find example recipe. Please check paths: {example_path}",
            }

        # Read the content
        content = read_file(full_path)

        # Try to find README file with description
        dir_path = os.path.dirname(full_path)
        readme_path = os.path.join(dir_path, "README.md")
        desc = ""
        if os.path.exists(readme_path):
            desc = read_file(readme_path)

        return {
            "recipe_content": content,
            "description": desc or "No description available for this example.",
        }
    except Exception as e:
        logger.error(f"Error loading example: {e}")
        return {"recipe_content": "", "description": f"Error loading example: {str(e)}"}


async def load_example_formatted(path: str) -> Tuple[str, str]:
    """Load an example recipe and format for UI.

    Args:
        path: Path to the example recipe

    Returns:
        Tuple[str, str]: (recipe_content, description)
    """
    result = await load_example(path)
    # Ensure we return strings even if result contains None values
    return result.get("recipe_content", ""), result.get("description", "")


def find_examples_in_directory(directory: str) -> Dict[str, str]:
    """Find all JSON recipe examples in a directory.

    Args:
        directory: Directory to search in

    Returns:
        Dict[str, str]: Map of display names to file paths
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.warning(f"Example directory not found: {directory}")
        return {}

    examples = {}
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


=== File: apps/recipe-tool/recipe_tool_app/file_operations.py ===
"""File operations for the Recipe Tool app."""

import json
import logging
import os
import tempfile
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from recipe_tool_app.path_resolver import ensure_directory_exists

# Initialize logger
logger = logging.getLogger(__name__)


def read_file(file_path: str) -> str:
    """Read a file and return its contents as a string.

    Args:
        file_path: Path to the file to read

    Returns:
        str: File contents as a string

    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    logger.debug(f"Reading file: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            logger.debug(f"Read {len(content)} bytes from {file_path}")
            return content
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def write_file(file_path: str, content: str) -> str:
    """Write content to a file and return the file path.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        str: Path to the written file

    Raises:
        IOError: If there's an error writing the file
    """
    logger.debug(f"Writing to file: {file_path}")

    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            logger.debug(f"Wrote {len(content)} bytes to {file_path}")
        return file_path
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise


def find_recent_json_file(directory: str, max_age_seconds: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """Find the most recently modified JSON file in a directory.

    Args:
        directory: Directory to search in
        max_age_seconds: Maximum age of file in seconds

    Returns:
        tuple: (file_content, file_path) if found, (None, None) otherwise
    """
    logger.debug(f"Searching for recent JSON files in {directory} (max age: {max_age_seconds}s)")

    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return None, None

    try:
        # Find all JSON files
        json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]

        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return None, None

        # Get the newest file
        newest_file = max(json_files, key=os.path.getmtime)
        file_age = time.time() - os.path.getmtime(newest_file)

        # Check if it's recent enough
        if file_age > max_age_seconds:
            logger.warning(f"Most recent JSON file {newest_file} is {file_age:.2f} seconds old, skipping")
            return None, None

        # Read the file
        logger.info(f"Found recent JSON file: {newest_file}")
        content = read_file(newest_file)
        logger.info(f"Read content from {newest_file}")
        return content, newest_file

    except Exception as e:
        logger.warning(f"Error while searching for recent files: {e}")
        return None, None


def create_temp_file(content: str, prefix: str = "temp_", suffix: str = ".txt") -> Tuple[str, Callable[[], None]]:
    """Create a temporary file with the given content and return the path and a cleanup function.

    Args:
        content: Content to write to the temporary file
        prefix: Prefix for the temporary file name
        suffix: Suffix for the temporary file name

    Returns:
        Tuple[str, Callable[[], None]]: Tuple containing (file_path, cleanup_function)
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    logger.debug(f"Created temporary file: {temp_path}")

    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)

    def cleanup() -> None:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Removed temporary file: {temp_path}")

    return temp_path, cleanup


def list_files_with_extension(directory: str, extension: str = ".json") -> List[str]:
    """List all files with a given extension in a directory.

    Args:
        directory: Directory to search in
        extension: File extension to filter by (include the dot)

    Returns:
        List[str]: List of file paths
    """
    logger.debug(f"Listing files with extension {extension} in {directory}")

    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return []

    try:
        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]
    except Exception as e:
        logger.warning(f"Error listing files in {directory}: {e}")
        return []


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read a JSON file and parse its contents.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dict[str, Any]: Parsed JSON content

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    content = read_file(file_path)
    return json.loads(content)


def write_json_file(file_path: str, data: Dict[str, Any], indent: int = 2) -> str:
    """Write data to a JSON file.

    Args:
        file_path: Path to the JSON file
        data: Data to write to the file
        indent: JSON indentation level

    Returns:
        str: Path to the written file
    """
    content = json.dumps(data, indent=indent)
    return write_file(file_path, content)


def safe_delete_file(file_path: str) -> bool:
    """Safely delete a file if it exists.

    Args:
        file_path: Path to the file to delete

    Returns:
        bool: True if the file was deleted, False otherwise
    """
    if os.path.exists(file_path):
        try:
            os.unlink(file_path)
            logger.debug(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.warning(f"Error deleting file {file_path}: {e}")
            return False
    else:
        logger.debug(f"File does not exist, nothing to delete: {file_path}")
        return False


=== File: apps/recipe-tool/recipe_tool_app/path_resolver.py ===
"""Path resolution utilities for the Recipe Tool app."""

import logging
import os
from typing import List, Optional

# Initialize logger
logger = logging.getLogger(__name__)


def get_repo_root() -> str:
    """Get the absolute path to the repository root.

    Returns:
        str: Absolute path to the repository root directory
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def resolve_path(path: str, root: Optional[str] = None, attempt_fixes: bool = True) -> str:
    """Resolve a path to an absolute path, optionally relative to a root.

    Args:
        path: The path to resolve
        root: Optional root directory to resolve relative paths against
        attempt_fixes: Whether to attempt to fix common path resolution issues

    Returns:
        str: The absolute path
    """
    logger.debug(f"Resolving path: '{path}' (root: '{root}')")

    # Get repo root for reference
    repo_root = get_repo_root()
    logger.debug(f"Repository root: {repo_root}")

    # First, check if it's already an absolute path
    if os.path.isabs(path):
        logger.debug(f"Path is already absolute: {path}")
        return path

    # Normal case: relative to specified root or repo root
    resolved_path = None

    # Handle paths that are relative to repo root with ../ prefix
    if path.startswith("../") or path.startswith("../../"):
        # Start from repo root and navigate up as needed
        current_path = repo_root
        parts = path.split("/")

        # Count initial "../" parts to determine how many levels up to go
        up_levels = 0
        for part in parts:
            if part == "..":
                up_levels += 1
            else:
                break

        # Go up the required number of levels from repo root
        for _ in range(up_levels):
            current_path = os.path.dirname(current_path)

        # Join with the remainder of the path (excluding the "../" parts)
        resolved_path = os.path.join(current_path, *parts[up_levels:])
        logger.debug(f"Resolved ../ path to: {resolved_path}")
    elif root:
        # Relative to specified root
        if not os.path.isabs(root):
            root = os.path.join(repo_root, root)
        resolved_path = os.path.join(root, path)
        logger.debug(f"Resolved path relative to root: {resolved_path}")
    else:
        # Default: relative to repo root
        resolved_path = os.path.join(repo_root, path)
        logger.debug(f"Resolved path relative to repo root: {resolved_path}")

    # Check if the resolved path exists and attempt fixes if not
    if attempt_fixes and not os.path.exists(resolved_path):
        logger.debug(f"Resolved path does not exist, attempting fixes: {resolved_path}")

        # Try to fix using various strategies
        alt_path = _attempt_path_fixes(path, repo_root)
        if alt_path:
            return alt_path

    # Return the originally resolved path
    return resolved_path


def _attempt_path_fixes(path: str, repo_root: str) -> Optional[str]:
    """Attempt various fixes for a path that doesn't exist.

    Args:
        path: The original path string
        repo_root: The repository root path

    Returns:
        Optional[str]: Fixed path if successful, None otherwise
    """
    # Prepare potential alternatives
    alternatives = []

    # If path contains "recipes", try to resolve relative to the recipes directory
    if "recipes" in path:
        recipes_dir = os.path.join(repo_root, "recipes")

        # Get the part after "recipes/"
        if "recipes/" in path:
            after_recipes = path.split("recipes/", 1)[1]
            alternatives.append(os.path.join(recipes_dir, after_recipes))
            logger.debug(f"Added alternative from recipes/ split: {alternatives[-1]}")

        # Try with just the basename
        basename = os.path.basename(path)

        # Try finding the file recursively in the recipes directory
        for root, _, files in os.walk(recipes_dir):
            if basename in files:
                alternatives.append(os.path.join(root, basename))
                logger.debug(f"Found file by basename in recipes dir: {alternatives[-1]}")

    # If nothing found, try some common paths
    if not alternatives:
        # Try joining with recipes directory
        alternatives.append(os.path.join(repo_root, "recipes", path))
        logger.debug(f"Added recipes fallback: {alternatives[-1]}")

        # Try joining with recipe-tool directory
        alternatives.append(os.path.join(repo_root, "apps", "recipe-tool", path))
        logger.debug(f"Added recipe-tool fallback: {alternatives[-1]}")

    # Check alternatives
    for alt_path in alternatives:
        if os.path.exists(alt_path):
            logger.debug(f"Found existing alternative path: {alt_path}")
            return alt_path

    return None


def find_file_by_name(filename: str, search_dir: str, recursive: bool = True) -> Optional[str]:
    """Find a file by name in a directory, with optional recursive search.

    Args:
        filename: The filename to search for
        search_dir: The directory to search in
        recursive: Whether to search recursively

    Returns:
        Optional[str]: Full path to the file if found, None otherwise
    """
    logger.debug(f"Searching for file: {filename} in {search_dir}")

    if not os.path.exists(search_dir):
        logger.warning(f"Search directory does not exist: {search_dir}")
        return None

    if recursive:
        for root, _, files in os.walk(search_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                logger.debug(f"Found file: {file_path}")
                return file_path
    else:
        file_path = os.path.join(search_dir, filename)
        if os.path.exists(file_path):
            logger.debug(f"Found file: {file_path}")
            return file_path

    logger.debug(f"File not found: {filename}")
    return None


def ensure_directory_exists(path: str) -> str:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory

    Returns:
        str: Path to the directory
    """
    if not os.path.exists(path):
        logger.debug(f"Creating directory: {path}")
        os.makedirs(path, exist_ok=True)
    return path


def get_recipes_directory() -> str:
    """Get the path to the recipes directory.

    Returns:
        str: Path to the recipes directory
    """
    return os.path.join(get_repo_root(), "recipes")


def get_output_directory() -> str:
    """Get the path to the output directory.

    Returns:
        str: Path to the output directory
    """
    output_dir = os.path.join(get_repo_root(), "output")
    return ensure_directory_exists(output_dir)


def get_potential_paths(path: str) -> List[str]:
    """Generate a list of potential paths to try for a given path.

    Args:
        path: The original path

    Returns:
        List[str]: List of potential paths to try
    """
    repo_root = get_repo_root()
    recipe_root = os.path.join(repo_root, "recipes")

    return [
        # 1. Direct interpretation of the path
        path,
        # 2. Relative to repo root
        os.path.join(repo_root, path.lstrip("/")),
        # 3. Relative to recipe_root (replacing initial ../../recipes with recipe_root)
        os.path.join(recipe_root, path.replace("../../recipes/", "")),
        # 4. Relative to recipe_root (replacing initial ../../../recipes with recipe_root)
        os.path.join(recipe_root, path.replace("../../../recipes/", "")),
        # 5. Direct path in recipes directory
        os.path.join(recipe_root, os.path.basename(path)),
    ]


=== File: apps/recipe-tool/recipe_tool_app/recipe_processor.py ===
"""Recipe processing utilities for the Recipe Tool app."""

import json
import logging
from typing import Any, Dict, Optional, Tuple

# Initialize logger
logger = logging.getLogger(__name__)


def parse_recipe_json(recipe_content: str) -> Dict[str, Any]:
    """Parse recipe JSON and return a structured dictionary.

    Args:
        recipe_content: Recipe JSON as string

    Returns:
        dict: Parsed recipe JSON
    """
    logger.debug("Parsing recipe JSON")

    if not recipe_content:
        logger.warning("Empty recipe content")
        return {}

    # Make sure it's a string
    if not isinstance(recipe_content, str):
        if isinstance(recipe_content, (dict, list)):
            recipe_content = json.dumps(recipe_content, indent=2)
            logger.debug("Converted dict/list to JSON string")
        else:
            recipe_content = str(recipe_content)
            logger.debug("Converted non-string content to string")

    # Parse JSON
    try:
        parsed = json.loads(recipe_content)
        logger.debug("Successfully parsed recipe JSON")
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing recipe JSON: {e}")
        # Return empty dict on error
        return {}


def extract_recipe_content(generated_recipe: Any) -> Optional[str]:
    """Extract recipe content from various formats.

    Args:
        generated_recipe: Recipe in any supported format

    Returns:
        str: Recipe content if found, None otherwise
    """
    logger.debug(f"Extracting recipe content from {type(generated_recipe)}")

    if isinstance(generated_recipe, str):
        logger.debug("Recipe is already a string")
        return generated_recipe

    if isinstance(generated_recipe, list) and generated_recipe:
        item = generated_recipe[0]
        if isinstance(item, dict) and "content" in item:
            logger.debug("Extracted content from first item in list")
            return item["content"]

    if isinstance(generated_recipe, dict) and "content" in generated_recipe:
        logger.debug("Extracted content from dictionary")
        return generated_recipe["content"]

    logger.warning("Could not extract recipe content")
    return None


def generate_recipe_preview(recipe_json: Dict[str, Any], execution_time: float = 0.0) -> str:
    """Generate a markdown preview of a recipe structure.

    Args:
        recipe_json: Parsed recipe JSON
        execution_time: Optional execution time to include in the preview

    Returns:
        str: Markdown formatted preview
    """
    logger.debug("Generating recipe preview")

    # Create a markdown preview of the recipe structure
    preview = "### Recipe Structure\n\n"

    if execution_time > 0:
        preview += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

    if "name" in recipe_json:
        preview += f"**Name**: {recipe_json['name']}\n\n"

    if "description" in recipe_json:
        preview += f"**Description**: {recipe_json['description']}\n\n"

    if "steps" in recipe_json and isinstance(recipe_json["steps"], list):
        preview += f"**Steps**: {len(recipe_json['steps'])}\n\n"
        preview += "| # | Type | Description |\n"
        preview += "|---|------|-------------|\n"

        for i, step in enumerate(recipe_json["steps"]):
            step_type = step.get("type", "unknown")
            step_desc = ""

            if "config" in step and "description" in step["config"]:
                step_desc = step["config"]["description"]
            elif "description" in step:
                step_desc = step["description"]

            preview += f"| {i + 1} | {step_type} | {step_desc} |\n"

    logger.debug("Recipe preview generated successfully")
    return preview


def validate_recipe(recipe_json: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate a recipe JSON structure and return (is_valid, error_message).

    Args:
        recipe_json: Recipe JSON dictionary

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    logger.debug("Validating recipe")

    # Check for required fields
    if not recipe_json:
        return False, "Recipe is empty"

    if "steps" not in recipe_json:
        return False, "Recipe must contain 'steps' field"

    if not isinstance(recipe_json["steps"], list):
        return False, "'steps' field must be a list"

    # Validate each step
    for i, step in enumerate(recipe_json["steps"]):
        if not isinstance(step, dict):
            return False, f"Step {i + 1} must be a dictionary"

        if "type" not in step:
            return False, f"Step {i + 1} is missing required 'type' field"

    logger.debug("Recipe validation successful")
    return True, None


def format_recipe_results(results: Dict[str, Any], execution_time: float = 0.0) -> str:
    """Format recipe execution results as markdown.

    Args:
        results: Dictionary containing result data
        execution_time: Execution time in seconds

    Returns:
        str: Markdown formatted results
    """
    logger.debug("Formatting recipe results")

    if results:
        markdown_output = "### Recipe Execution Successful\n\n"

        if execution_time > 0:
            markdown_output += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

        markdown_output += "#### Results\n\n"

        for key, value in results.items():
            markdown_output += f"**{key}**:\n"
            # Check if value is JSON
            try:
                if isinstance(value, str):
                    json_obj = json.loads(value)
                    markdown_output += f"```json\n{json.dumps(json_obj, indent=2)}\n```\n\n"
                else:
                    # Already a dict or list
                    markdown_output += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
            except (json.JSONDecodeError, TypeError):
                # Not JSON, treat as regular text
                markdown_output += f"```\n{value}\n```\n\n"
    else:
        markdown_output = "### Recipe Execution Successful\n\n"

        if execution_time > 0:
            markdown_output += f"**Execution Time**: {execution_time:.2f} seconds\n\n"

        markdown_output += "No string results were found in the context."

    logger.debug("Recipe results formatted successfully")
    return markdown_output


def extract_results_from_context(context: Dict[str, Any]) -> Dict[str, str]:
    """Extract only the result/output entries from a context dictionary.

    Args:
        context: The full context dictionary

    Returns:
        Dict[str, str]: Dictionary containing only the results
    """
    logger.debug("Extracting results from context")

    results = {}
    for key, value in context.items():
        # Only include string results or keys that look like outputs
        if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
            results[key] = value

    logger.debug(f"Extracted {len(results)} results from context")
    return results


def format_context_for_display(context: Dict[str, Any]) -> str:
    """Format the context dictionary for display as JSON.

    Args:
        context: Context dictionary

    Returns:
        str: JSON formatted context
    """
    logger.debug("Formatting context for display")

    try:
        # Format raw JSON output using a simple default function to handle non-serializable types
        return json.dumps(context, indent=2, default=lambda o: str(o))
    except Exception as e:
        logger.error(f"Error formatting context: {e}")
        return "{}"


=== File: apps/recipe-tool/recipe_tool_app/ui_components.py ===
"""UI components for the Recipe Tool Gradio app."""

import json
import logging
from typing import List, Optional, Tuple

import gradio as gr
import gradio.themes

# Import recipe-executor components
from recipe_executor_app.app import create_executor_block
from recipe_executor_app.core import RecipeExecutorCore

from recipe_tool_app.config import settings
from recipe_tool_app.core import RecipeToolCore

# Initialize logger
logger = logging.getLogger(__name__)


def build_create_recipe_tab() -> Tuple[
    gr.TextArea, gr.File, gr.File, gr.Textbox, gr.Button, gr.Code, gr.Markdown, gr.JSON
]:
    """Build the Create Recipe tab UI components.

    Returns:
        Tuple: (idea_text, idea_file, reference_files, create_context_vars, create_btn,
               create_output, preview_md, create_debug_context)
    """
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")

            with gr.Tabs():
                with gr.TabItem("Text Input"):
                    idea_text = gr.TextArea(label="Idea Text", placeholder="Enter your recipe idea here...", lines=10)

                with gr.TabItem("File Input"):
                    idea_file = gr.File(label="Idea File", file_types=[".md", ".txt"])

            with gr.Accordion("Additional Options", open=False):
                reference_files = gr.File(
                    label="Reference Files",
                    file_types=[".md", ".txt", ".py", ".json"],
                    file_count="multiple",
                )
                create_context_vars = gr.Textbox(
                    label="Context Variables",
                    placeholder="key1=value1,key2=value2",
                    info="Add context variables as key=value pairs, separated by commas",
                )

            create_btn = gr.Button("Create Recipe", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### Output")
            with gr.Tabs():
                with gr.TabItem("Generated Recipe"):
                    create_output = gr.Code(language="json", label="Recipe JSON", lines=20, wrap_lines=True)
                with gr.TabItem("Preview"):
                    preview_md = gr.Markdown(label="Recipe Structure")
                with gr.TabItem("Context"):
                    create_debug_context = gr.JSON(label="Context Variables")

    return (
        idea_text,
        idea_file,
        reference_files,
        create_context_vars,
        create_btn,
        create_output,
        preview_md,
        create_debug_context,
    )


def setup_create_recipe_events(
    recipe_core: RecipeToolCore,
    idea_text: gr.TextArea,
    idea_file: gr.File,
    reference_files: gr.File,
    context_vars: gr.Textbox,
    create_btn: gr.Button,
    create_output: gr.Code,
    preview_md: gr.Markdown,
    debug_context: gr.JSON,
) -> None:
    """Set up event handlers for create recipe tab.

    Args:
        recipe_core: RecipeToolCore instance
        idea_text: Idea text textarea
        idea_file: Idea file upload component
        reference_files: Reference files upload component
        context_vars: Context variables textbox
        create_btn: Create button
        create_output: Generated recipe code component
        preview_md: Recipe structure preview markdown
        debug_context: Debug context code component
    """

    async def create_recipe_formatted(
        text: str, file: Optional[str], refs: Optional[List[str]], ctx: Optional[str]
    ) -> Tuple[str, str, str]:
        """Format create_recipe output for Gradio UI."""
        result = await recipe_core.create_recipe(text, file, refs, ctx)
        # Extract the individual fields for Gradio UI
        recipe_json = result.get("recipe_json", "")
        structure_preview = result.get("structure_preview", "")
        # Format debug context as JSON string
        debug_context = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
        return recipe_json, structure_preview, debug_context

    create_btn.click(
        fn=create_recipe_formatted,
        inputs=[idea_text, idea_file, reference_files, context_vars],
        outputs=[create_output, preview_md, debug_context],
        api_name="create_recipe",
    )


def build_ui(recipe_core: RecipeToolCore) -> gr.Blocks:
    """Build the complete Gradio UI.

    Args:
        recipe_core: RecipeToolCore instance for executing recipes

    Returns:
        gr.Blocks: Gradio Blocks interface
    """
    # Apply theme
    theme = gradio.themes.Soft() if settings.theme == "soft" else settings.theme

    with gr.Blocks(title=settings.app_title, theme=theme) as app:
        gr.Markdown("# Recipe Tool")
        gr.Markdown("A web interface for executing and creating recipes.")

        with gr.Tabs():
            # Create Recipe Tab
            with gr.TabItem("Create Recipe"):
                create_components = build_create_recipe_tab()
                (
                    idea_text,
                    idea_file,
                    reference_files,
                    create_context_vars,
                    create_btn,
                    create_output,
                    preview_md,
                    create_debug_context,
                ) = create_components

            # Use the dedicated recipe-executor component
            with gr.TabItem("Execute Recipe"):
                # Create a standalone recipe executor core
                executor_core = RecipeExecutorCore()

                # Create the executor block with no header (since we're in a tab)
                # We're using the block directly in the UI, so no need to assign it to a variable
                create_executor_block(executor_core, include_header=False)

                # Log success
                logger.info("Successfully created Recipe Executor component")

        # Set up event handlers for create recipe tab
        setup_create_recipe_events(
            recipe_core,
            idea_text,
            idea_file,
            reference_files,
            create_context_vars,
            create_btn,
            create_output,
            preview_md,
            create_debug_context,
        )

    return app


=== File: apps/recipe-tool/recipe_tool_app/utils.py ===
"""Utility functions for the Recipe Tool app."""

import logging
import os
import time
from typing import Any, Dict, Optional, Tuple

from recipe_executor.context import Context


def get_repo_root() -> str:
    """Get the absolute path to the repository root."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def resolve_path(path: str, root: Optional[str] = None, attempt_fixes: bool = True) -> str:
    """Resolve a path to an absolute path, optionally relative to a root.

    Args:
        path: The path to resolve
        root: Optional root directory to resolve relative paths against
        attempt_fixes: Whether to attempt to fix common path resolution issues

    Returns:
        str: The absolute path
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Resolving path: '{path}' (root: '{root}')")

    # Get repo root for reference
    repo_root = get_repo_root()
    logger.debug(f"Repository root: {repo_root}")

    # First, check if it's already an absolute path
    if os.path.isabs(path):
        logger.debug(f"Path is already absolute: {path}")
        return path

    # Normal case: relative to specified root or repo root
    resolved_path = None

    # Handle paths that are relative to repo root with ../ prefix
    if path.startswith("../") or path.startswith("../../"):
        # Start from repo root and navigate up as needed
        current_path = repo_root
        parts = path.split("/")

        # Count initial "../" parts to determine how many levels up to go
        up_levels = 0
        for part in parts:
            if part == "..":
                up_levels += 1
            else:
                break

        # Go up the required number of levels from repo root
        for _ in range(up_levels):
            current_path = os.path.dirname(current_path)

        # Join with the remainder of the path (excluding the "../" parts)
        resolved_path = os.path.join(current_path, *parts[up_levels:])
        logger.debug(f"Resolved ../ path to: {resolved_path}")
    elif root:
        # Relative to specified root
        if not os.path.isabs(root):
            root = os.path.join(repo_root, root)
        resolved_path = os.path.join(root, path)
        logger.debug(f"Resolved path relative to root: {resolved_path}")
    else:
        # Default: relative to repo root
        resolved_path = os.path.join(repo_root, path)
        logger.debug(f"Resolved path relative to repo root: {resolved_path}")

    # Check if the resolved path exists and attempt fixes if not
    if attempt_fixes and not os.path.exists(resolved_path):
        logger.debug(f"Resolved path does not exist, attempting fixes: {resolved_path}")

        # Prepare potential alternatives
        alternatives = []

        # If path contains "recipes", try to resolve relative to the recipes directory
        if "recipes" in path:
            recipes_dir = os.path.join(repo_root, "recipes")

            # Get the part after "recipes/"
            if "recipes/" in path:
                after_recipes = path.split("recipes/", 1)[1]
                alternatives.append(os.path.join(recipes_dir, after_recipes))
                logger.debug(f"Added alternative from recipes/ split: {alternatives[-1]}")

            # Try with just the basename
            basename = os.path.basename(path)

            # Try finding the file recursively in the recipes directory
            for root, _, files in os.walk(recipes_dir):
                if basename in files:
                    alternatives.append(os.path.join(root, basename))
                    logger.debug(f"Found file by basename in recipes dir: {alternatives[-1]}")

        # If nothing found, try some common paths
        if not alternatives:
            # Try joining with recipes directory
            alternatives.append(os.path.join(repo_root, "recipes", path))
            logger.debug(f"Added recipes fallback: {alternatives[-1]}")

            # Try joining with recipe-tool directory
            alternatives.append(os.path.join(repo_root, "apps", "recipe-tool", path))
            logger.debug(f"Added recipe-tool fallback: {alternatives[-1]}")

        # Check alternatives
        for alt_path in alternatives:
            if os.path.exists(alt_path):
                logger.debug(f"Found existing alternative path: {alt_path}")
                return alt_path

    # Return the originally resolved path
    return resolved_path


def prepare_context(context_vars: Optional[str] = None) -> Tuple[Dict[str, Any], Context]:
    """Prepare recipe context from context variables string.

    Args:
        context_vars: Optional string of context variables in format "key1=value1,key2=value2"

    Returns:
        tuple: (context_dict, Context object)
    """
    logger = logging.getLogger(__name__)

    # Start with empty dictionary
    context_dict = {}

    # Set up default paths
    repo_root = get_repo_root()
    default_paths = {
        "recipe_root": os.path.join(repo_root, "recipes"),
        "ai_context_root": os.path.join(repo_root, "ai_context"),
        "output_root": os.path.join(repo_root, "output"),
    }

    # Add default paths first
    context_dict.update(default_paths)

    # Parse user-provided context variables (these will override defaults)
    if context_vars:
        logger.debug(f"Parsing context variables: {context_vars}")
        for item in context_vars.split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Log if we're overriding a default path
                if key in default_paths:
                    logger.debug(f"Overriding default path {key}: {default_paths[key]} -> {value}")

                context_dict[key] = value

    # Ensure output directory exists
    os.makedirs(context_dict["output_root"], exist_ok=True)

    # Log all context variables for debugging
    logger.debug(f"Final context variables: {context_dict}")

    return context_dict, Context(artifacts=context_dict)


def extract_recipe_content(generated_recipe: Any) -> Optional[str]:
    """Extract recipe content from various formats.

    Args:
        generated_recipe: Recipe in any supported format

    Returns:
        str: Recipe content if found, None otherwise
    """
    if isinstance(generated_recipe, str):
        return generated_recipe

    if isinstance(generated_recipe, list) and generated_recipe:
        item = generated_recipe[0]
        if isinstance(item, dict) and "content" in item:
            return item["content"]

    if isinstance(generated_recipe, dict) and "content" in generated_recipe:
        return generated_recipe["content"]

    return None


def find_recent_json_file(directory: str, max_age_seconds: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """Find the most recently modified JSON file in a directory.

    Args:
        directory: Directory to search in
        max_age_seconds: Maximum age of file in seconds

    Returns:
        tuple: (file_content, file_path) if found, (None, None) otherwise
    """
    logger = logging.getLogger(__name__)

    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return None, None

    try:
        # Find all JSON files
        json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]

        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return None, None

        # Get the newest file
        newest_file = max(json_files, key=os.path.getmtime)
        file_age = time.time() - os.path.getmtime(newest_file)

        # Check if it's recent enough
        if file_age > max_age_seconds:
            logger.warning(f"Most recent JSON file {newest_file} is {file_age:.2f} seconds old, skipping")
            return None, None

        # Read the file
        logger.info(f"Found recent JSON file: {newest_file}")
        with open(newest_file, "r") as f:
            content = f.read()
            logger.info(f"Read content from {newest_file}")
            return content, newest_file

    except Exception as e:
        logger.warning(f"Error while searching for recent files: {e}")
        return None, None


def parse_recipe_json(recipe_content: str) -> Dict[str, Any]:
    """Parse recipe JSON and provide a structured preview.

    Args:
        recipe_content: Recipe JSON as string

    Returns:
        dict: Parsed recipe JSON
    """
    import json

    if not recipe_content:
        return {}

    # Make sure it's a string
    if not isinstance(recipe_content, str):
        if isinstance(recipe_content, (dict, list)):
            recipe_content = json.dumps(recipe_content, indent=2)
        else:
            recipe_content = str(recipe_content)

    # Parse JSON
    return json.loads(recipe_content)


def handle_recipe_error(func):
    """Decorator to standardize error handling for recipe operations."""
    import asyncio
    import functools
    import logging

    logger = logging.getLogger(__name__)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            error_msg = f"### Error\n\n```\n{str(e)}\n```"

            # Use appropriate result format based on function name
            if "execute" in func.__name__:
                return {"formatted_results": error_msg, "raw_json": "{}", "debug_context": {"error": str(e)}}
            else:
                return {"recipe_json": "", "structure_preview": error_msg, "debug_context": {"error": str(e)}}

    # Handle non-async functions
    if not asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(wrapper(*args, **kwargs))

        return sync_wrapper

    return wrapper


