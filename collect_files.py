#!/usr/bin/env python3
"""
Collect Files Utility

Recursively scans the specified file/directory patterns and outputs a single Markdown
document containing each file's relative path and its contents.

Usage examples:
  # Collect all Python files in the current directory:
  python collect_files.py *.py > my_python_files.md

  # Collect all files in the 'output' directory:
  python collect_files.py output > my_output_dir_files.md

  # Collect specific files, excluding 'utils' and 'logs', but including Markdown files from 'utils':
  python collect_files.py *.py --exclude "utils,logs,__pycache__,*.pyc" --include "utils/*.md" > my_output.md
"""

import argparse
import fnmatch
import glob
import os

# Default exclude patterns: common directories and binary files to ignore.
DEFAULT_EXCLUDE = [".venv", "node_modules", ".git", "__pycache__", "*.pyc"]


def parse_patterns(pattern_str: str) -> list:
    """Splits a comma-separated string into a list of stripped patterns."""
    return [p.strip() for p in pattern_str.split(",") if p.strip()]


def should_exclude(rel_path: str, exclude_patterns: list) -> bool:
    """
    Returns True if any component of the relative path matches an exclude pattern.
    """
    parts = os.path.normpath(rel_path).split(os.sep)
    for pat in exclude_patterns:
        for part in parts:
            if fnmatch.fnmatch(part, pat):
                return True
    return False


def should_include(rel_path: str, include_patterns: list) -> bool:
    """
    Returns True if the relative path matches any of the include patterns.
    This is applied after exclusion, so a match here can bring a file back in.
    """
    for pat in include_patterns:
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def collect_files(patterns: list, exclude_patterns: list, include_patterns: list) -> list:
    """
    Collects file paths matching the given patterns, applying exclusion first.
    Files that match an include pattern are added back in.

    Returns a sorted list of absolute file paths.
    """
    collected = set()
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for path in matches:
            if os.path.isfile(path):
                rel_path = os.path.relpath(path)
                if should_exclude(rel_path, exclude_patterns) and not should_include(rel_path, include_patterns):
                    continue
                collected.add(os.path.abspath(path))
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    # Filter directories based on each directory name.
                    dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path)
                        if should_exclude(rel_path, exclude_patterns) and not should_include(
                            rel_path, include_patterns
                        ):
                            continue
                        collected.add(os.path.abspath(full_path))
    return sorted(collected)


def main():
    parser = argparse.ArgumentParser(
        description="Recursively collect files matching the given patterns and output a Markdown file with file names and contents."
    )
    parser.add_argument("patterns", nargs="+", help="File and/or directory patterns to collect (e.g. *.py or output)")
    parser.add_argument(
        "--exclude",
        type=str,
        default=",".join(DEFAULT_EXCLUDE),
        help="Comma-separated patterns to exclude (default: " + ",".join(DEFAULT_EXCLUDE) + ")",
    )
    parser.add_argument(
        "--include", type=str, default="", help="Comma-separated patterns to include (overrides excludes if matched)"
    )
    args = parser.parse_args()

    exclude_patterns = parse_patterns(args.exclude)
    include_patterns = parse_patterns(args.include) if args.include else []

    print(f"Scanning patterns: {args.patterns}")
    print(f"Excluding patterns: {exclude_patterns}")
    print(f"Including patterns: {include_patterns}")

    files = collect_files(args.patterns, exclude_patterns, include_patterns)
    print(f"Found {len(files)} files.\n")

    for file in files:
        rel_path = os.path.relpath(file)
        print(f"=== File: {rel_path} ===")
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            print(content)
        except Exception as e:
            print(f"[ERROR reading file: {e}]")
        print("\n")  # Extra newline between files


if __name__ == "__main__":
    main()
