#!/usr/bin/env python3
"""
Generator module for the blueprint pipeline.

This module contains functions for generating blueprints and code
from component specifications.
"""
import concurrent.futures
import os
from typing import Dict, List, Optional, Tuple

from blueprint_pipeline.executor import run_recipe
from blueprint_pipeline.flow_control import ActionState, FlowControl, pause_and_check
from blueprint_pipeline.utils import safe_print


def generate_blueprint(
    component_id: str,
    spec_path: str,
    base_context: Dict[str, str],
    output_dir: str,
    target_project: str,
    verbose: bool = False,
    resume_mode: bool = False,
) -> Tuple[bool, str]:
    """
    Generate blueprint for a single component with enhanced dependency handling.
    This function can be run in parallel for multiple components.

    Args:
        component_id: ID of the component to process
        spec_path: Path to the component specification file
        base_context: Base context dictionary
        output_dir: Output directory
        target_project: Target project name
        verbose: Whether to show detailed output
        resume_mode: Whether to skip steps with existing output

    Returns:
        Tuple[bool, str]: Success status and path to the created recipe
    """
    # Generate Blueprint
    blueprint_dir = f"{output_dir}/blueprints/{target_project}/components/{component_id}"
    create_recipe_path = f"{blueprint_dir}/{component_id}_create.json"

    if os.path.exists(create_recipe_path) and resume_mode:
        safe_print(f"Blueprint for {component_id} already exists. Skipping blueprint generation.")
        return True, create_recipe_path
    else:
        safe_print(f"Generating blueprint for {component_id}")
        os.makedirs(blueprint_dir, exist_ok=True)

        files_param = base_context.get("project_spec", "")
        if base_context.get("context_files"):
            files_param = f"{files_param},{base_context['context_files']}"

        # Scan the component specification for dependencies
        dependencies = extract_dependencies_from_spec(spec_path)
        if dependencies and verbose:
            safe_print(f"Identified dependencies for {component_id}: {', '.join(dependencies)}")

        # Create related_docs parameter for dependencies
        related_docs = []
        if dependencies:
            for dep in dependencies:
                dep_docs_path = f"{output_dir}/blueprints/{target_project}/components/{dep}/{dep}_docs.md"
                # Only include dependencies that have documentation files
                if os.path.exists(dep_docs_path):
                    related_docs.append(dep_docs_path)
                elif verbose:
                    safe_print(f"Warning: Dependency '{dep}' documentation not found at {dep_docs_path}")

        # Add related_docs to context if any were found
        context = {
            "candidate_spec_path": spec_path,
            "component_id": component_id,
            "component_name": component_id.title().replace("_", " "),
            "target_project": target_project,
            "output_root": f"{output_dir}/blueprints",
            "files": files_param,
            "project_recipe_path": f"{output_dir}/blueprints"
        }

        if related_docs:
            context["related_docs"] = ",".join(related_docs)
            if verbose:
                safe_print(f"Including related docs: {context['related_docs']}")

        if "model" in base_context:
            context["model"] = base_context["model"]

        blueprint_success = run_recipe(
            "recipes/blueprint_generator/build_blueprint.json",
            context,
            verbose
        )

        if not blueprint_success:
            safe_print(f"Blueprint generation failed for {component_id}.")
            return False, ""

        if not os.path.exists(create_recipe_path):
            safe_print(f"Expected create recipe not found: {create_recipe_path}")
            return False, ""

        return True, create_recipe_path


def extract_dependencies_from_spec(spec_path: str) -> List[str]:
    """
    Extract component dependencies from a specification file.

    Args:
        spec_path: Path to the component specification file

    Returns:
        List[str]: List of component IDs that this component depends on
    """
    dependencies = []

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()

        # Look for dependency sections
        sections = [
            "## Component Dependencies",
            "### Internal Components",
            "## Dependencies",
            "## Internal Dependencies"
        ]

        for section in sections:
            if section in spec_content:
                # Get the content from the section to the next section or end of file
                start_idx = spec_content.find(section)
                next_section_idx = spec_content.find("##", start_idx + len(section))
                if next_section_idx == -1:
                    section_content = spec_content[start_idx:]
                else:
                    section_content = spec_content[start_idx:next_section_idx]

                # Look for component IDs in bullet points
                import re
                # Pattern to match: - **component_name** or - component_name
                component_patterns = [
                    r'\*\*([a-z][a-z0-9_]*)\*\*',  # Match **component_id**
                    r'- ([a-z][a-z0-9_]*)[^a-z0-9_]'  # Match - component_id
                ]

                for pattern in component_patterns:
                    matches = re.findall(pattern, section_content)
                    for match in matches:
                        # Verify this looks like a component ID (not other emphasized text)
                        if match and match.islower() and '_' in match:
                            dependencies.append(match)

    except Exception as e:
        safe_print(f"Error extracting dependencies from {spec_path}: {e}")

    # Remove duplicates while preserving order
    seen = set()
    return [dep for dep in dependencies if not (dep in seen or seen.add(dep))]


