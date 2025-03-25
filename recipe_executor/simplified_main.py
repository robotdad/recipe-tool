"""Command-line interface for the simplified Recipe Executor."""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional

from recipe_executor.constants import ExecutionStatus
from recipe_executor.core import RecipeExecutor
from recipe_executor.utils import logging as log_utils

# Setup logging
logger = log_utils.get_logger()


async def main():
    """Main entry point for the recipe executor."""
    import argparse

    parser = argparse.ArgumentParser(description="Recipe Executor")
    parser.add_argument("recipe_file", help="Path to the recipe file")
    parser.add_argument("--model", default="claude-3-7-sonnet-20250219", help="Default model to use")
    parser.add_argument("--provider", default="anthropic", help="Default model provider")
    parser.add_argument("--recipes-dir", default="recipes", help="Directory containing recipe files")
    parser.add_argument("--output-dir", default="output", help="Directory to output generated files to")
    parser.add_argument(
        "--cache-dir",
        default="cache",
        help="Directory for caching LLM responses, or 'none' to disable",
    )
    parser.add_argument("--temp", type=float, default=0.1, help="Default temperature setting")
    parser.add_argument(
        "--vars",
        action="append",
        help="Initial variables in the format name=value",
        default=[],
    )
    parser.add_argument(
        "--validation",
        choices=["minimal", "standard", "strict"],
        default="standard",
        help="Validation level",
    )
    parser.add_argument(
        "--interaction",
        choices=["none", "critical", "regular", "verbose"],
        default="critical",
        help="Interaction mode",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    print(f"Setting log level to: {args.log_level.upper()}")

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Handle cache directory
    cache_dir = None if args.cache_dir.lower() == "none" else args.cache_dir

    # Create the executor
    executor = RecipeExecutor(
        default_model_name=args.model,
        default_model_provider=args.provider,
        recipes_dir=args.recipes_dir,
        output_dir=args.output_dir,
        cache_dir=cache_dir,
        temp=args.temp,
        validation_level=args.validation,
        interaction_mode=args.interaction,
        log_level=log_level,
    )

    # Add initial variables from command line
    initial_vars = {}
    for var_str in args.vars:
        name, value = var_str.split("=", 1)
        # Try to convert to appropriate type
        try:
            # Try to parse as JSON
            initial_vars[name] = json.loads(value)
        except json.JSONDecodeError:
            # Fall back to string
            initial_vars[name] = value

    # Load and execute the recipe
    recipe = await executor.load_recipe(args.recipe_file)

    # Add initial variables
    if initial_vars:
        recipe.variables.update(initial_vars)

    # Execute the recipe
    result = await executor.execute_recipe(recipe)

    # Print the result - we don't need this since we have progress reporting
    # But we'll keep a simplified version for now
    if result.error:
        print(f"\nError: {result.error}")

    # Print variables marked for display (if any) or just the completion message
    if "_display_variables" in result.variables:
        display_vars = result.variables["_display_variables"]
        if isinstance(display_vars, list):
            print("\nOutput Variables:")
            for var_name in display_vars:
                if var_name in result.variables:
                    print(f"  {var_name}: {result.variables[var_name]}")


if __name__ == "__main__":
    asyncio.run(main())