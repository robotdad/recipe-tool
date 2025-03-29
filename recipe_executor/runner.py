# runner.py
import json
import os
import re
import sys
from typing import Dict

from context import Context
from executor import Executor
from logger import init_logger
from models import Recipe
from utils import render_template


def load_recipe(recipe_path: str, context: Context) -> Recipe:
    """
    Load and render a recipe from a markdown file using Liquid template rendering.

    Args:
        recipe_path (str): Path to the recipe markdown file.
        context (Context): The execution context.

    Returns:
        Recipe: A validated Recipe object.

    Raises:
        ValueError: If the recipe cannot be loaded or parsed.
    """
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            content = f.read()
        rendered = render_template(content, context).strip()
        if rendered.startswith("{") or rendered.startswith("["):
            recipe_json = json.loads(rendered)
        else:
            match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", rendered, re.DOTALL)
            if not match:
                raise ValueError("No JSON recipe found in the markdown file.")
            recipe_json = json.loads(match.group(1))
        if isinstance(recipe_json, list):
            recipe_json = {"steps": recipe_json}
        recipe = Recipe.model_validate(recipe_json)
        return recipe
    except Exception as e:
        raise ValueError(f"Failed to load recipe from '{recipe_path}'. Error: {e}") from e


def run_executor(recipe_path: str, cli_context: Dict[str, str], log_dir: str) -> None:
    """
    Core logic for running the recipe executor.

    This function sets up the logger, builds the Context instance, loads the recipe,
    and executes it.

    Args:
        recipe_path (str): The path to the recipe markdown file.
        cli_context (Dict[str, str]): Context provided via the CLI.
        log_dir (str): The directory for log files.
    """
    logger = init_logger(log_dir)

    # Set defaults if not provided.
    if "input_root" not in cli_context:
        cli_context["input_root"] = os.getcwd()
    if "output_root" not in cli_context:
        cli_context["output_root"] = os.path.join(os.getcwd(), "output")

    # Build a Context instance.
    context = Context(
        input_root=cli_context["input_root"],
        output_root=cli_context["output_root"],
        extra={k: v for k, v in cli_context.items() if k not in ("input_root", "output_root")},
    )

    logger.info("Logger initialized.")

    try:
        recipe = load_recipe(recipe_path, context)
        logger.info("Recipe loaded and rendered successfully.")
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    try:
        executor = Executor(recipe, context, logger)
        executor.execute()
        logger.info("Recipe execution finished successfully.")
    except Exception as e:
        logger.error(f"Execution failed with error: {e}", exc_info=True)
        sys.exit(1)
