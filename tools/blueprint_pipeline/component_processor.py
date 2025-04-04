#!/usr/bin/env python3
"""
Component processor module for the blueprint pipeline.

This module contains functions for processing components in the pipeline,
including project analysis, component splitting, and component evaluation.
"""
import argparse
import concurrent.futures
import glob
import os
import shutil
from typing import Dict, List, Optional, Tuple

from blueprint_pipeline.executor import execute_step, run_recipe
from blueprint_pipeline.flow_control import ActionState, FlowControl, pause_and_check
from blueprint_pipeline.utils import safe_print, needs_human_review, find_latest_spec


def process_project_analysis(
    args: argparse.Namespace,
    base_context: Dict[str, str],
    flow_mode: FlowControl,
    last_action: ActionState,
) -> Tuple[Optional[FlowControl], ActionState]:
    """
    Process the project analysis step.

    Args:
        args: Command line arguments.
        base_context: Base context dictionary.
        flow_mode: Current flow control mode.
        last_action: Last action state.

    Returns:
        Tuple[Optional[FlowControl], ActionState]: Updated flow mode and action state.
            If flow_mode is None, the step failed.
    """
    safe_print("\n=== Step 1: Project Split Analysis ===")

    # Check if output already exists (resume capability)
    analysis_file = f"{args.output_dir}/analysis/project_component_breakdown_analysis.md"
    if os.path.exists(analysis_file) and flow_mode == FlowControl.RESUME:
        safe_print(f"Found existing output file: {analysis_file}")
        safe_print("Skipping project split analysis step.")

        # Update last_action to reflect we've processed this step
        last_action = ActionState(
            step_name="Project Split Analysis",
            component_id=None,
            recipe_path="recipes/utilities/project_split_analysis.json",
            context={},
        )
        return flow_mode, last_action

    context = base_context.copy()
    context.update({
        "input": args.project_spec,
        "files": args.context_files,
        "output_root": f"{args.output_dir}/analysis",
    })

    # Handle retry logic - if in retry mode, reuse last_action
    if flow_mode == FlowControl.RETRY and last_action.step_name == "Project Split Analysis":
        safe_print("Retrying: Project Split Analysis")
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
        safe_print("Project split analysis failed. Exiting.")
        return None, last_action

    # Pause after project analysis
    flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True, allow_retry=True)

    # Check if the expected output file exists
    if not os.path.exists(analysis_file):
        safe_print(f"Expected output file not found: {analysis_file}")
        return None, last_action

    return flow_mode, last_action


def process_component_split(
    args: argparse.Namespace,
    base_context: Dict[str, str],
    flow_mode: FlowControl,
    last_action: ActionState,
) -> Tuple[Optional[FlowControl], ActionState]:
    """
    Process the component split step.

    Args:
        args: Command line arguments.
        base_context: Base context dictionary.
        flow_mode: Current flow control mode.
        last_action: Last action state.

    Returns:
        Tuple[Optional[FlowControl], ActionState]: Updated flow mode and action state.
            If flow_mode is None, the step failed.
    """
    safe_print("\n=== Step 2: Split to Components ===")

    # Check if output already exists (resume capability)
    component_specs_paths = glob.glob(f"{args.output_dir}/components/*_candidate_spec.md")
    if component_specs_paths and flow_mode == FlowControl.RESUME:
        safe_print(f"Found {len(component_specs_paths)} existing component specifications.")
        safe_print("Skipping split to components step.")

        # Update last_action to reflect we've processed this step
        last_action = ActionState(
            step_name="Split to Components",
            component_id=None,
            recipe_path="recipes/utilities/split_to_components.json",
            context={},
        )
        return flow_mode, last_action

    context = {}
    # Only add model from base context to avoid incorrect parameters
    if "model" in base_context:
        context["model"] = base_context["model"]

    # Set the expected parameters for split_to_components recipe
    # Create a combined files parameter including project_spec and context_files
    files_param = args.project_spec
    if args.context_files:
        files_param = f"{files_param},{args.context_files}"

    analysis_file = f"{args.output_dir}/analysis/project_component_breakdown_analysis.md"
    context.update({
        "input": analysis_file,
        # Combine project_spec and context_files for the "files" parameter
        "files": files_param,
        "output_root": f"{args.output_dir}/components",
    })

    # Handle retry logic
    if flow_mode == FlowControl.RETRY and last_action.step_name == "Split to Components":
        safe_print("Retrying: Split to Components")
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
        safe_print("Split to components failed. Exiting.")
        return None, last_action

    # Pause after split to components
    flow_mode = pause_and_check(
        flow_mode,
        last_action,
        allow_all_components_option=True,
        allow_until_complete_option=True,
        allow_retry=True,
    )

    return flow_mode, last_action


