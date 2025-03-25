"""File operation executor functions."""

import json
import os
from typing import Any, Dict, List, Optional

from recipe_executor.constants import StepType
from recipe_executor.context.simple_context import ExecutionContext
from recipe_executor.executors.registry import register_executor
from recipe_executor.models.step import RecipeStep
from recipe_executor.utils import logging as log_utils

logger = log_utils.get_logger("file")


@register_executor(StepType.FILE_READ)
async def execute_file_read(step: RecipeStep, context: ExecutionContext) -> Any:
    """Execute a file read step."""
    if not step.file_read:
        raise ValueError(f"Missing file_read configuration for step {step.id}")

    config = step.file_read
    path = context.interpolate_variables(config.path)
    encoding = config.encoding or "utf-8"
    is_binary = False  # FileInputConfig doesn't have a binary field, default to text
    
    # Handle pattern matching for multiple files
    if config.pattern:
        import glob
        
        pattern = context.interpolate_variables(config.pattern)
        base_dir = os.path.dirname(path) or "."
        full_pattern = os.path.join(base_dir, pattern)
        
        matching_files = glob.glob(full_pattern, recursive=True)
        logger.info(f"Found {len(matching_files)} files matching pattern: {full_pattern}")
        
        # Read all matching files
        results = {}
        for file_path in matching_files:
            try:
                mode = "rb" if is_binary else "r"
                with open(file_path, mode, encoding=None if is_binary else encoding) as f:
                    content = f.read()
                    
                # For binary files, we can't directly include them in the results
                if is_binary:
                    results[file_path] = f"<binary data, {len(content)} bytes>"
                else:
                    results[file_path] = content
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                results[file_path] = f"ERROR: {str(e)}"
        
        return results
    else:
        # Read single file
        try:
            logger.info(f"Reading file: {path}")
            mode = "rb" if is_binary else "r"
            with open(path, mode, encoding=None if is_binary else encoding) as f:
                content = f.read()
            
            # If JSON file, consider auto-parsing
            should_parse = False  # FileInputConfig doesn't have auto_parse field
            
            if not is_binary and should_parse and path.lower().endswith(".json"):
                try:
                    content = json.loads(content)
                    logger.info(f"Automatically parsed JSON from {path}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to auto-parse JSON from {path}: {e}")
            
            # Store the result in the specified variable
            result = content
            
            # Update logs to show where the data is being stored
            logger.info(f"Storing file content in variable: {config.as_variable}")
            
            return result
        except Exception as e:
            error_msg = f"Error reading file {path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)


@register_executor(StepType.FILE_WRITE)
async def execute_file_write(step: RecipeStep, context: ExecutionContext) -> Any:
    """Execute a file write step."""
    if not step.file_write:
        raise ValueError(f"Missing file_write configuration for step {step.id}")

    config = step.file_write
    path = context.interpolate_variables(config.path)
    
    # Get content from either direct content or content_variable
    if hasattr(config, "content") and config.content is not None:
        # Content might contain templates, so interpolate variables
        content = context.interpolate_variables(config.content)
    elif hasattr(config, "content_variable") and config.content_variable:
        var_name = config.content_variable
        content = context.get_variable(var_name)
        if content is None:
            raise ValueError(f"Variable '{var_name}' not found or has value None")
    else:
        raise ValueError(f"Neither content nor content_variable specified for file_write step {step.id}")
    
    # Determine file mode and encoding
    is_binary = False  # FileOutputConfig doesn't have a binary field
    encoding = config.encoding or "utf-8"
    mode = config.mode or "w"
    if is_binary and "b" not in mode:
        mode = mode + "b"
    
    # Create directory if it doesn't exist
    if config.mkdir:
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                error_msg = f"Error creating directory {directory}: {e}"
                logger.error(error_msg)
                raise ValueError(error_msg)
    
    # Write the file
    try:
        # Convert content to appropriate type if needed
        if isinstance(content, (dict, list)) and not is_binary:
            # Convert dict/list to JSON string
            content = json.dumps(content, indent=2, ensure_ascii=False)
            logger.info(f"Converted dict/list to JSON string for {path}")
        
        # Handle binary content
        if is_binary and isinstance(content, str):
            content = content.encode(encoding)
        
        with open(path, mode, encoding=None if is_binary else encoding) as f:
            f.write(content)
        
        logger.info(f"Wrote file: {path}")
        return {"path": path, "success": True}
    except Exception as e:
        error_msg = f"Error writing file {path}: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)