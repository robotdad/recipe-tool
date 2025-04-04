#!/usr/bin/env python3
"""
Executor module for the blueprint pipeline.

This module contains functions for executing recipes and steps
in the blueprint pipeline.
"""
import subprocess
from typing import Dict, Optional, Tuple

from blueprint_pipeline.flow_control import ActionState
from blueprint_pipeline.utils import safe_print


def run_recipe(recipe_path: str, context: Dict[str, str], verbose: bool = False) -> bool:
    """
    Run a recipe executor recipe with the given context.

    Args:
        recipe_path: Path to the recipe to execute.
        context: Context dictionary to pass to the recipe.
        verbose: Whether to show detailed output.

    Returns:
        bool: True if the recipe executed successfully, False otherwise.
    """
    cmd = ["python", "recipe_executor/main.py", recipe_path]

    if context:
        for key, value in context.items():
            cmd.extend(["--context", f"{key}={value}"])

    safe_print(f"Running: {' '.join(cmd)}")

    if verbose:
        # Show all output in real-time
        result = subprocess.run(cmd)
        success = result.returncode == 0
    else:
        # Only show summary
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        if success:
            safe_print(f"Recipe completed successfully: {recipe_path}")
        else:
            safe_print(f"Error running recipe: {result.stderr}")

    return success


def execute_step(
    recipe_path: Optional[str],
    context: Optional[Dict[str, str]],
    step_name: str,
    component_id: Optional[str],
    verbose: bool,
) -> Tuple[bool, ActionState]:
    """
    Execute a step and return a result and action state for possible retries.

    Args:
        recipe_path: Path to the recipe to execute (may be None for non-executable steps)
        context: Context for the recipe execution (may be None for non-executable steps)
        step_name: Name of the step (for display)
        component_id: Current component ID if applicable
        verbose: Whether to show detailed output

    Returns:
        Tuple[bool, ActionState]: Success status and action state
    """
    # For non-executable steps (status updates, etc.)
    if recipe_path is None or not recipe_path or context is None:
        action_state = ActionState(
            step_name=step_name,
            component_id=component_id,
            recipe_path="" if recipe_path is None else recipe_path,
            context={} if context is None else context,
        )
        return True, action_state

    # Add component_id to context if it's not already there and not None
    if component_id is not None and "component_id" not in context:
        context["component_id"] = component_id

    # Log context keys for debugging when verbose is True
    if verbose:
        safe_print(f"Context keys for {step_name}: {', '.join(context.keys())}")
        for key in ["component_id", "candidate_spec_path", "clarification_questions_path", "files", "context_files"]:
            if key in context:
                safe_print(f"  {key}: {context[key]}")

    # For normal executable steps
    success = run_recipe(recipe_path, context, verbose)

    # Create action state for possible retry
    action_state = ActionState(
        step_name=step_name, component_id=component_id, recipe_path=recipe_path, context=context.copy()
    )

    return success, action_state