def determine_components_to_process(
    output_dir: str,
    component_status: Dict[str, str],
    iteration_count: int,
    component_filter: Optional[str] = None,
) -> Tuple[List[Tuple[str, str]], Dict[str, str]]:
    """
    Determine which components to process in the current iteration.

    Args:
        output_dir: Output directory.
        component_status: Component status dictionary.
        iteration_count: Current iteration count.
        component_filter: Optional component filter.

    Returns:
        Tuple[List[Tuple[str, str]], Dict[str, str]]:
            - List of (component_id, spec_path) tuples to process.
            - Updated component status dictionary.
    """
    # Get all component specs to process in this iteration
    component_specs = []

    # If first iteration, get from components directory
    if iteration_count == 1:
        # Get all component specs
        component_specs_paths = glob.glob(f"{output_dir}/components/*_candidate_spec.md")

        # Initialize status tracking
        for spec_path in component_specs_paths:
            component_id = os.path.basename(spec_path).replace("_candidate_spec.md", "")

            # Check if the component is already complete
            eval_files = glob.glob(f"{output_dir}/evaluation/{component_id}*.md")
            revised_spec = f"{output_dir}/clarification/{component_id}_candidate_spec_revised.md"

            if eval_files and not needs_human_review(eval_files[-1]) and os.path.exists(revised_spec):
                # Component is already complete
                component_status[component_id] = "complete"
                safe_print(f"Component {component_id} is already complete. Skipping.")
            else:
                # Component needs processing
                component_status[component_id] = "incomplete"
                component_specs.append((component_id, spec_path))
    else:
        # For subsequent iterations, process components that need review
        for component_id, status in component_status.items():
            if status == "needs_review":
                spec_path = find_latest_spec(component_id, output_dir)
                if spec_path:
                    component_specs.append((component_id, spec_path))

    # Apply component filter if specified
    if component_filter and component_specs:
        filtered_specs = []
        for component_id, spec_path in component_specs:
            if component_id.startswith(component_filter):
                filtered_specs.append((component_id, spec_path))

        if not filtered_specs:
            safe_print(f"No components match the filter: {component_filter}")

        component_specs = filtered_specs

    return component_specs, component_status


