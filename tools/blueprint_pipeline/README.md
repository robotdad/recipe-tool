# Blueprint Pipeline

A modular tool for generating code from high-level specifications using AI-assisted generation with parallel processing capabilities.

## Overview

The Blueprint Pipeline takes a high-level project specification and breaks it down into components, generates candidate specifications, processes them through a clarification and evaluation cycle, and then generates blueprints and code for the components that pass evaluation.

## Features

- **Modular Architecture**: Clearly separated components with well-defined interfaces
- **Parallel Processing**: Process multiple components simultaneously
- **Interactive Flow Control**: Step-by-step execution with user interaction
- **Automated Mode**: Run the entire pipeline without pauses
- **Component Filtering**: Process only specific components
- **Human Review Integration**: Flag components for human review
- **Progress Tracking**: Track the status of each component

## Installation

1. Clone this repository
2. Install the required dependencies

```bash
pip install -r requirements.txt
```

## Directory Structure

```
blueprint_pipeline/
├── __init__.py             # Package initialization
├── blueprint_pipeline.py   # Main entry point
├── component_processor.py  # Component processing logic
├── config.py               # Configuration handling
├── executor.py             # Step and recipe execution
├── flow_control.py         # Flow control and user interaction
├── generator.py            # Blueprint and code generation
└── utils.py                # Utility functions
```

## Usage

```bash
python -m blueprint_pipeline.blueprint_pipeline \
    --project_spec path/to/project_spec.md \
    --context_files path/to/context1.md,path/to/context2.md \
    --output_dir output \
    --model openai:o3-mini \
    --target_project my_project \
    --max_workers 4
```

### Command Line Arguments

- `--project_spec`: Path to the project specification file (required)
- `--context_files`: Comma-separated list of context files
- `--output_dir`: Output directory (default: "output")
- `--model`: LLM model to use (default: "openai:o3-mini")
- `--target_project`: Target project name (default: "generated_project")
- `--verbose`: Show detailed output
- `--component_filter`: Only process components matching this prefix
- `--max_iterations`: Maximum number of refinement iterations (default: 3)
- `--auto`: Run automatically without pausing
- `--max_workers`: Maximum number of parallel workers (default: 4)

## Pipeline Flow

1. **Project Analysis**: Generate a high-level breakdown of the project
2. **Component Split**: Split the project into individual components
3. **Component Processing**:
   - Generate clarification questions
   - Generate clarification answers
   - Evaluate the revised specification
4. **Blueprint Generation**: Generate blueprints for components that pass evaluation
5. **Code Generation**: Generate code from the blueprints

## Extending the Pipeline

The modular design makes it easy to extend the pipeline with new functionality:

- Add new modules to the `blueprint_pipeline` package
- Update the main entry point to include the new functionality
- Follow the established patterns for error handling, logging, and flow control

## Using Individual Modules

You can use individual modules directly in your code:

```python
from blueprint_pipeline.executor import run_recipe
from blueprint_pipeline.utils import find_latest_spec
from blueprint_pipeline.generator import generate_blueprint_and_code

# Run a recipe
success = run_recipe("path/to/recipe.json", {"key": "value"}, verbose=True)

# Find the latest specification file
spec_path = find_latest_spec("component_id", "output_dir")

# Generate blueprint and code
success = generate_blueprint_and_code(
    "component_id",
    spec_path,
    base_context,
    "output_dir",
    "target_project",
    verbose=True
)
```
