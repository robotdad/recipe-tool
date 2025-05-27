Goal: Create a new recipe for analyzing a codebase from a file roll-up, named analyze_codebase.json.

Context variables:

- input: The file path to the codebase roll-up file(s).
- model (optional): The model to use for generating the recipe. Defaults to openai/o4-mini.
- output_root (optional)`: Where to write the generated analysis file. Defaults to output.

Steps:

- Read the codebase roll-up file(s).
- Ask the LLM to generate the analysis from the codebase roll-up file(s), saving it to "<project_name>\_analysis.md".
- Write the generated analysis file to the specified output root.
