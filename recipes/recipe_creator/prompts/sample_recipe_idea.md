## Goal

Create a new recipe for analyzing a codebase from a file roll-up, named `analyze_codebase.json`.

## How

### Input context variables

- `input`: [Required] The file path to the codebase roll-up file(s).
- `model`: [Optional] The model to use for generating the recipe. Defaults to `openai/o4-mini`.
- `output_root`: [Optional] The root directory for saving the generated recipe file. Defaults to `output`.

### Steps

1. Start with read of the codebase roll-up file(s) (`input` context variable).

2. Use the LLM (default set to use `openai/o4-mini`) to generate the analysis:

```markdown
Anayze the codebase from the following roll-up file(s):

- Codebase Roll-up: {{codebase_rollup}}

Save the generated analysis as `<project_name>_analysis.md`.
```

3. Save the generated file.

- The root should be set to value of `output_root` context variable, or `output` if not specified.
