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
