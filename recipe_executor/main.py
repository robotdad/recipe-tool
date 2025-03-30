#!/usr/bin/env python3
import argparse
import sys
from typing import Any, Dict

from context import Context
from executor import RecipeExecutor

from recipe_executor.logger import init_logger


def parse_context(context_args: list[str]) -> Dict[str, Any]:
    """
    Parse context key=value pairs from the CLI arguments.

    Args:
        context_args: List of context arguments as key=value strings.

    Returns:
        A dictionary with key-value pairs parsed from the arguments.

    Raises:
        ValueError: If any argument does not follow key=value format.
    """
    context: Dict[str, Any] = {}
    for item in context_args:
        if "=" in item:
            key, value = item.split("=", 1)
            context[key.strip()] = value.strip()
        else:
            raise ValueError(f"Invalid context argument '{item}'. Expected format key=value.")
    return context


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    """
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Executes a recipe with additional context information."
    )
    parser.add_argument("recipe_path", help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Additional context values as key=value pairs")
    args = parser.parse_args()

    # Parse the context key=value pairs
    try:
        cli_context = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Initialize logging
    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Create the Context object with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        executor = RecipeExecutor()
        executor.execute(args.recipe_path, context, logger=logger)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
