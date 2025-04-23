import argparse
import asyncio
import sys
import time
import traceback
from typing import Dict, List

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_kv_list(entries: List[str], arg_name: str) -> Dict[str, str]:
    """
    Parse a list of key=value strings into a dictionary.

    Raises ValueError if any entry is not in key=value format.
    """
    result: Dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Invalid {arg_name} format '{entry}', expected key=value")
        key, value = entry.split("=", 1)
        if not key:
            raise ValueError(f"Invalid {arg_name} format '{entry}', key is empty")
        result[key] = value
    return result


async def run_execution(recipe_path: str, context: Context, logger) -> None:
    """
    Orchestrate the asynchronous execution of a recipe.
    """
    logger.info("Starting Recipe Executor Tool")
    logger.info(f"Executing recipe: {recipe_path}")
    start_time = time.time()
    executor = Executor(logger)
    await executor.execute(recipe_path, context)
    end_time = time.time()
    elapsed = end_time - start_time
    logger.info(f"Recipe executed successfully in {elapsed:.2f} seconds")


def main() -> None:
    """
    Main entry point for the Recipe Executor CLI.
    """
    # Load environment variables from .env, if present
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Recipe Executor: run JSON/YAML recipes with context and configuration."
    )
    parser.add_argument(
        "recipe_path",
        help="Path to the recipe file to execute."
    )
    parser.add_argument(
        "--log-dir",
        dest="log_dir",
        default="logs",
        help="Directory to store log files (default: 'logs')."
    )
    parser.add_argument(
        "--context",
        dest="context",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Context artifact values (can be repeated)."
    )
    parser.add_argument(
        "--config",
        dest="config",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Static config values (can be repeated)."
    )
    args = parser.parse_args()

    # Initialize logger
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {e}\n")
        sys.exit(1)

    # Parse context and config key/value arguments
    try:
        context_dict = parse_kv_list(args.context, "context")
        config_dict = parse_kv_list(args.config, "config")
    except ValueError as e:
        sys.stderr.write(f"Argument Error: {e}\n")
        sys.exit(1)

    # Debug log of parsed arguments and initial state
    logger.debug(
        f"Parsed arguments: recipe={args.recipe_path}, log_dir={args.log_dir}, "
        f"context={context_dict}, config={config_dict}"
    )

    # Create execution context
    context = Context(artifacts=context_dict, config=config_dict)

    # Run the asynchronous execution
    try:
        asyncio.run(run_execution(args.recipe_path, context, logger))
    except Exception as e:
        # Log and report any execution errors
        logger.error(
            f"An error occurred during recipe execution: {e}",
            exc_info=True
        )
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)

    # Normal exit
    sys.exit(0)


if __name__ == "__main__":
    main()
