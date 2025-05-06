# recipes/recipe_creator

[collect-files]

**Search:** ['recipes/recipe_creator']
**Exclude:** ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc', '*.ruff_cache']
**Include:** []
**Date:** 5/6/2025, 10:52:16 AM
**Files:** 3

=== File: recipes/recipe_creator/create.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{input}}",
        "content_key": "recipe_idea"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{files}}",
        "content_key": "additional_files",
        "optional": true,
        "merge_mode": "concat"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md,ai_context/generated/RECIPE_EXECUTOR_RECIPE_FILES.md,ai_context/RECIPE_JSON_AUTHORING_GUIDE.md,ai_context/IMPLEMENTATION_PHILOSOPHY.md,ai_context/MODULAR_DESIGN_PHILOSOPHY.md,ai_context/git_collector/LIQUID_PYTHON_DOCS.md,ai_context/RECIPE_JSON_AUTHORING_GUIDE.md",
        "content_key": "context_files",
        "merge_mode": "concat"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Create a new JSON recipe file for use with recipe executor based on the following Recipe Idea:\n\n<RECIPE_IDEA>\n{{recipe_idea}}\n</RECIPE_IDEA>\n\n{% if additional_files %}In addition, here are some additional files for reference (DO NOT INCLUDE THEM IN THE RECIPE ITSELF):\n\n<ADDITIONAL_FILES>\n{{additional_files}}\n</ADDITIONAL_FILES>\n\n{% endif %}Here is some documentation, code, examples, and guides for the recipes concept for additional context when writing a recipe for the requested recipe idea (DO NOT INCLUDE THEM IN THE RECIPE ITSELF):\n\n<CONTEXT_FILES>\n{{context_files}}\n</CONTEXT_FILES>\n\nThe output MUST be valid JSON: no comments, all strings should be on a single line within the file (use escape characters for newlines), etc.\n\nSave the generated recipe file as {{target_file | default:'generated_recipe.json'}} unless a different name is specified in the recipe idea.",
        "model": "{{model | default:'openai/o4-mini'}}",
        "output_format": "files",
        "output_key": "generated_recipe"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_recipe",
        "root": "{{output_root | default:'output'}}"
      }
    }
  ]
}


=== File: recipes/recipe_creator/recipe_ideas/create_recipe_json.md ===
## Goal

Create a new JSON recipe file for creating new JSON recipe files, named `create_recipe_json.json`.

## How

### Input context variables

- `input`: [Required] The file path to a recipe idea file.
- `files`: [Optional] A list of additional files to include in the recipe.
- `model`: [Optional] The model to use for generating the recipe. Defaults to `openai/o4-mini`.
- `output_root`: [Optional] The root directory for saving the generated recipe file. Defaults to `output`.
- `target_file`: [Optional] The name of the file to save the generated recipe to. Defaults to `generated_recipe.json` unless the recipe idea suggests a different name.

### Steps

1. Start with read of the recipe idea file (`input` context variable).

2. Always load the following files into context as `context_files`:

- `ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md`
- `ai_context/generated/RECIPE_EXECUTOR_RECIPE_FILES.md`
- `ai_context/RECIPE_JSON_AUTHORING_GUIDE.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/git_collector/LIQUID_PYTHON_DOCS.md`

3. Load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

4. Use the LLM (default set to use `openai/o4-mini`) to generate the content for a JSON recipe file:

{% raw %}

```markdown
Create a new JSON recipe file for use with recipe executor based on the following Recipe Idea:
<RECIPE_IDEA>
{{recipe_idea}}
</RECIPE_IDEA>

{% if additional_files %}
In addition, here are some additional files for reference (DO NOT INCLUDE THEM IN THE RECIPE ITSELF):
<ADDITIONAL_FILES>
{{additional_files}}
</ADDITIONAL_FILES>
{% endif %}

Here is some documentation, code, examples, and guides for the recipes concept for additional context when writing a recipe for the requested recipe idea (DO NOT INCLUDE THEM IN THE RECIPE ITSELF):
<CONTEXT_FILES>
{{context_files}}
</CONTEXT_FILES>

The output MUST be valid JSON: no comments, all strings should be on a single new within the file (use escape characters for newlines), etc.

Save the generated recipe file as {{target_file | default:'generated_recipe.json'}} unless a different name is specified in the recipe idea.
```

{% endraw %}

5. Save the generated file.

- The root should be set to value of `output_root` context variable, or `output` if not specified.


=== File: recipes/recipe_creator/recipe_ideas/sample_recipe_idea.md ===
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


