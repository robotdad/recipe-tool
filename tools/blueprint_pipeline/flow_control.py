#!/usr/bin/env python3
"""
Flow control module for the blueprint pipeline.

This module contains classes and functions for controlling the
flow of execution in the pipeline, including user interaction,
action state tracking, and flow control modes.
"""
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Tuple

from blueprint_pipeline.utils import safe_print


class FlowControl(Enum):
    """Control flow modes for the pipeline."""

    STEP_BY_STEP = auto()  # Pause after each step
    COMPONENT_COMPLETE = auto()  # Continue until current component completes
    ALL_COMPONENTS = auto()  # Continue until all components are processed
    UNTIL_COMPLETE = auto()  # Run everything to completion
    AUTO_MODE = auto()  # Never pause (set via CLI flag)
    RETRY = auto()  # Retry the last action
    RESUME = auto()  # Resume execution, skipping completed steps


@dataclass
class ActionState:
    """Tracks the state of the last action for retry purposes."""

    step_name: str = ""
    component_id: Optional[str] = None
    recipe_path: str = ""  # Default to empty string instead of Optional[str]
    context: Dict[str, str] = field(default_factory=dict)  # Use default_factory for mutable default


def pause_and_check(
    current_mode: FlowControl,
    action_state: ActionState,
    allow_component_option: bool = False,
    allow_all_components_option: bool = False,
    allow_until_complete_option: bool = False,
    allow_retry: bool = False,
) -> FlowControl:
    """
    Pause execution and ask user how to proceed.

    Args:
        current_mode: Current flow control mode
        action_state: Information about the current action
        allow_component_option: Whether to show "until component complete" option
        allow_all_components_option: Whether to show "until all components evaluated" option
        allow_until_complete_option: Whether to show "until complete" option
        allow_retry: Whether to show retry option

    Returns:
        FlowControl: New flow control mode
    """
    # If in auto mode, never pause
    if current_mode == FlowControl.AUTO_MODE:
        return current_mode

    # If in resume mode, don't pause (similar to auto mode but skips completed steps)
    if current_mode == FlowControl.RESUME:
        return current_mode

    # If in component complete mode, don't pause during component processing
    if current_mode == FlowControl.COMPONENT_COMPLETE and action_state.component_id and allow_component_option:
        return current_mode

    # If in all components mode, don't pause during component processing
    if current_mode == FlowControl.ALL_COMPONENTS and allow_all_components_option:
        return current_mode

    # If in until complete mode, don't pause
    if current_mode == FlowControl.UNTIL_COMPLETE and allow_until_complete_option:
        return current_mode

    # Display current step information
    safe_print("\n" + "=" * 80)
    safe_print(f"Completed: {action_state.step_name}")
    if action_state.component_id:
        safe_print(f"Component: {action_state.component_id}")
    safe_print("=" * 80)

    # Build options
    options = ["Continue to next step (default)"]
    if allow_retry and action_state.recipe_path:
        options.append("Retry this step")
    options.append("Resume execution (skip completed steps)")
    if allow_component_option and action_state.component_id:
        options.append("Continue until current component completes")
    if allow_all_components_option:
        options.append("Continue until all components are evaluated")
    if allow_until_complete_option:
        options.append("Continue until pipeline completes")
    options.append("Exit pipeline")

    # Display options
    safe_print("\nHow would you like to proceed?")
    for i, option in enumerate(options):
        safe_print(f"{i + 1}. {option}")

    # Get user choice
    choice = input("\nEnter choice (1-{}): ".format(len(options)))
    if not choice.strip():
        choice = "1"  # Default is next step

    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(options):
            raise ValueError("Invalid choice")
    except ValueError:
        safe_print("Invalid choice. Continuing to next step.")
        return FlowControl.STEP_BY_STEP

    # Handle choices
    # First option (index 0) is always "Continue to next step"
    if choice_idx == 0:
        return FlowControl.STEP_BY_STEP

    # Last option is always "Exit pipeline"
    if choice_idx == len(options) - 1:
        safe_print("Exiting pipeline at user request.")
        sys.exit(0)

    # Check if retry is the selected option
    current_option_idx = 1  # Start at the second option (index 1)
    if allow_retry and action_state.recipe_path:
        if choice_idx == current_option_idx:
            safe_print(f"Retrying step: {action_state.step_name}")
            return FlowControl.RETRY
        current_option_idx += 1

    # Check if resume is the selected option (always added after retry)
    if choice_idx == current_option_idx:
        safe_print("Resuming execution and skipping completed steps.")
        return FlowControl.RESUME
    current_option_idx += 1

    # Handle other options
    if allow_component_option and action_state.component_id and choice_idx == current_option_idx:
        return FlowControl.COMPONENT_COMPLETE
    elif allow_component_option and action_state.component_id:
        current_option_idx += 1

    if allow_all_components_option and choice_idx == current_option_idx:
        return FlowControl.ALL_COMPONENTS
    elif allow_all_components_option:
        current_option_idx += 1

    if allow_until_complete_option and choice_idx == current_option_idx:
        return FlowControl.UNTIL_COMPLETE

    # If we got here, something went wrong, just continue to next step
    return FlowControl.STEP_BY_STEP


def handle_human_review_feedback() -> Tuple[bool, str]:
    """
    Prompt for human intervention after components have been flagged for review.

    Returns:
        Tuple[bool, str]: (proceed, additional_context)
            - proceed: Whether to continue with the next iteration
            - additional_context: Additional context files to include
    """
    safe_print("\nPlease review the files in the human_review directory.")
    safe_print("After review, you can provide additional context files and continue.")

    proceed = input("Do you want to continue with the next iteration? (y/n): ")
    if proceed.lower() != "y":
        return False, ""

    # Optionally get additional context files
    additional_context = input(
        "Enter paths to additional context files (comma-separated, or press Enter to skip): "
    )

    return True, additional_context
