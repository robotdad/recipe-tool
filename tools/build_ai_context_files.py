#!/usr/bin/env python3
"""
Build AI Context Files Script

This script imports the collect_files module and calls its functions directly
 to generate Markdown files containing code and recipe files for AI context.

This script should be placed at:
[repo_root]/tools/build_ai_context_files.py

And will be run from the repository root.
"""

import argparse
import os
import sys
import datetime
import re
import platform

OUTPUT_DIR = "ai_context/generated"

# We're running from repo root, so that's our current directory
global repo_root
repo_root = os.getcwd()

# Add the tools directory to the Python path
tools_dir = os.path.join(repo_root, "tools")
sys.path.append(tools_dir)

# Import the collect_files module
try:
    import collect_files  # type: ignore
except ImportError:
    print(f"Error: Could not import collect_files module from {tools_dir}")
    print("Make sure this script is run from the repository root.")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build AI Context Files script that collects project files into markdown."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always overwrite files, even if content unchanged",
    )
    return parser.parse_args()


def ensure_directory_exists(file_path) -> None:
    """Create directory for file if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def strip_date_line(text: str) -> str:
    """Remove any '**Date:** …' line so we can compare content ignoring timestamps."""
    # Remove the entire line that begins with **Date:**
    return re.sub(r'^\*\*Date:\*\*.*\n?', '', text, flags=re.MULTILINE)


def build_context_files(force=False) -> None:
    # Define the tasks to run
    tasks = [
        # Collect files from recipe_executor
        {
            "patterns": ["recipe_executor"],
            "output": f"{OUTPUT_DIR}/RECIPE_EXECUTOR_CODE_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": ["README.md", "pyproject.toml", ".env.example"],
        },
        # Collect files from recipes/recipe_executor
        {
            "patterns": ["recipes/recipe_executor"],
            "output": f"{OUTPUT_DIR}/RECIPE_EXECUTOR_RECIPE_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/recipe_creator
        {
            "patterns": ["recipes/recipe_creator"],
            "output": f"{OUTPUT_DIR}/RECIPE_CREATOR_RECIPE_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/utilities
        {
            "patterns": ["recipes/utilities"],
            "output": f"{OUTPUT_DIR}/UTILITIES_RECIPE_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from mcp-servers/python-code-tools
        {
            "patterns": ["mcp-servers/python-code-tools"],
            "output": f"{OUTPUT_DIR}/PYTHON_CODE_TOOLS_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/document_generator
        {
            "patterns": ["recipes/document_generator"],
            "output": f"{OUTPUT_DIR}/DOCUMENT_GENERATOR_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/examples_*
        {
            "patterns": ["recipes/example_*"],
            "output": f"{OUTPUT_DIR}/RECIPE_EXAMPLES_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/experimental/blueprint_generator_v3
        {
            "patterns": ["recipes/experimental/blueprint_generator_v3"],
            "output": f"{OUTPUT_DIR}/BLUEPRINT_GENERATOR_V3_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
        # Collect files from recipes/experimental/blueprint_generator_v4
        {
            "patterns": ["recipes/experimental/blueprint_generator_v4"],
            "output": f"{OUTPUT_DIR}/BLUEPRINT_GENERATOR_V4_FILES.md",
            "exclude": collect_files.DEFAULT_EXCLUDE,
            "include": [],
        },
    ]

    # Execute each task
    for task in tasks:
        patterns = task["patterns"]
        output = task["output"]
        exclude = task["exclude"]
        include = task["include"]

        # Ensure the output directory exists
        ensure_directory_exists(output)

        print(f"Collecting files for patterns: {patterns}")
        print(f"Excluding patterns: {exclude}")
        print(f"Including patterns: {include}")

        # Collect the files
        files = collect_files.collect_files(patterns, exclude, include)
        print(f"Found {len(files)} files.")

        # Build header
        now = datetime.datetime.now()
        # Use appropriate format specifiers based on the platform
        if platform.system() == 'Windows':
            date_str = now.strftime('%#m/%#d/%Y, %#I:%M:%S %p')  # Windows non-padding format
        else:
            date_str = now.strftime('%-m/%-d/%Y, %-I:%M:%S %p')  # Unix non-padding format
        header_lines = [
            f"# {' | '.join(patterns)}",
            "",
            "[collect-files]",
            "",
            f"**Search:** {patterns}",
            f"**Exclude:** {exclude}",
            f"**Include:** {include}",
            f"**Date:** {date_str}",
            f"**Files:** {len(files)}\n\n",
        ]
        header = "\n".join(header_lines)

        # Build content body
        content_body = ""
        for file in files:
            rel_path = os.path.relpath(file)
            content_body += f"=== File: {rel_path} ===\n"
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content_body += f.read()
            except Exception as e:
                content_body += f"[ERROR reading file: {e}]\n"
            content_body += "\n\n"

        new_content = header + content_body

        # If file exists and we're not forcing, compare (ignoring only the date)
        if os.path.exists(output) and not force:
            try:
                with open(output, "r", encoding="utf-8") as f:
                    existing_content = f.read()
                # Strip out date lines from both
                existing_sanitized = strip_date_line(existing_content).strip()
                new_sanitized = strip_date_line(new_content).strip()
                if existing_sanitized == new_sanitized:
                    print(f"No substantive changes in {output}, skipping write.")
                    continue
            except Exception as e:
                print(f"Warning: unable to compare existing file {output}: {e}")

        # Write the file (new or forced update)
        with open(output, "w", encoding="utf-8") as outfile:
            outfile.write(new_content)
        print(f"Written to {output}")


def main():
    args = parse_args()

    # Verify we're in the repository root by checking for key directories/files
    required_paths = [
        os.path.join(repo_root, "tools", "collect_files.py"),
        os.path.join(repo_root, "recipes"),
    ]

    missing_paths = [path for path in required_paths if not os.path.exists(path)]
    if missing_paths:
        print("Warning: This script should be run from the repository root.")
        print("The following expected paths were not found:")
        for path in missing_paths:
            print(f"  - {path}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    build_context_files(force=args.force)


if __name__ == "__main__":
    main()
