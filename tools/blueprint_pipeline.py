#!/usr/bin/env python3
import argparse
import glob
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Tuple


class FlowControl(Enum):
    """Control flow modes for the pipeline."""

    STEP_BY_STEP = auto()  # Pause after each step
    COMPONENT_COMPLETE = auto()  # Continue until current component completes
    ALL_COMPONENTS = auto()  # Continue until all components are processed
    UNTIL_COMPLETE = auto()  # Run everything to completion
    AUTO_MODE = auto()  # Never pause (set via CLI flag)
    RETRY = auto()  # Retry the last action


@dataclass
class ActionState:
    """Tracks the state of the last action for retry purposes."""

    step_name: str = ""
    component_id: Optional[str] = None
    recipe_path: str = ""  # Default to empty string instead of Optional[str]
    context: Dict[str, str] = field(default_factory=dict)  # Use default_factory for mutable default


def run_recipe(recipe_path: str, context: Dict[str, str], verbose: bool = False) -> bool:
    """Run a recipe executor recipe with the given context"""
    cmd = ["python", "recipe_executor/main.py", recipe_path]
    if context:
        for key, value in context.items():
            cmd.extend(["--context", f"{key}={value}"])

    print(f"Running: {' '.join(cmd)}")

    if verbose:
        # Show all output in real-time
        result = subprocess.run(cmd)
        success = result.returncode == 0
    else:
        # Only show summary
        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0
        if success:
            print(f"Recipe completed successfully: {recipe_path}")
        else:
            print(f"Error running recipe: {result.stderr}")

    return success


def needs_human_review(eval_file_path: str) -> bool:
    """Check if the evaluation file indicates the spec needs human review"""
    return "_needs_clarification" in eval_file_path


def find_latest_spec(component_id: str, output_dir: str) -> Optional[str]:
    """Find the latest spec file for a component, looking first in clarification, then in components"""
    # Check for revised specs first
    revised_specs = glob.glob(f"{output_dir}/clarification/{component_id}_candidate_spec_revised.md")
    if revised_specs:
        # Sort by modification time to get the latest one
        return sorted(revised_specs, key=os.path.getmtime)[-1]

    # Then check original specs
    original_specs = glob.glob(f"{output_dir}/components/{component_id}_candidate_spec.md")
    if original_specs:
        return original_specs[0]

    return None


def get_base_context(args):
    """Create a base context dictionary with values passed to every recipe"""
    context = {}
    if args.project_spec:
        context["project_spec"] = args.project_spec
    if args.context_files:
        context["context_files"] = args.context_files
    if args.model:
        context["model"] = args.model
    return context


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
    print("\n" + "=" * 80)
    print(f"Completed: {action_state.step_name}")
    if action_state.component_id:
        print(f"Component: {action_state.component_id}")
    print("=" * 80)

    # Build options
    options = ["Continue to next step (default)"]
    if allow_retry and action_state.recipe_path:
        options.append("Retry this step")
    if allow_component_option and action_state.component_id:
        options.append("Continue until current component completes")
    if allow_all_components_option:
        options.append("Continue until all components are evaluated")
    if allow_until_complete_option:
        options.append("Continue until pipeline completes")
    options.append("Exit pipeline")

    # Display options
    print("\nHow would you like to proceed?")
    for i, option in enumerate(options):
        print(f"{i + 1}. {option}")

    # Get user choice
    choice = input("\nEnter choice (1-{}): ".format(len(options)))
    if not choice.strip():
        choice = "1"  # Default is next step

    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(options):
            raise ValueError("Invalid choice")
    except ValueError:
        print("Invalid choice. Continuing to next step.")
        return FlowControl.STEP_BY_STEP

    # Handle choices
    # First option (index 0) is always "Continue to next step"
    if choice_idx == 0:
        return FlowControl.STEP_BY_STEP

    # Last option is always "Exit pipeline"
    if choice_idx == len(options) - 1:
        print("Exiting pipeline at user request.")
        sys.exit(0)

    # Check if retry is the selected option
    current_option_idx = 1  # Start at the second option (index 1)
    if allow_retry and action_state.recipe_path:
        if choice_idx == current_option_idx:
            print(f"Retrying step: {action_state.step_name}")
            return FlowControl.RETRY
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

    # Log context keys for debugging when verbose is True
    if verbose:
        print(f"Context keys for {step_name}: {', '.join(context.keys())}")
        for key in ["candidate_spec_path", "clarification_questions_path", "files", "context_files"]:
            if key in context:
                print(f"  {key}: {context[key]}")

    # For normal executable steps
    success = run_recipe(recipe_path, context, verbose)

    # Create action state for possible retry
    action_state = ActionState(
        step_name=step_name, component_id=component_id, recipe_path=recipe_path, context=context.copy()
    )

    return success, action_state