def generate_code(
    component_id: str,
    create_recipe_path: str,
    base_context: Dict[str, str],
    output_dir: str,
    target_project: str,
    verbose: bool = False,
    resume_mode: bool = False,
) -> bool:
    """
    Generate code for a single component.
    This function can be run in parallel for multiple components.

    Args:
        component_id: ID of the component to process
        create_recipe_path: Path to the component create recipe file
        base_context: Base context dictionary
        output_dir: Output directory
        target_project: Target project name
        verbose: Whether to show detailed output
        resume_mode: Whether to skip steps with existing output

    Returns:
        bool: Success status
    """
    code_dir = f"{output_dir}/code/{target_project}"
    component_code_file = f"{code_dir}/{component_id}.py"  # Assuming Python, adjust as needed

    if os.path.exists(component_code_file) and resume_mode:
        safe_print(f"Code for {component_id} already exists. Skipping code generation.")
        return True
    else:
        safe_print(f"Generating code for {component_id}")
        os.makedirs(code_dir, exist_ok=True)

        files_param = base_context.get("project_spec", "")
        if base_context.get("context_files"):
            files_param = f"{files_param},{base_context['context_files']}"

        context = {
            "output_root": f"{output_dir}/code",
            "files": files_param,
            "target_project": target_project,
            "project_recipe_path": f"{output_dir}/blueprints/{target_project}/components",  # Include the full output_dir path
            "component_id": component_id
        }
        if "model" in base_context:
            context["model"] = base_context["model"]

        code_success = run_recipe(create_recipe_path, context, verbose)

        if not code_success:
            safe_print(f"Code generation failed for {component_id}.")
            return False

        safe_print(f"Successfully generated code for {component_id}")
        return True


def generate_blueprint_and_code(
    component_id: str,
    spec_path: str,
    base_context: Dict[str, str],  # Now may contain dependency info
    output_dir: str,
    target_project: str,
    verbose: bool = False,
    resume_mode: bool = False,
) -> bool:
    """
    Generate blueprint and code for a single component.
    This function can be run in parallel for multiple components.

    Args:
        component_id: ID of the component to process
        spec_path: Path to the component specification file
        base_context: Base context dictionary (potentially with dependency info)
        output_dir: Output directory
        target_project: Target project name
        verbose: Whether to show detailed output
        resume_mode: Whether to skip steps with existing output

    Returns:
        bool: Success status
    """
    # Step 1: Generate Blueprint
    # We pass the dependency-enhanced context directly to generate_blueprint
    blueprint_success, create_recipe_path = generate_blueprint(
        component_id,
        spec_path,
        base_context,  # Pass context with dependency information
        output_dir,
        target_project,
        verbose,
        resume_mode
    )

    if not blueprint_success:
        return False

    # Step 2: Generate Code
    return generate_code(
        component_id,
        create_recipe_path,
        base_context,
        output_dir,
        target_project,
        verbose,
        resume_mode
    )


