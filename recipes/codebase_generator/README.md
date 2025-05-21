# Codebase Generator Recipes

This directory contains the recipes used for an opinionated approach for codebase generation from a component manifest file and individual component docs/spec files. These recipes demonstrate the self-generating capability of the blueprints written to generate the codebase for the Recipe Executor system.

## Example: Run the Codebase Generator Recipe to generate the Recipe Executor code

From the repo root, run the codebase generator recipe to generate the Recipe Executor code.

Use the defaults, which are set for generating the Recipe Executor code in "edit" mode (uses the existing code for reference, mostly adjusting for changes to the source docs/spec files).

```bash
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json
```

Instead of generating the entire codebase, you can generate just the code for a specific module.
For example, to generate the code for the `steps.llm_generate` module, run:

```bash
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   edit=true \
   component_id=steps.llm_generate
```

You can also run with edit set to false to generate code without using the existing code as a reference.

```bash
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   edit=false
```

Alternatively, you can specify the parameters explicitly. This is useful if you want to generate a different codebase or if you want to run with different parameters.

```bash
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   project_blueprints_root=blueprints/recipe_executor \
   existing_code_root=recipe_executor \
   edit=true \
   refs_root=ai_context \
   dev_guide_path=ai_context/DEV_GUIDE_FOR_PYTHON.md \
   output_root=output \
   output_path='' \
   model=openai/o4-mini
```

## Diagram

![Recipe Executor Build Process](./docs/codebase-generator-flow.svg)

## Main Recipes

### `generate-codebase.json`

The main entry point recipe that orchestrates the entire component generation process. It:

1. Reads the component definitions from `components.json`
2. Iterates through each component (optionally filtering by a specific component ID)
3. Processes each component by calling the `process_component.json` recipe

```bash
# Process all components
recipe-tool --execute recipes/recipe_executor/generate-codebase.json

# Process a single component
recipe-tool --execute recipes/recipe_executor/generate-codebase.json component_id=context
```

### `components.json`

Contains the definitions of all components in the system, including:

- Component ID
- Dependencies on other components
- References to external documentation

## Sub-Recipes

### `recipes/process_component.json`

Handles the processing of a single component:

1. If in edit mode, reads existing code for the component
2. Calls `recipes/read_component_resources.json` to gather all resources
3. Calls `recipes/generate_component_code.json` to generate code using an LLM

```bash
# Process a specific component with edit mode enabled
recipe-tool --execute recipes/recipe_executor/recipes/process_component.json component_id=context edit=true
```

### `recipes/read_component_resources.json`

Gathers all resources required for generating a component:

1. Reads the component specification
2. Reads the component documentation (if available)
3. Gathers dependency specifications
4. Collects reference documentation
5. Loads implementation philosophy and dev guide

### `recipes/generate_component_code.json`

Uses an LLM to generate code based on the gathered resources:

1. Constructs a prompt with specifications, docs, and guidance
2. Calls the LLM to generate code files
3. Writes the generated files to disk

```bash
# Generate code for a specific component
recipe-tool --execute recipes/recipe_executor/recipes/generate_component_code.json spec=path/to/spec.md docs=path/to/docs.md
```

## Configuration Options

| Option                    | Description                                                                   |
| ------------------------- | ----------------------------------------------------------------------------- |
| `project_blueprints_root` | Root directory for project blueprints (default: "blueprints/recipe_executor") |
| `component_id`            | ID of the specific component to process (e.g., "context", "executor")         |
| `edit`                    | Set to `true` to read and update existing code (default: `false`)             |
| `model`                   | LLM model to use (default: "openai/o4-mini")                                  |
| `output_root`             | Root directory for output files (default: "output")                           |
| `existing_code_root`      | Root directory for existing code (used in edit mode)                          |

## Example Usage

```bash
# Process all components and output to a custom directory
recipe-tool --execute recipes/recipe_executor/generate-codebase.json output_root=custom_output

# Edit an existing component with a specific model
recipe-tool --execute recipes/recipe_executor/generate-codebase.json component_id=executor edit=true model=openai/gpt-4o existing_code_root=src
```

## How It Works

The recipe system follows these steps:

1. **Component Selection**: The system reads component definitions and selects which ones to process.
2. **Resource Gathering**: For each component, it collects specifications, documentation, and dependencies.
3. **Code Generation**: It uses an LLM to generate code based on the gathered resources.
4. **Output**: The generated code is written to disk in the specified directory structure.

This workflow demonstrates the power of using the Recipe Executor to generate (even its own) code, serving as both an example and a practical tool for development.
