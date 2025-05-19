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
