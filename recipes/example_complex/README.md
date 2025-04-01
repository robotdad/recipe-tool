# Complex Recipe Example

## Overview

This directory demonstrates a more sophisticated Recipe Executor workflow using multiple specification files, sub-recipes, and more complex code generation. It shows how to build larger, modular code generation pipelines.

## Contents

- `complex_recipe.md` - The main recipe file demonstrating a multi-step workflow
- `sub_recipe.md` - A sub-recipe that gets executed as part of the main workflow
- `specs/` - Directory containing multiple specification files:
  - `main_spec.txt` - Primary specification for the main module
  - `auxiliary_spec.txt` - Additional specification for auxiliary features
  - `sub_spec.txt` - Specification for the utility module

## How It Works

The workflow in this example follows these steps:

1. **Read Multiple Specifications**: Reads both main and auxiliary specifications
2. **Generate Primary Module**: Uses an LLM to generate a Python module that integrates both specifications
3. **Write Output**: Writes the generated module to `output/main_module`
4. **Execute Sub-Recipe**: Runs a separate recipe to generate a utility module, which:
   - Reads a sub-specification
   - Generates a utility module with logging and data processing functions
   - Writes to `output/utility_module`

## Usage

Run the complex recipe with:

```bash
python recipe_executor/main.py recipes/example_complex/complex_recipe.md
```

This will generate:

- A main module in `output/main_module/`
- A utility module in `output/utility_module/`

## Validating the Output

After running the recipe, you can run the main module to test it:

```bash
# Run the main module to see "Hello from Main!" printed to console
python output/main_module/main.py
```

The generated code includes:

- A main module with functions to print "Hello from Main!" and return a greeting
- A utility module with logging and data processing functions

## Learning Outcomes

This example teaches more advanced concepts:

1. Working with multiple specification files
2. Composing recipes using the `execute_recipe` step
3. Building modular code generation pipelines
4. Generating multiple related files from specifications
5. Structuring more complex prompts for code generation

This example is ideal after understanding the basics from the simple example, showing how to scale up to more sophisticated code generation workflows.