def generate_blueprints_and_code_in_parallel(
    completed_specs: List[Tuple[str, str]],
    dependency_map: Optional[Dict[str, List[str]]],
    base_context: Dict[str, str],
    output_dir: str,
    target_project: str,
    verbose: bool = False,
    flow_mode: FlowControl = FlowControl.STEP_BY_STEP,
    max_workers: int = 4,
) -> Tuple[List[str], List[str]]:
    """
    Generate blueprints and code in parallel for multiple components.
    This implementation runs blueprint generation for all components first,
    then runs code generation in parallel for components with successful blueprints.

    Args:
        completed_specs: List of (component_id, spec_path) tuples to process.
        dependency_map: Map of component dependencies (component_id -> list of dependencies).
        base_context: Base context dictionary.
        output_dir: Output directory.
        target_project: Target project name.
        verbose: Whether to show detailed output.
        flow_mode: Current flow control mode.
        max_workers: Maximum number of parallel workers.

    Returns:
        Tuple[List[str], List[str]]: Lists of successful and failed component IDs.
    """
    successful_components = []
    failed_components = []
    resume_mode = (flow_mode == FlowControl.RESUME)

    # If we're in step-by-step mode, don't parallelize
    if flow_mode == FlowControl.STEP_BY_STEP:
        for component_id, spec_path in completed_specs:
            # Add dependency information if available
            context_with_deps = base_context.copy()
            if dependency_map and component_id in dependency_map:
                deps = dependency_map[component_id]
                if deps and verbose:
                    safe_print(f"Component {component_id} depends on: {', '.join(deps)}")
                # Include dependency info in context
                context_with_deps["key_dependencies"] = ",".join(deps)

                # Create related_docs string for dependencies with documentation
                related_docs = []
                for dep in deps:
                    dep_docs_path = f"{output_dir}/blueprints/{target_project}/components/{dep}/{dep}_docs.md"
                    if os.path.exists(dep_docs_path):
                        related_docs.append(dep_docs_path)
                    elif verbose:
                        safe_print(f"Warning: Dependency '{dep}' documentation not found at {dep_docs_path}")

                if related_docs:
                    context_with_deps["related_docs"] = ",".join(related_docs)
                    if verbose:
                        safe_print(f"Including related docs: {context_with_deps['related_docs']}")

            success = generate_blueprint_and_code(
                component_id,
                spec_path,
                context_with_deps,  # Use enhanced context with dependencies
                output_dir,
                target_project,
                verbose,
                resume_mode
            )

            if success:
                successful_components.append(component_id)
            else:
                failed_components.append(component_id)

            # Update action state
            last_action = ActionState(
                step_name=f"Generated Blueprint and Code for {component_id}",
                component_id=component_id,
                recipe_path="",
                context={},
            )

            # Pause after each component (but not in resume mode)
            if flow_mode != FlowControl.RESUME:
                flow_mode = pause_and_check(
                    flow_mode,
                    last_action,
                    allow_until_complete_option=True
                )
    else:
        # Phase 1: Generate all blueprints in parallel
        safe_print("\n=== Phase 1: Generating Blueprints in Parallel ===")
        blueprint_results = {}  # component_id -> (success, create_recipe_path)

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(completed_specs))) as executor:
            # Submit all blueprint generation tasks with dependency enriched contexts
            future_to_component = {}
            for component_id, spec_path in completed_specs:
                # Create enhanced context with dependencies
                context_with_deps = base_context.copy()
                if dependency_map and component_id in dependency_map:
                    deps = dependency_map[component_id]
                    if deps and verbose:
                        safe_print(f"Component {component_id} depends on: {', '.join(deps)}")
                    # Include dependency info in context
                    context_with_deps["key_dependencies"] = ",".join(deps)

                    # Create related_docs string for dependencies with documentation
                    related_docs = []
                    for dep in deps:
                        dep_docs_path = f"{output_dir}/blueprints/{target_project}/components/{dep}/{dep}_docs.md"
                        if os.path.exists(dep_docs_path):
                            related_docs.append(dep_docs_path)
                        elif verbose:
                            safe_print(f"Warning: Dependency '{dep}' documentation not found at {dep_docs_path}")

                    if related_docs:
                        context_with_deps["related_docs"] = ",".join(related_docs)
                        if verbose:
                            safe_print(f"Including related docs: {context_with_deps['related_docs']}")

                # Submit task with enhanced context
                future = executor.submit(
                    generate_blueprint,
                    component_id,
                    spec_path,
                    context_with_deps,  # Use enhanced context with dependencies
                    output_dir,
                    target_project,
                    verbose,
                    resume_mode
                )
                future_to_component[future] = component_id

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_component):
                component_id = future_to_component[future]
                try:
                    success, create_recipe_path = future.result()
                    blueprint_results[component_id] = (success, create_recipe_path)
                    if not success:
                        safe_print(f"Blueprint generation failed for {component_id}.")
                        failed_components.append(component_id)
                except Exception as exc:
                    safe_print(f"Component {component_id} blueprint generation generated an exception: {exc}")
                    blueprint_results[component_id] = (False, "")
                    failed_components.append(component_id)

        # Phase 2: Generate code for components with successful blueprints
        safe_print("\n=== Phase 2: Generating Code in Parallel ===")
        successful_blueprints = [(comp_id, path) for comp_id, (success, path) in blueprint_results.items() if success]

        if not successful_blueprints:
            safe_print("No successful blueprints to generate code from.")
            return successful_components, failed_components

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(successful_blueprints))) as executor:
            # Submit all code generation tasks
            future_to_component = {
                executor.submit(
                    generate_code,
                    component_id,
                    create_recipe_path,
                    base_context,
                    output_dir,
                    target_project,
                    verbose,
                    resume_mode
                ): component_id for component_id, create_recipe_path in successful_blueprints
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_component):
                component_id = future_to_component[future]
                try:
                    success = future.result()
                    if success:
                        successful_components.append(component_id)
                        safe_print(f"Successfully generated code for {component_id}")
                    else:
                        failed_components.append(component_id)
                        safe_print(f"Code generation failed for {component_id}")
                except Exception as exc:
                    safe_print(f"Component {component_id} code generation generated an exception: {exc}")
                    failed_components.append(component_id)

    return successful_components, failed_components
