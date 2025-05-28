# recipes/recipe_creator

[collect-files]

**Search:** ['recipes/recipe_creator']
**Exclude:** ['.venv', 'node_modules', '*.lock', '.git', '__pycache__', '*.pyc', '*.ruff_cache', 'logs', 'output']
**Include:** []
**Date:** 5/28/2025, 7:14:48 AM
**Files:** 5

=== File: recipes/recipe_creator/create.json ===
{
  "steps": [
    {
      "type": "set_context",
      "config": {
        "key": "recipe_root",
        "value": "{{ recipe_root | default: 'recipes/recipe_creator' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "ai_context_root",
        "value": "{{ ai_context_root | default: 'ai_context' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "model",
        "value": "{{ model | default: 'openai/o4-mini' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "target_file",
        "value": "{{ target_file | default: 'generated_recipe.json' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_root",
        "value": "{{ output_root | default: 'output' }}"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ input }}",
        "content_key": "recipe_idea"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ files }}",
        "content_key": "additional_files",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ ai_context_root }}/generated/RECIPE_EXECUTOR_CODE_FILES.md,{{ ai_context_root }}/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md,{{ ai_context_root }}/generated/CODEBASE_GENERATOR_FILES.md,{{ ai_context_root }}/generated/RECIPE_JSON_AUTHORING_GUIDE.md,{{ ai_context_root }}/IMPLEMENTATION_PHILOSOPHY.md,{{ ai_context_root }}/MODULAR_DESIGN_PHILOSOPHY.md,{{ ai_context_root }}/git_collector/LIQUID_PYTHON_DOCS.md",
        "content_key": "context_files"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "model": "{{ model }}",
        "prompt": "Create a new JSON recipe file for use with recipe executor based on the following Recipe Idea:\n\n<RECIPE_IDEA>\n{{ recipe_idea }}\n</RECIPE_IDEA>\n\n{% if additional_files %}In addition, here are some additional files for reference (DO NOT INCLUDE THEM IN THE RECIPE ITSELF):\n\n<ADDITIONAL_FILES>\n{{ additional_files }}\n</ADDITIONAL_FILES>\n\n{% endif %}Here is some documentation, code, examples, and guides for the recipes concept for additional context when writing a recipe for the requested recipe idea (DO NOT INCLUDE THEM IN THE RECIPE ITSELF):\n\n<CONTEXT_FILES>\n{{ context_files }}\n</CONTEXT_FILES>\n\nThe output MUST be valid JSON: no comments, all strings should be on a single line within the file (use escape characters for newlines), but pretty-print with 2-space indents, etc.\n\nSave the generated recipe file as {{ target_file }} unless a different name is specified in the recipe idea.",
        "output_format": "files",
        "output_key": "generated_recipe"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_recipe",
        "root": "{{ output_root }}"
      }
    }
  ]
}


=== File: recipes/recipe_creator/examples/analyze-code-files-idea.md ===
Goal: Create a new recipe named analyze_codebase.json, for analyzing a codebase from an input file.

Context variables:

- input: The file path to the codebase file(s).
- model (optional): The model to use for generating the recipe. Defaults to openai/o4-mini.
- output_root (optional)`: Where to write the generated analysis file. Defaults to output.

Steps:

- Read the codebase file(s).
- Ask the LLM to generate the analysis from the codebase file(s), saving it to "<project_name>\_analysis.md".
- Write the generated analysis file to the specified output root.


=== File: recipes/recipe_creator/examples/demo-quarterly-report-idea.md ===
Goal:
Create a recipe that generates a quarterly business report by analyzing new performance data, comparing it with historical data, and producing a professional document with insights and visualizations.

How:

Input context variables:

- new_data_file: Path to the CSV file containing the latest quarterly data
- historical_data_file (optional): Path to the CSV file containing historical quarterly data
- company_name (optional): Name of the company for the report. Defaults to "Our Company"
- quarter (optional): Current quarter (e.g., "Q2 2025"). Will attempt to detect from data if not provided.
- output_root (optional): Directory to save the output report. Defaults to "output"
- model (optional): The model to use. Defaults to "openai/o4-mini"

Steps:

- Read the new quarterly data from the CSV file specified by the new_data_file variable
- Read historical data from the historical_data_file
- Process and analyze the data:
  - Calculate key performance metrics (revenue growth, customer acquisition, etc.)
  - Compare current quarter with historical trends
  - Identify significant patterns and outliers
  - If quarter is not provided, attempt to detect it from the new data
  - If historical data is not provided, use the new data to establish a baseline for the current quarter
- Use an LLM to generate insights and recommendations based on the analysis
- Use another LLM to create a comprehensive report that includes:
  - Executive summary
  - Key metrics with Mermaid charts (quarterly trends, product performance)
    - Make sure LLM is aware of the limited available mermaid diagram types:
      - pie
      - timeline
      - mindmap
      - gantt
      - stateDiagram-v2
      - classDiagram
      - sequenceDiagram
      - flowchart
  - Regional performance analysis
  - Strategic recommendations for next quarter
  - Report completion date
- Write the complete report as markdown to the output directory


=== File: recipes/recipe_creator/examples/recipe-to-mermaid-idea.md ===
Recipe goal:
Turn any existing recipe (JSON) into a ready-to-preview Mermaid diagram that follows the “collapsed-subgraph” style we like.

Set up the following inputs:

- recipe_path (required): Full path to the JSON recipe you want to visualize
- output_path: The folder to save the diagram to (default: `output`)
- diagram_filename: The filename to save the diagram to (Mermaid markdown file, default: same path as filename part of `recipe_path` but with \*.md)
- model: LLM to use to generate the diagram (default: openai/o4-mini)

Steps:

1. Read the target recipe file

- Load the entire file found at `recipe_path`

2. Ask the LLM to produce the diagram

- Invoke the model specified by `model`
- Provide this system instruction:

  > “You are an expert in the Recipe-Executor JSON format.
  > Output only a Mermaid flow-chart that follows these rules:
  > • Each `execute_recipe` becomes its own collapsed subgraph named after the file.
  > • Insert an entry node (💬) at the call site and an exit node (⬆︎) when the sub-recipe returns.
  > • Use unique IDs like `<STEM>_S0`, `<STEM>_S1`, etc.
  > • For loops, render a `loop` node followed by an indented subgraph for its sub-steps.
  > • For conditionals, draw a diamond and separate IF_TRUE and IF_FALSE subgraphs.
  > • Provide a user-friendly label for each node.
  > • Do not include comments or Liquid templates in the output.
  > • Include proper line breaks and indentation.
  >
  > Here is the recipe JSON you must transform (between `<JSON>` tags):
  > `<JSON>` > {{ recipe_src }} > `</JSON>`

- Capture the model’s plain-text response as `mermaid_diagram`.\*

3. Write the diagram to disk

- Save `mermaid_diagram` to the file given by `diagram_path` (defaulting to the same folder and filename as `recipe_path`, but with a “.md” extension).\*


=== File: recipes/recipe_creator/examples/simple-spec-recipe-idea.md ===
Goal: Turn a simple text spec into a runnable Python script and save it.

Context variables:

- model (optional): LLM to use, default openai/o4-mini.
- spec_file: Folder with the spec.
- output_root (optional): Where to write files, default output.

Steps:

- Read spec_file.
- Ask the LLM to generate code that satisfies the spec.
- Write the returned file(s) into output_root.


