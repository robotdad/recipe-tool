# UML-Based Code Generation System

This system transforms high-level natural language specifications into well-engineered code using UML diagrams as an intermediate representation. It follows a multi-stage pipeline with human review checkpoints.

## Overview

The system consists of recipes that work together to:

1. Extract structured requirements from natural language specifications
2. Generate UML models representing the system architecture
3. Create implementation recipes based on the UML models
4. Execute those recipes to generate the final code

At each stage, the system evaluates the outputs and flags issues that need human review.

## Directory Structure

```
recipes/
  uml_system/
    main.json                     # Top-level orchestration recipe
    parse_specifications.json     # Extract structured requirements
    evaluate_specifications.json  # Validate specifications
    generate_uml_models.json      # Create UML diagrams
    evaluate_uml_models.json      # Validate UML models
    generate_recipes.json         # Create implementation recipes
    evaluate_recipes.json         # Validate recipes
    generate_code.json            # Execute recipes to generate code
```

## How to Use

1. Create a project specification document (see `sample_project_vision.md` for an example format)
2. Run the main recipe:

```bash
recipe-tool --execute recipes/experimental/uml_system/main.json input_path=path/to/your/specification.md
```

3. Review any items flagged for human intervention (stored in the `output/review` directory)
4. Continue the process by following the instructions in the `NEXT_STEPS.md` file

## Human Review Process

The system automatically detects potential issues that need human intervention:

1. Ambiguities or missing information in the specifications
2. UML models that may not fully represent the system
3. Implementation recipes that may have inconsistencies
4. Generated code that needs refinement

When issues are detected, the system pauses execution and outputs:

- A description of the issues in a markdown file
- Suggestions for addressing each issue
- Instructions for continuing execution after your review

## Example Workflow

```bash
# Start with your project specification
recipe-tool --execute recipes/experimental/uml_system/main.json input_path=specs/project_vision.md

# If review is needed, edit the files in output/review/
# Then continue execution using the command from NEXT_STEPS.md
recipe-tool --execute recipes/experimental/uml_system/main.json continuation=true

# Continue this process through each stage
```

## Output Structure

The system creates a structured output directory:

```
output/
  uml/                        # UML diagram files
    component_diagram.puml
    package_diagram.puml
    class_diagrams/
    sequence_diagrams/
    state_diagrams/
  recipes/                    # Generated implementation recipes
    implementation/
      main.json
      components/
      shared/
  implementation/             # Generated code
    <generated code structure>
  review/                     # Human review files (if needed)
    specifications_review.md
    uml_models_review.md
    recipes_review.md
    code_review.md
    NEXT_STEPS.md
  FINAL_REPORT.md             # Summary of the generated system
```

## Tips for Best Results

1. Make your project specification as detailed as possible
2. Pay close attention to human review requests
3. Check the UML diagrams to ensure they match your intentions
4. Ensure specifications cover all system components and their interactions

## Sample Project

A sample project specification is provided in `sample_project_vision.md`. This can be used to test the system and see how it processes a typical project vision document.
