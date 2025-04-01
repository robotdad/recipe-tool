# Component Blueprint Generator - Summary

## Overview

The Component Blueprint Generator is a recipe-based system that creates comprehensive component blueprints from candidate specifications. It generates all the necessary files for implementing a component following the modular building-block approach to software development with AI.

## Key Features

1. **Automated Blueprint Generation**: Convert a simple candidate spec into a complete set of blueprint files
2. **Specification Refinement**: Generate formal, structured component specifications
3. **Documentation Generation**: Create comprehensive usage documentation with examples
4. **Recipe Creation**: Generate the recipe files needed to implement and edit the component
5. **Consistent Structure**: Ensure all components follow the same structural patterns
6. **Specification Evaluation**: Assess candidate specifications for completeness and clarity
7. **Clarification Questions**: Generate targeted questions to improve incomplete specifications

## How It Works

1. A candidate specification is provided as input
2. AI analyzes the spec to extract key component information
3. The system generates a formal specification document
4. Documentation is created based on the specification
5. Recipe files for component creation and editing are generated
   - These recipe files are designed to call the [Codebase Generator](/recipes/codebase_generator/) recipe
   - This creates a seamless workflow from spec to blueprint to actual code
6. A summary report is created with instructions for using the generated files

> **Integration with Codebase Generator**: The Blueprint Generator and Codebase Generator work together in a deliberate pipeline. The Blueprint Generator creates recipe files that call the Codebase Generator with the appropriate context, showing how Recipe Executor leverages recipe composition for complex workflows.

## Generated Files for Each Component

For each component, the system generates:

1. **Specification File**: `<target_project>/specs/<component_id>.md`
2. **Documentation File**: `<target_project>/docs/<component_id>.md`
3. **Recipe Files**:
   - `<target_project>/recipes/<component_id>_create.json`
   - `<target_project>/recipes/<component_id>_edit.json`
4. **Blueprint Summary**: `<target_project>/<component_id>_blueprint_summary.md`

## Usage Instructions

### Basic Usage

To generate a component blueprint from a candidate specification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context component_id=auth \
  --context component_name="Authentication" \
  --context target_project=recipe_executor \
  --context output_root=output
```

To evaluate a candidate specification and generate clarification questions if needed:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/evaluate_candidate_spec.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context output_root=output
```

To specifically generate clarification questions for an incomplete specification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/generate_clarification_questions.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context output_root=output
```

### Parameters

- `candidate_spec_path`: Path to the candidate specification file
- `component_id`: ID of the component (lowercase, underscore-separated)
- `component_name`: Human-readable name of the component
- `target_project`: Name of the project/folder where component will be placed
- `output_root`: Base directory for output files (default: "output")
- `module_path` (optional): Import path for the component
- `component_type` (optional): Type of component (utility, core, etc.)
- `model` (optional): LLM model to use (default: "openai:o3-mini")

### Workflow

1. **Create Candidate Spec**: Write a basic specification for your component
2. **Evaluate Specification**: Run the evaluation recipe to check for completeness
3. **Address Clarifications**: If needed, answer the clarification questions
4. **Generate Blueprint**: Run the blueprint generator recipe
5. **Review Generated Files**: Examine the specification, documentation, and recipes
6. **Generate Component**: Use the generated recipes to create the actual component code
7. **Iterate if Needed**: If changes are needed, edit the specification and regenerate

## Files in this Recipe System

| File                                    | Purpose                                                          |
| --------------------------------------- | ---------------------------------------------------------------- |
| `build_blueprint.json`                  | Main entry point recipe for blueprint generation                 |
| `create.json`                           | Orchestrates the blueprint generation process                    |
| `create_spec.json`                      | Generates the formal specification                               |
| `create_doc.json`                       | Creates component documentation                                  |
| `create_recipes.json`                   | Generates component recipe files                                 |
| `finalize_blueprint.json`               | Creates a summary report                                         |
| `evaluate_candidate_spec.json`          | Evaluates a candidate specification for completeness             |
| `generate_clarification_questions.json` | Generates questions to improve incomplete specs                  |
| `spec_template.md`                      | Template for specification files                                 |
| `doc_template.md`                       | Template for documentation files                                 |
| `SPEC_DOC_GUIDE.md`                     | Comprehensive guide to creating specifications and documentation |
| `IMPLEMENTATION_PHILOSOPHY.md`          | Philosophy for implementation approaches                         |
| `MODULAR_DESIGN_PHILOSOPHY.md`          | Philosophy for modular, building-block design                    |
