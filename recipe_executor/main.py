#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from typing import Dict, List

from context import Context
from executor import Executor
from logger import init_logger
from models import Recipe
from utils import render_template


def parse_context(context_list: List[str]) -> Dict[str, str]:
    """
    Parse a list of context strings (in key=value format) into a dictionary.
    """
    context: Dict[str, str] = {}
    if context_list:
        for item in context_list:
            if "=" in item:
                key, value = item.split("=", 1)
                context[key.strip()] = value.strip()
    return context


def load_recipe(recipe_path: str, context: Context) -> Recipe:
    """
    Load and render a recipe from a markdown file using Liquid template rendering.

    Renders the recipe using the context and parses it as JSON.
    """
    try:
        with open(recipe_path, "r", encoding="utf-8") as f:
            content = f.read()
        rendered = render_template(
            content, {**context.as_dict(), "input_root": context.input_root, "output_root": context.output_root}
        ).strip()
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


def main() -> None:
    """
    Main entry point for the Recipe Executor Tool.
    """
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Generates code based on a recipe using context for path values."
    )
    parser.add_argument("recipe_path", help="Path to the recipe markdown file")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", help="Additional context values as key=value pairs")
    args = parser.parse_args()

    logger = init_logger(args.log_dir)
    logger.info("Logger initialized.")

    cli_context = parse_context(args.context or [])
    # Set defaults if not provided.
    if "input_root" not in cli_context:
        cli_context["input_root"] = os.getcwd()
    if "output_root" not in cli_context:
        cli_context["output_root"] = os.path.join(os.getcwd(), "output")

    # Create a Context instance with required fields and extra values.
    context = Context(
        input_root=cli_context["input_root"],
        output_root=cli_context["output_root"],
        extra={k: v for k, v in cli_context.items() if k not in ("input_root", "output_root")},
    )

    logger.debug(f"Context: {context}")

    try:
        recipe = load_recipe(args.recipe_path, context)
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


if __name__ == "__main__":
    main()
