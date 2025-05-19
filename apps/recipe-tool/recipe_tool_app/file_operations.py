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
