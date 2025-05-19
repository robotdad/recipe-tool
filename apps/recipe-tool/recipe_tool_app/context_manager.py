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
