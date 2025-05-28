Goal: Create a new recipe named analyze_codebase.json, for analyzing a codebase from an input file.

Context variables:

- input: The file path to the codebase file(s).
- model (optional): The model to use for generating the recipe. Defaults to openai/o4-mini.
- output_root (optional)`: Where to write the generated analysis file. Defaults to output.

Steps:

- Read the codebase file(s).
- Ask the LLM to generate the analysis from the codebase file(s), saving it to "<project_name>\_analysis.md".
- Write the generated analysis file to the specified output root.