def process_component(
    component_id: str,
    spec_path: str,
    base_context: Dict[str, str],
    output_dir: str,
    verbose: bool = False,
    resume_mode: bool = False,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Process a single component through the pipeline steps.
    This function can be run in parallel for multiple components.

    Args:
        component_id: ID of the component to process
        spec_path: Path to the component specification file
        base_context: Base context dictionary
        output_dir: Output directory
        verbose: Whether to show detailed output
        resume_mode: Whether to skip steps with existing output

    Returns:
        Tuple[str, Optional[str], Optional[str]]: Status, reason, and path to the latest spec
    """
    # This function runs each component through the pipeline:
    # 1. Generate Clarification Questions
    # 2. Generate Clarification Answers
    # 3. Evaluate the revised spec

    safe_print(f"\n=== Processing Component: {component_id} ===")

    # Step 1: Generate Clarification Questions
    questions_file = f"{output_dir}/clarification/{component_id}_component_clarification_questions.md"

    if os.path.exists(questions_file) and resume_mode:
        safe_print(f"Found existing clarification questions for {component_id}. Skipping question generation.")
    else:
        safe_print(f"Generating clarification questions for {component_id}")
        context = {
            "candidate_spec_path": spec_path,
            "component_id": component_id,
            "output_root": f"{output_dir}/clarification"
        }
        if "model" in base_context:
            context["model"] = base_context["model"]

        success = run_recipe(
            "recipes/blueprint_generator/generate_clarification_questions.json",
            context,
            verbose,
        )

        if not success:
            safe_print(f"Failed to generate clarification questions. Skipping {component_id}.")
            return "needs_review", "Failed to generate questions", spec_path

        if not os.path.exists(questions_file):
            safe_print(f"Expected questions file not found: {questions_file}")
            return "needs_review", "Questions file not found", spec_path

    # Step 2: Generate Clarification Answers
    revised_spec = f"{output_dir}/clarification/{component_id}_candidate_spec_revised.md"

    if os.path.exists(revised_spec) and resume_mode:
        safe_print(f"Found existing revised spec for {component_id}. Skipping answer generation.")
    else:
        safe_print(f"Generating clarification answers for {component_id}")
        files_param = base_context.get("project_spec", "")
        if base_context.get("context_files"):
            files_param = f"{files_param},{base_context['context_files']}"

        context = {
            "candidate_spec_path": spec_path,
            "clarification_questions_path": questions_file,
            "context_files": files_param,
            "output_root": f"{output_dir}/clarification",
            "component_id": component_id
        }
        if "model" in base_context:
            context["model"] = base_context["model"]

        success = run_recipe(
            "recipes/blueprint_generator/generate_clarification_answers.json",
            context,
            verbose,
        )

        if not success:
            safe_print(f"Failed to generate clarification answers. Skipping {component_id}.")
            return "needs_review", "Failed to generate answers", spec_path

        if not os.path.exists(revised_spec):
            safe_print(f"Expected revised spec not found: {revised_spec}")
            return "needs_review", "Revised spec not found", spec_path

    # Step 3: Evaluate Candidate Spec
    eval_files = glob.glob(f"{output_dir}/evaluation/{component_id}*.md")

    if eval_files and resume_mode:
        safe_print(f"Found existing evaluation for {component_id}. Skipping evaluation.")
        eval_file = eval_files[-1]  # Take most recent evaluation
    else:
        safe_print(f"Evaluating revised spec for {component_id}")
        context = {
            "candidate_spec_path": revised_spec,
            "component_id": component_id,
            "output_root": f"{output_dir}/evaluation"
        }
        if "model" in base_context:
            context["model"] = base_context["model"]

        success = run_recipe(
            "recipes/blueprint_generator/evaluate_candidate_spec.json",
            context,
            verbose,
        )

        if not success:
            safe_print(f"Evaluation failed. Skipping {component_id}.")
            return "needs_review", "Evaluation failed", revised_spec

        # Find evaluation file
        eval_files = glob.glob(f"{output_dir}/evaluation/{component_id}*.md")
        if not eval_files:
            safe_print(f"No evaluation file found for {component_id}. Skipping.")
            return "needs_review", "No evaluation file found", revised_spec

        eval_file = eval_files[-1]  # Take most recent evaluation

    # Check if clarification is needed
    if needs_human_review(eval_file):
        safe_print(f"{component_id} needs human review.")

        # Copy files to human_review folder
        for file_path in [eval_file, revised_spec, questions_file]:
            os.makedirs(f"{output_dir}/human_review", exist_ok=True)
            shutil.copy(file_path, f"{output_dir}/human_review/{os.path.basename(file_path)}")

        return "needs_review", "Evaluation indicates need for human review", revised_spec
    else:
        safe_print(f"{component_id} passed evaluation!")
        return "complete", None, revised_spec


def process_components_in_parallel(
    component_specs: List[Tuple[str, str]],
    component_status: Dict[str, str],
    base_context: Dict[str, str],
    output_dir: str,
    verbose: bool = False,
    flow_mode: FlowControl = FlowControl.STEP_BY_STEP,
    max_workers: int = 4,
) -> Tuple[Dict[str, str], List[Tuple[str, str, str]], FlowControl, ActionState]:
    """
    Process multiple components in parallel based on the flow mode.

    Args:
        component_specs: List of (component_id, spec_path) tuples to process.
        component_status: Component status dictionary.
        base_context: Base context dictionary.
        output_dir: Output directory.
        verbose: Whether to show detailed output.
        flow_mode: Current flow control mode.
        max_workers: Maximum number of parallel workers.

    Returns:
        Tuple[Dict[str, str], List[Tuple[str, str, str]], FlowControl, ActionState]:
            - Updated component status dictionary.
            - List of (component_id, spec_path, reason) tuples needing human review.
            - Updated flow mode.
            - Updated action state.
    """
    human_review_needed = []
    last_action = ActionState()
    resume_mode = (flow_mode == FlowControl.RESUME)

    # If we're in step-by-step mode, don't parallelize
    if flow_mode == FlowControl.STEP_BY_STEP or flow_mode == FlowControl.RESUME:
        for component_id, spec_path in component_specs:
            status, reason, final_spec = process_component(
                component_id,
                spec_path,
                base_context,
                output_dir,
                verbose,
                resume_mode
            )
            component_status[component_id] = status
            if status == "needs_review":
                human_review_needed.append((component_id, final_spec, reason))

            # Update action state
            last_action = ActionState(
                step_name=f"Processed Component {component_id}",
                component_id=component_id,
                recipe_path="",
                context={},
            )

            # Pause after processing each component (but not in resume mode)
            if flow_mode != FlowControl.RESUME:
                flow_mode = pause_and_check(
                    flow_mode,
                    last_action,
                    allow_all_components_option=True,
                    allow_until_complete_option=True,
                )
    else:
        # Use parallel processing for auto mode or UNTIL_COMPLETE mode
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(component_specs))) as executor:
            # Submit all component processing tasks
            future_to_component = {
                executor.submit(
                    process_component,
                    component_id,
                    spec_path,
                    base_context,
                    output_dir,
                    verbose,
                    False  # Don't use resume_mode for parallel processing
                ): (component_id, spec_path) for component_id, spec_path in component_specs
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_component):
                component_id, spec_path = future_to_component[future]
                try:
                    status, reason, final_spec = future.result()
                    component_status[component_id] = status
                    if status == "needs_review":
                        human_review_needed.append((component_id, final_spec, reason))

                    # Update action state
                    last_action = ActionState(
                        step_name=f"Processed Component {component_id}",
                        component_id=component_id,
                        recipe_path="",
                        context={},
                    )
                except Exception as exc:
                    safe_print(f"Component {component_id} generated an exception: {exc}")
                    component_status[component_id] = "needs_review"
                    human_review_needed.append((component_id, spec_path, f"Exception: {exc}"))

    return component_status, human_review_needed, flow_mode, last_action
