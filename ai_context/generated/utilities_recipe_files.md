=== File: recipes/utilities/create_recipe_json.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "recipe_idea"
    },
    {
      "type": "read_files",
      "path": [
        "ai_context/generated/recipe_executor_code_files.md",
        "ai_context/generated/recipe_executor_recipe_files.md"
      ],
      "artifact": "context_files",
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "Create a new JSON recipe file for use with recipe executor based on the following content:\n\n- Recipe Idea: {{recipe_idea}}\n- Context Files:\n  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>\n  {% if additional_files != '' %}\n- Additional Files:\n  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>\n  {% endif %}\n\nSave the generated recipe file as `generated_recipe.json` unless a different name is specified in the recipe idea.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_recipe"
    },
    {
      "type": "write_files",
      "artifact": "generated_recipe",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/utilities/generate_from_files.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{ files }}",
      "artifact": "combined_input",
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "{% if combined_input != '' %}{{combined_input}}{% else %}A request was made to generate a response based upon some files that were read in, but no files were received, please respond with an `error.md` file that contains a message indicating that no files were read and that 'context.path' must contain a valid list of files.{% endif %}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "llm_response"
    },
    {
      "type": "write_files",
      "artifact": "llm_response",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/utilities/project_split_analysis.json ===
{
  "recipe_idea": "project_split_analysis.json",
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "input_file",
      "optional": false,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": [
        "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
        "ai_context/IMPLEMENTATION_PHILOSOPHY.md"
      ],
      "artifact": "context_files",
      "optional": false,
      "merge_mode": "concat"
    },
    {
      "type": "read_files",
      "path": "{{files}}",
      "artifact": "additional_files",
      "optional": true,
      "merge_mode": "concat"
    },
    {
      "type": "generate",
      "prompt": "Create a new project breakdown analysis based on the following content:\n\n- Project Definition: {{input_file}}\n- Context Files:\n  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>\n  {% if additional_files != '' %}\n- Additional Files:\n  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>\n  {% endif %}\n\nThe project breakdown analysis should be:\n\n- Based on the philosophies and such outlined in the context files.\n- A breakdown of the project into smaller, manageable components.\n- Complete, covering all required aspects of the project.\n- Modular, allowing for easy implementation and testing of each component in isolation.\n- Cohesive, ensuring that each component has a clear purpose and responsibility.\n- Loosely coupled, minimizing dependencies between components.\n- Testable, with clear guidelines for how to validate each component.\n- Documented, with clear instructions for how to use and interact with each component.\n\nFor each component, the analysis should include:\n\n- A description of the component's purpose and functionality.\n- A brief overview of why this component is \"right sized\" and does not need to be broken down further.\n- The contract for the component, including:\n  - The inputs and outputs of the component.\n  - The expected behavior of the component.\n  - Any edge cases or special considerations for the component.\n- How to test and validate the component.\n- Any dependencies or interactions with other components.\n- Any implementation details or requirements such as example code, libraries, or frameworks to use.\n\nSave this generated project breakdown analysis as `{{target_file|default:'project_component_breakdown_analysis.md'}}`, unless the `target_file` is set to a different value in the project definition.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_analysis"
    },
    {
      "type": "write_files",
      "artifact": "generated_analysis",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/utilities/prompts/create_recipe_json.md ===
## Goal

Create a new JSON recipe file for creating new JSON recipe files, named `create_recipe_json.json`.

## How

Start wtih upload of a **required** recipe idea file. This path is passed in via a context key of `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

After that, load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

Use the LLM (default set to use `openai:o3-mini`) to generate the content for a JSON recipe file:

```markdown
Create a new JSON recipe file for use with recipe executor based on the following content:

- Recipe Idea: {{recipe_idea}}
- Context Files:
  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>
  {% if additional_files != '' %}
- Additional Files:
  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>
  {% endif %}

Save the generated recipe file as `generated_recipe.json` unless a different name is specified in the recipe idea.
```

The final step should be to save the generated file. The root should be set to value of `output_root` variable, defaulting to the `output` directory.


=== File: recipes/utilities/prompts/project_split_analysis.md ===
recipe_idea: `project_split_analysis.json`

Start wtih upload of a **required** high-level project definition file. This path is passed in via a context key of `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`

After that, load any other files that are passed in via the `files` context variable. These files should be considered optional and stored in a variable called `additional_files`.

Use the LLM (default set to use `openai:o3-mini`) to generate a project breakdown analysis:

```markdown
Create a new project breakdown analysis based on the following content:

- Project Definition: {{input_file}}
- Context Files:
  <CONTEXT_FILES>{{context_files}}</CONTEXT_FILES>
  {% if additional_files != '' %}
- Additional Files:
  <ADDITIONAL_FILES>{{additional_files}}</ADDITIONAL_FILES>
  {% endif %}

The project breakdown analysis should be:

- Based on the philosophies and such outlined in the context files.
- A breakdown of the project into smaller, manageable components.
- Complete, covering all required aspects of the project.
- Modular, allowing for easy implementation and testing of each component in isolation.
- Cohesive, ensuring that each component has a clear purpose and responsibility.
- Loosely coupled, minimizing dependencies between components.
- Testable, with clear guidelines for how to validate each component.
- Documented, with clear instructions for how to use and interact with each component.

For each component, the analysis should include:

- A description of the component's purpose and functionality.
- A brief overview of why this component is "right sized" and does not need to be broken down further.
- The contract for the component, including:
  - The inputs and outputs of the component.
  - The expected behavior of the component.
  - Any edge cases or special considerations for the component.
- How to test and validate the component.
- Any dependencies or interactions with other components.
- Any implmentation details or requirements such as example code, libraries, or frameworks to use.

Save this generated project breakdown analysis as `{{target_file|default:'project_component_breakdown_analysis.md'}}`, unless the `target_file` is set to a different value in the project definition.
```

The final step should be to save the generated file. The root should be set to value of `output_root` variable, defaulting to the `output` directory.


=== File: recipes/utilities/prompts/recipe_creator-future_version.md ===
Create a new JSON recipe file in the current folder. It should be named `create_recipe.json`. The recipe should use the `read_files` step to load a file that contains a request for a recipe to be created, from context key `input`. This file should be configurable via context, and the default value should be an error message indicating that the file is missing. The loaded content should be stored in a variable called `input`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `ai_context/generated/recipe_executor_code_files.md`
- `ai_context/generated/recipe_executor_recipe_files.md`

The `input` value will be of type FileGenerationResult from the recipe executor, you will need to unpack that value properly to use it in the next `generate` step.

Pass the loaded content to a `generate` step that extracts values to `recipe_idea`, `additional_files`, and `target_file` from the loaded content if such values are present. If the values are not present, assume the request is actually the recipe idea and set `recipe_idea` to the loaded content. The `additional_files` value should be a comma-separated list of files to be loaded into context, and the `target_file` value should be the name of the file to save the generated recipe to.

The next step should be another `generate` step that should _start with_:

```
Create a new recipe file based on the following content:
- Recipe Idea: {recipe_idea}
- Context Files: {context_files}
{% if additional_files != '' %}
- Additional Files: {additional_files}
{% endif %}

Save the generated recipe file as {{target_file|default:'generated_recipe.json'}}.
```

Default model for this recipe should be: `openai:o3-mini`

The final step should be a `write_files` step that saves the generated recipe file to the specified target file. The `root` should be set to: {{output_root|default:'output'}}

Consider the ideas and patterns expressed in _this_ request as good practices to append to the end of the generated recipe's generation prompt.


=== File: recipes/utilities/prompts/split_to_components.md ===
recipe_idea:
Create a new JSON receipe file for recipe executor that will all me to use read_files to load a breakdown analysis of a large project that is passed in via a context key of `input`. The default value should be an error message indicating that the file is missing. Place the contents into the context as `project_analysis`.

The next step should load the following files into context as `context_files`:

- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`

The next step should be a `read_files` step that loads any paths from the `files` context variable, storing content in a variable called `additional_files`. These files should be considered optional.

The next step should be a `generate` step that should _start with_:

```
Review the project analysis and break it down into individual components that contain detailed spefications for each component (split into file per component) that includes all of the details necessary to implement a version of that component based upon the `additional_files` and the philosophies and such outlined in these files I'm sharing with you. The `additional_files` may include some of component candidate specs that have already been created, in this case you can skip those ones. If there are no more components needed for the current break down, return a file named `completed_breakdown_report` with the final list of all of the component candidate specs. Default value for the target files for the components should be `<component_id>_candidate_spec.md` and the default model for this recipe should be `openai:o3-mini`.

- Recipe Idea: {{recipe_idea}}
{% if additional_files != '' %}
- Additional Files: {{additional_files}}
{% endif %}
- Context Files: {{context_files}}

Save one file per component, as `<component_id>_candidate_spec.md`.
```

Default model for this recipe should be: `openai:o3-mini`

The final step should be a `write_files` step that saves each of the generated recipe files to their requested file names. The `root` should be set to: {{output_root|default:'output'}}

Make sure to use double curly braces for all template variables in the recipe for use with liquid templating.

Consider the ideas and patterns expressed in _this_ request as good practices to append to the end of the generated recipe's generation prompt.

save this recipe as: split_to_components.json


=== File: recipes/utilities/split_to_components.json ===
{
  "steps": [
    {
      "type": "read_files",
      "path": "{{input}}",
      "artifact": "project_analysis",
      "optional": true,
      "default": "Error: breakdown analysis file is missing"
    },
    {
      "type": "read_files",
      "path": [
        "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
        "ai_context/IMPLEMENTATION_PHILOSOPHY.md"
      ],
      "artifact": "context_files"
    },
    {
      "type": "read_files",
      "path": "{{files}}",
      "artifact": "additional_files",
      "optional": true,
      "merge_mode": "dict"
    },
    {
      "type": "generate",
      "prompt": "Review the project analysis and break it down into individual components that contain detailed specifications for each component (split into file per component) that includes all of the details necessary to implement a version of that component based upon the `additional_files` and the philosophies and such outlined in these files I'm sharing with you. The `additional_files` may include some of component candidate specs that have already been created, in this case you can skip those ones. If there are no more components needed for the current break down, return a file named `completed_breakdown_report` with the final list of all of the component candidate specs. Default value for the target files for the components should be `<component_id>_candidate_spec.md` and the default model for this recipe should be `openai:o3-mini`.\n\n- Recipe Idea: {{recipe_idea}}\n{% if additional_files != '' %}\n- Additional Files: {{additional_files}}\n{% endif %}\n- Context Files: {{context_files}}",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_components"
    },
    {
      "type": "write_files",
      "artifact": "generated_components",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


