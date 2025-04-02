import argparse
import sys
from typing import Dict, List

from dotenv import load_dotenv

from executor import RecipeExecutor
from recipe_executor.context import Context
from recipe_executor.logger import init_logger


def parse_context(context_list: List[str]) -> Dict[str, str]:
    """
    Parse a list of key=value strings into a dictionary.

    Args:
        context_list (List[str]): List of context strings in key=value format.

    Returns:
        Dict[str, str]: Dictionary containing parsed context values.

    Raises:
        ValueError: If any context string is malformed or key is empty.
    """
    context: Dict[str, str] = {}
    for item in context_list:
        if "=" not in item:
            raise ValueError(f"Malformed context item: {item}. Expected format key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty key in context pair: {item}.")
        context[key] = value
    return context


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    This function parses command-line arguments, loads environment variables, sets up logging,
    creates a Context from CLI inputs, and executes the specified recipe.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Define command-line argument parser
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Executes a recipe with additional context information."
    )
    parser.add_argument("recipe_path", help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Additional context values as key=value pairs")
    args = parser.parse_args()

    # Parse context key=value pairs
    try:
        cli_context = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Initialize logging system
    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Create the execution context with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        # Execute the specified recipe
        executor = RecipeExecutor()
        executor.execute(args.recipe_path, context, logger=logger)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
