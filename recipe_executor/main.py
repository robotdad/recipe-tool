#!/usr/bin/env python3
import argparse

from runner import run_executor


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

    # Convert the list of context strings into a dictionary.
    cli_context = {}
    if args.context:
        for item in args.context:
            if "=" in item:
                key, value = item.split("=", 1)
                cli_context[key.strip()] = value.strip()

    run_executor(args.recipe_path, cli_context, args.log_dir)


if __name__ == "__main__":
    main()
