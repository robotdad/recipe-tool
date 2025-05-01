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
