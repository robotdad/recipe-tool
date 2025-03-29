#!/usr/bin/env python3
import argparse

from context import Context
from executor import RecipeExecutor

from recipe_executor.logger import init_logger


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments and calls the core runner function.
    """
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Generates code based on a recipe using context for path values."
    )
    parser.add_argument("recipe_path", help="Path to the recipe markdown file")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", help="Additional context values as key=value pairs")
    args = parser.parse_args()

    # Convert CLI --context values (key=value) to a dictionary
    cli_context = {}
    if args.context:
        for item in args.context:
            if "=" in item:
                key, value = item.split("=", 1)
                cli_context[key.strip()] = value.strip()

    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Inject CLI context values into Context.artifacts
    context = Context(artifacts=cli_context)

    executor = RecipeExecutor()
    executor.execute(args.recipe_path, context, logger=logger)


if __name__ == "__main__":
    main()