def main():
    parser = argparse.ArgumentParser(description="Blueprint-to-Code Generation Pipeline")
    parser.add_argument("--project_spec", required=True, help="Path to the project specification file")
    parser.add_argument("--context_files", help="Comma-separated list of context files")
    parser.add_argument("--output_dir", default="output", help="Output directory")
    parser.add_argument("--model", default="openai:o3-mini", help="LLM model to use")
    parser.add_argument("--target_project", default="generated_project", help="Target project name")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--component_filter", help="Only process components matching this prefix")
    parser.add_argument("--max_iterations", type=int, default=3, help="Maximum number of refinement iterations")
    parser.add_argument("--auto", action="store_true", help="Run automatically without pausing")
    args = parser.parse_args()

    # Initialize flow control mode
    flow_mode = FlowControl.AUTO_MODE if args.auto else FlowControl.STEP_BY_STEP

    # Initialize action state for retries
    last_action = ActionState()

    # Create base context with common parameters
    base_context = get_base_context(args)

    # Create output directories
    for subdir in ["analysis", "components", "evaluation", "clarification", "human_review", "blueprints", "code"]:
        os.makedirs(f"{args.output_dir}/{subdir}", exist_ok=True)

    # Create additional directories needed for the target project
    os.makedirs(f"{args.output_dir}/blueprints/{args.target_project}/components", exist_ok=True)
    os.makedirs(f"{args.output_dir}/blueprints/{args.target_project}/reports", exist_ok=True)
    os.makedirs(f"{args.output_dir}/code/{args.target_project}", exist_ok=True)

    # Track completion status for components
    component_status = {}  # component_id -> "complete" or "needs_review"

    iteration_count = 0
    all_complete = False

    while not all_complete and iteration_count < args.max_iterations:
        iteration_count += 1
        print(f"\n=== Starting Iteration {iteration_count} ===")

        # Only run project analysis and split to components on first iteration
        if iteration_count == 1:
            # Step 1: Project Split Analysis
            print("\n=== Step 1: Project Split Analysis ===")
            context = base_context.copy()
            context.update({
                "input": args.project_spec,
                "files": args.context_files,
                "output_root": f"{args.output_dir}/analysis",
            })

            # Handle retry logic - if in retry mode, reuse last_action
            if flow_mode == FlowControl.RETRY and last_action.step_name == "Project Split Analysis":
                print("Retrying: Project Split Analysis")
                success, _ = execute_step(
                    last_action.recipe_path,
                    last_action.context,
                    last_action.step_name,
                    last_action.component_id,
                    args.verbose,
                )
                # Reset flow mode after retry
                flow_mode = FlowControl.STEP_BY_STEP
            else:
                # Normal execution
                success, last_action = execute_step(
                    "recipes/utilities/project_split_analysis.json",
                    context,
                    "Project Split Analysis",
                    None,
                    args.verbose,
                )

            if not success:
                print("Project split analysis failed. Exiting.")
                return

            # Pause after project analysis
            flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True, allow_retry=True)

            # If retry requested, continue from the top of the loop
            if flow_mode == FlowControl.RETRY:
                continue

            analysis_file = f"{args.output_dir}/analysis/project_component_breakdown_analysis.md"
            if not os.path.exists(analysis_file):
                print(f"Expected output file not found: {analysis_file}")
                return

            # Step 2: Split to Components
            # FIXED: Parameter handling to match recipe expectations
            print("\n=== Step 2: Split to Components ===")
            context = {}
            # Only add model from base context to avoid incorrect parameters
            if "model" in base_context:
                context["model"] = base_context["model"]

            # Set the expected parameters for split_to_components recipe
            # Create a combined files parameter including project_spec and context_files
            files_param = args.project_spec
            if args.context_files:
                files_param = f"{files_param},{args.context_files}"

            context.update({
                "input": analysis_file,
                # Combine project_spec and context_files for the "files" parameter
                "files": files_param,
                "output_root": f"{args.output_dir}/components",
            })

            # Handle retry logic
            if flow_mode == FlowControl.RETRY and last_action.step_name == "Split to Components":
                print("Retrying: Split to Components")
                success, _ = execute_step(
                    last_action.recipe_path,
                    last_action.context,
                    last_action.step_name,
                    last_action.component_id,
                    args.verbose,
                )
                # Reset flow mode after retry
                flow_mode = FlowControl.STEP_BY_STEP
            else:
                # Normal execution
                success, last_action = execute_step(
                    "recipes/utilities/split_to_components.json", context, "Split to Components", None, args.verbose
                )

            if not success:
                print("Split to components failed. Exiting.")
                return

            # Pause after split to components
            flow_mode = pause_and_check(
                flow_mode,
                last_action,
                allow_all_components_option=True,
                allow_until_complete_option=True,
                allow_retry=True,
            )

            # If retry requested, continue from the top of the loop
            if flow_mode == FlowControl.RETRY:
                continue

        # Get all component specs to process in this iteration
        component_specs = []

        # If first iteration, get from components directory
        if iteration_count == 1:
            component_specs = glob.glob(f"{args.output_dir}/components/*_candidate_spec.md")
            # Initialize status tracking
            for spec in component_specs:
                component_id = os.path.basename(spec).replace("_candidate_spec.md", "")
                component_status[component_id] = "incomplete"
        else:
            # For subsequent iterations, process components that need review
            for component_id, status in component_status.items():
                if status == "needs_review":
                    spec_path = find_latest_spec(component_id, args.output_dir)
                    if spec_path:
                        component_specs.append(spec_path)

        if not component_specs:
            print("No component specifications were found to process.")
            if iteration_count == 1:
                return
            else:
                print("All components have been completed successfully.")
                all_complete = True
                continue

        # Apply component filter if specified
        if args.component_filter:
            component_specs = [
                spec for spec in component_specs if os.path.basename(spec).startswith(args.component_filter)
            ]
            if not component_specs:
                print(f"No components match the filter: {args.component_filter}")
                return

        print(f"Processing {len(component_specs)} component specifications in iteration {iteration_count}.")

        # Components needing human review in this iteration
        human_review_needed = []

        # Process each component
        for spec_path in component_specs:
            component_id = (
                os.path.basename(spec_path).replace("_candidate_spec.md", "").replace("_candidate_spec_revised.md", "")
            )
            print(f"\n=== Processing Component: {component_id} ===")

            # Step 3: ALWAYS Generate Clarification Questions first
            print(f"Generating clarification questions for {component_id}")
            # FIXED: Only include necessary parameters for generate_clarification_questions
            context = {"candidate_spec_path": spec_path, "output_root": f"{args.output_dir}/clarification"}
            # Add model if present in base context
            if "model" in base_context:
                context["model"] = base_context["model"]

            # Handle retry logic
            step_name = f"Generate Clarification Questions for {component_id}"
            if flow_mode == FlowControl.RETRY and last_action.step_name == step_name:
                print(f"Retrying: {step_name}")
                success, _ = execute_step(
                    last_action.recipe_path,
                    last_action.context,
                    last_action.step_name,
                    last_action.component_id,
                    args.verbose,
                )
                # Reset flow mode after retry
                flow_mode = FlowControl.STEP_BY_STEP
            else:
                # Normal execution
                success, last_action = execute_step(
                    "recipes/blueprint_generator/generate_clarification_questions.json",
                    context,
                    step_name,
                    component_id,
                    args.verbose,
                )

            if not success:
                print(f"Failed to generate clarification questions. Skipping {component_id}.")
                human_review_needed.append((component_id, spec_path, "Failed to generate questions"))
                component_status[component_id] = "needs_review"
                continue

            # Pause after generating questions
            flow_mode = pause_and_check(
                flow_mode,
                last_action,
                allow_component_option=True,
                allow_all_components_option=True,
                allow_until_complete_option=True,
                allow_retry=True,
            )

            # If retry requested, continue retry loop
            if flow_mode == FlowControl.RETRY:
                # Decrement the component counter to retry this component
                continue

            questions_file = f"{args.output_dir}/clarification/{component_id}_component_clarification_questions.md"
            if not os.path.exists(questions_file):
                print(f"Expected questions file not found: {questions_file}")
                human_review_needed.append((component_id, spec_path, "Questions file not found"))
                component_status[component_id] = "needs_review"
                continue

            # Step 4: Generate Clarification Answers
            print(f"Generating clarification answers for {component_id}")
            # Add project_spec to files parameter for generate_clarification_answers
            files_param = args.project_spec
            if args.context_files:
                files_param = f"{files_param},{args.context_files}"

            context = {
                "candidate_spec_path": spec_path,
                "clarification_questions_path": questions_file,
                "context_files": files_param,
                "output_root": f"{args.output_dir}/clarification",
                "component_id": component_id  # Explicitly pass component_id to ensure proper file naming
            }
            # Add model if present in base context
            if "model" in base_context:
                context["model"] = base_context["model"]

            # Handle retry logic
            step_name = f"Generate Clarification Answers for {component_id}"
            if flow_mode == FlowControl.RETRY and last_action.step_name == step_name:
                print(f"Retrying: {step_name}")
                success, _ = execute_step(
                    last_action.recipe_path,
                    last_action.context,
                    last_action.step_name,
                    last_action.component_id,
                    args.verbose,
                )
                # Reset flow mode after retry
                flow_mode = FlowControl.STEP_BY_STEP
            else:
                # Normal execution
                success, last_action = execute_step(
                    "recipes/blueprint_generator/generate_clarification_answers.json",
                    context,
                    step_name,
                    component_id,
                    args.verbose,
                )

            if not success:
                print(f"Failed to generate clarification answers. Skipping {component_id}.")
                human_review_needed.append((component_id, spec_path, "Failed to generate answers"))
                component_status[component_id] = "needs_review"
                continue

            # Pause after generating answers
            flow_mode = pause_and_check(
                flow_mode,
                last_action,
                allow_component_option=True,
                allow_all_components_option=True,
                allow_until_complete_option=True,
                allow_retry=True,
            )

            # If retry requested, continue retry loop
            if flow_mode == FlowControl.RETRY:
                continue

            revised_spec = f"{args.output_dir}/clarification/{component_id}_candidate_spec_revised.md"
            if not os.path.exists(revised_spec):
                print(f"Expected revised spec not found: {revised_spec}")
                human_review_needed.append((component_id, spec_path, "Revised spec not found"))
                component_status[component_id] = "needs_review"
                continue

            # Step 5: Now Evaluate the revised spec
            print(f"Evaluating revised spec for {component_id}")
            # FIXED: Only include necessary parameters for evaluate_candidate_spec
            context = {"candidate_spec_path": revised_spec, "output_root": f"{args.output_dir}/evaluation"}
            # Add model if present in base context
            if "model" in base_context:
                context["model"] = base_context["model"]

            # Handle retry logic
            step_name = f"Evaluate Candidate Spec for {component_id}"
            if flow_mode == FlowControl.RETRY and last_action.step_name == step_name:
                print(f"Retrying: {step_name}")
                success, _ = execute_step(
                    last_action.recipe_path,
                    last_action.context,
                    last_action.step_name,
                    last_action.component_id,
                    args.verbose,
                )
                # Reset flow mode after retry
                flow_mode = FlowControl.STEP_BY_STEP
            else:
                # Normal execution
                success, last_action = execute_step(
                    "recipes/blueprint_generator/evaluate_candidate_spec.json",
                    context,
                    step_name,
                    component_id,
                    args.verbose,
                )

            if not success:
                print(f"Evaluation failed. Skipping {component_id}.")
                human_review_needed.append((component_id, revised_spec, "Evaluation failed"))
                component_status[component_id] = "needs_review"
                continue

            # Pause after evaluation
            flow_mode = pause_and_check(
                flow_mode,
                last_action,
                allow_component_option=True,
                allow_all_components_option=True,
                allow_until_complete_option=True,
                allow_retry=True,
            )

            # If retry requested, continue retry loop
            if flow_mode == FlowControl.RETRY:
                continue

            # Find evaluation file
            eval_files = glob.glob(f"{args.output_dir}/evaluation/{component_id}*.md")
            if not eval_files:
                print(f"No evaluation file found for {component_id}. Skipping.")
                human_review_needed.append((component_id, revised_spec, "No evaluation file found"))
                component_status[component_id] = "needs_review"
                continue

            eval_file = eval_files[-1]  # Take most recent evaluation

            # Check if clarification is needed
            if needs_human_review(eval_file):
                print(f"{component_id} needs human review.")
                human_review_needed.append((component_id, revised_spec, "Evaluation indicates need for human review"))
                component_status[component_id] = "needs_review"

                # Copy evaluation and spec to human_review folder
                shutil.copy(eval_file, f"{args.output_dir}/human_review/{os.path.basename(eval_file)}")
                shutil.copy(revised_spec, f"{args.output_dir}/human_review/{os.path.basename(revised_spec)}")
                shutil.copy(questions_file, f"{args.output_dir}/human_review/{os.path.basename(questions_file)}")

                # Update action state to include review status
                last_action = ActionState(
                    step_name=f"Add {component_id} to Human Review Queue",
                    component_id=component_id,
                    recipe_path="",  # Empty string instead of None for recipe path
                    context={},  # Empty dict instead of None for context
                )

                # Pause after adding to human review queue
                flow_mode = pause_and_check(
                    flow_mode,
                    last_action,
                    allow_component_option=False,  # Component processing ends here
                    allow_all_components_option=True,
                    allow_until_complete_option=True,
                )
            else:
                print(f"{component_id} passed evaluation!")
                component_status[component_id] = "complete"

                # Update action state
                last_action = ActionState(
                    step_name=f"Mark {component_id} as Complete",
                    component_id=component_id,
                    recipe_path="",  # Empty string instead of None for recipe path
                    context={},  # Empty dict instead of None for context
                )

                # Pause after marking as complete
                flow_mode = pause_and_check(
                    flow_mode,
                    last_action,
                    allow_component_option=False,  # Component processing ends here
                    allow_all_components_option=True,
                    allow_until_complete_option=True,
                )

        # Check if any components need human review
        if human_review_needed:
            print("\n=== Components Needing Human Review ===")
            for component_id, spec_path, reason in human_review_needed:
                print(f"- {component_id}: {reason}")
                print(f"  Spec: {spec_path}")
                print(f"  Evaluation: {args.output_dir}/human_review/{component_id}*.md")

            # Update action state
            last_action = ActionState(
                step_name="Check For Components Needing Human Review",
                component_id=None,
                recipe_path="",  # Empty string instead of None for recipe path
                context={},  # Empty dict instead of None for context
            )

            # Pause after checking human review
            flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True)

            # Prompt for human intervention
            print("\nPlease review the files in the human_review directory.")
            print("After review, you can provide additional context files and continue.")

            proceed = input("Do you want to continue with the next iteration? (y/n): ")
            if proceed.lower() != "y":
                print("Exiting pipeline at user request.")
                return

            # Optionally get additional context files
            additional_context = input(
                "Enter paths to additional context files (comma-separated, or press Enter to skip): "
            )
            if additional_context:
                # Update context files for the next iteration
                if args.context_files:
                    args.context_files = f"{args.context_files},{additional_context}"
                else:
                    args.context_files = additional_context

                # Update base context
                base_context = get_base_context(args)

                # Update action state
                last_action = ActionState(
                    step_name="Process Human Review Input",
                    component_id=None,
                    recipe_path="",  # Empty string instead of None for recipe path
                    context={},  # Empty dict instead of None for context
                )

                # Pause after processing human input
                flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True)
        else:
            all_complete = all(status == "complete" for status in component_status.values())
            if all_complete:
                print("\nAll components have been successfully processed!")

                # Update action state
                last_action = ActionState(
                    step_name="All Components Evaluated Successfully",
                    component_id=None,
                    recipe_path="",  # Empty string instead of None for recipe path
                    context={},  # Empty dict instead of None for context
                )

                # Pause before blueprint generation
                flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True)
            else:
                print("\nSome components still need processing in the next iteration.")

    # Check if we hit the max iterations
    if not all_complete:
        print(f"\nReached maximum iterations ({args.max_iterations}) without completing all components.")
        print("Please review remaining issues manually before proceeding.")
        return

    # Proceed to blueprint and code generation
    print("\n=== Generating Blueprints and Code ===")

    # Get all successfully completed component specs
    completed_specs = []
    for component_id, status in component_status.items():
        if status == "complete":
            spec_path = find_latest_spec(component_id, args.output_dir)
            if spec_path:
                completed_specs.append((component_id, spec_path))

    # Blueprint generation loop
    for component_id, spec_path in completed_specs:
        print(f"Generating blueprint for {component_id}")
        # Create directories if they don't exist
        blueprint_dir = f"{args.output_dir}/blueprints/{args.target_project}/components/{component_id}"
        os.makedirs(blueprint_dir, exist_ok=True)

        # Create a combined files parameter for build_blueprint
        files_param = args.project_spec
        if args.context_files:
            files_param = f"{files_param},{args.context_files}"

        context = {
            "candidate_spec_path": spec_path,
            "component_id": component_id,
            "component_name": component_id.title().replace("_", " "),
            "target_project": args.target_project,
            "output_root": f"{args.output_dir}/blueprints",
            "files": files_param,  # Add combined files parameter
            "project_recipe_path": f"{args.output_dir}/blueprints"  # Ensure recipe path is set correctly
        }
        # Add model if present in base context
        if "model" in base_context:
            context["model"] = base_context["model"]

        # Handle retry logic
        step_name = f"Blueprint Generation for {component_id}"
        if flow_mode == FlowControl.RETRY and last_action.step_name == step_name:
            print(f"Retrying: {step_name}")
            success, _ = execute_step(
                last_action.recipe_path,
                last_action.context,
                last_action.step_name,
                last_action.component_id,
                args.verbose,
            )
            # Reset flow mode after retry
            flow_mode = FlowControl.STEP_BY_STEP
        else:
            # Normal execution
            success, last_action = execute_step(
                "recipes/blueprint_generator/build_blueprint.json", context, step_name, component_id, args.verbose
            )

        if not success:
            print(f"Blueprint generation failed for {component_id}. Skipping code generation.")
            continue

        # Pause after blueprint generation
        flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True, allow_retry=True)

        # If retry requested, retry the blueprint generation
        if flow_mode == FlowControl.RETRY:
            component_id_index = completed_specs.index((component_id, spec_path))
            # Reset to current component by adjusting the loop
            completed_specs = completed_specs[component_id_index:]
            continue

        # Generate code using the create recipe
        create_recipe_path = (
            f"{args.output_dir}/blueprints/{args.target_project}/components/{component_id}/{component_id}_create.json"
        )
        if not os.path.exists(create_recipe_path):
            print(f"Expected create recipe not found: {create_recipe_path}")
            continue

        print(f"Generating code for {component_id}")
        # Include project_spec and context_files for component create recipes
        files_param = args.project_spec
        if args.context_files:
            files_param = f"{files_param},{args.context_files}"

        # Create directory for generated code
        code_dir = f"{args.output_dir}/code/{args.target_project}"
        os.makedirs(code_dir, exist_ok=True)

        context = {
            "output_root": f"{args.output_dir}/code",
            "files": files_param,  # Add combined files parameter
            "target_project": args.target_project,
            "project_recipe_path": f"{args.output_dir}/blueprints"  # Path to find spec and doc files
        }
        # Add model if present in base context
        if "model" in base_context:
            context["model"] = base_context["model"]

        # Handle retry logic
        step_name = f"Code Generation for {component_id}"
        if flow_mode == FlowControl.RETRY and last_action.step_name == step_name:
            print(f"Retrying: {step_name}")
            success, _ = execute_step(
                last_action.recipe_path,
                last_action.context,
                last_action.step_name,
                last_action.component_id,
                args.verbose,
            )
            # Reset flow mode after retry
            flow_mode = FlowControl.STEP_BY_STEP
        else:
            # Normal execution
            success, last_action = execute_step(create_recipe_path, context, step_name, component_id, args.verbose)

        if not success:
            print(f"Code generation failed for {component_id}.")
            continue

        print(f"Successfully generated code for {component_id}")

        # Pause after code generation
        flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True, allow_retry=True)

        # If retry requested, retry this component's code generation
        if flow_mode == FlowControl.RETRY:
            component_id_index = completed_specs.index((component_id, spec_path))
            # Reset to current component by adjusting the loop
            completed_specs = completed_specs[component_id_index:]
            continue

    # Final Summary
    print("\n=== Pipeline Summary ===")
    print(f"Total components processed: {len(component_status)}")
    print(f"Successfully completed components: {len([s for s in component_status.values() if s == 'complete'])}")

    print("\nComponent Status:")
    for component_id, status in component_status.items():
        print(f"  - {component_id}: {status}")

    if all_complete:
        print(f"\nGenerated code can be found in: {args.output_dir}/code/{args.target_project}")
    else:
        print("\nSome components could not be completed successfully.")
        print("Review the human_review directory for details on remaining issues.")

    # Final pause
    if flow_mode != FlowControl.AUTO_MODE:
        input("\nPipeline complete. Press Enter to exit.")


if __name__ == "__main__":
    main()
