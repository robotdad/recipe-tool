#!/usr/bin/env python3
"""
Configuration module for the blueprint pipeline.

This module contains functions for parsing command line arguments,
setting up directories, and managing context information.
"""
import argparse
import os
from typing import Dict


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the blueprint pipeline.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Blueprint-to-Code Generation Pipeline")

    # Required arguments
    parser.add_argument("--project_spec", required=True, help="Path to the project specification file")

    # Optional arguments
    parser.add_argument("--context_files", help="Comma-separated list of context files")
    parser.add_argument("--output_dir", default="output", help="Output directory")
    parser.add_argument("--model", default="openai:o3-mini", help="LLM model to use")
    parser.add_argument("--target_project", default="generated_project", help="Target project name")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--component_filter", help="Only process components matching this prefix")
    parser.add_argument("--max_iterations", type=int, default=3, help="Maximum number of refinement iterations")
    parser.add_argument("--auto", action="store_true", help="Run automatically without pausing")
    parser.add_argument("--max_workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--resume", action="store_true", help="Resume from a previous execution")

    return parser.parse_args()


def setup_directories(output_dir: str, target_project: str) -> None:
    """
    Create all necessary directories for the blueprint pipeline.

    Args:
        output_dir: Base output directory.
        target_project: Target project name.
    """
    # Create main output directories
    for subdir in ["analysis", "components", "evaluation", "clarification", "human_review", "blueprints", "code"]:
        os.makedirs(f"{output_dir}/{subdir}", exist_ok=True)

    # Create additional directories needed for the target project
    os.makedirs(f"{output_dir}/blueprints/{target_project}/components", exist_ok=True)
    os.makedirs(f"{output_dir}/blueprints/{target_project}/reports", exist_ok=True)
    os.makedirs(f"{output_dir}/code/{target_project}", exist_ok=True)


def get_base_context(args: argparse.Namespace) -> Dict[str, str]:
    """
    Create a base context dictionary with values passed to every recipe.

    Args:
        args: Parsed command line arguments.

    Returns:
        Dict[str, str]: Base context dictionary.
    """
    context = {}

    if args.project_spec:
        context["project_spec"] = args.project_spec

    if args.context_files:
        context["context_files"] = args.context_files

    if args.model:
        context["model"] = args.model

    return context
