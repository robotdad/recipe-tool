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
