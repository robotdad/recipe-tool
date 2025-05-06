# UML-Based Recipe Management UI Generator

This system transforms a natural language specification for a Recipe Management UI into well-engineered code using UML diagrams as an intermediate representation. It follows a multi-stage pipeline with human review checkpoints and is specifically designed to create a web interface for managing your recipe automation system.

## Overview

The system consists of recipes that work together to:

1. Extract structured requirements from natural language specifications for the Recipe Management UI
2. Generate UML models representing the UI system architecture
3. Create implementation recipes based on the UML models
4. Execute those recipes to generate the final UI code

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

- Run the main recipe with the sample Recipe Management UI vision document:

  ```bash
  recipe-tool --execute recipes/experimental/uml_system/main.json \
     input_path=blueprint_test/input/recipe_management_ui_vision.md \
     output_dir=blueprint_test/output/uml_system \
     model=openai/o4-mini
  ```

4. Review any items flagged for human intervention (stored in the `**output**/review` directory)

5. Continue the process by following the instructions in the `NEXT_STEPS.md` file

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

## Recipe Management UI

The system will generate a complete web-based UI for managing recipe automation:

1. **Recipe Editor**: A visual interface for creating and editing recipe JSON files
2. **Recipe Library**: A repository for organizing and managing recipes
3. **Execution Dashboard**: UI for running recipes with visual progress tracking
4. **Context Management**: Interface for managing input data and parameters
5. **Output Viewer**: For viewing and managing recipe execution results

The UI will eliminate the need for command-line interaction with the recipe-tool, making it accessible to non-technical users while providing power features for experts.

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
    <generated UI code structure>
  review/                     # Human review files (if needed)
    specifications_review.md
    uml_models_review.md
    recipes_review.md
    code_review.md
    NEXT_STEPS.md
  FINAL_REPORT.md             # Summary of the generated system
```

## Tips for Best Results

1. Review the specifications to ensure they fully capture your vision for the Recipe Management UI
2. Pay close attention to human review requests
3. Check the UML diagrams to ensure they match your intentions
4. Ensure specifications cover all system components and their interactions
