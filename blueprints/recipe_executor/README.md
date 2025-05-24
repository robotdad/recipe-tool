# Recipe Executor Recipes

This directory contains the recipes used for generating the Recipe Executor components. These recipes demonstrate the self-generating capability of the Recipe Executor system.

## Generate the Recipe Executor Code

The Recipe Executor can generate its own codebase from a component manifest file and individual component documentation/specification files. This is done using the `codebase_generator` recipe.
To generate the codebase, you can run the following command:

```bash
# Generate the Recipe Executor codebase using the defaults
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json
```

This command will generate the codebase for the Recipe Executor, using the existing code as a reference and adjusting for changes to the source documentation/specification files.
Instead of generating the entire codebase, you can generate just the code for a specific module. For example, to generate the code for the `steps.llm_generate` module, run:

```bash
# Generate code for a specific module
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
    edit=true \
    component_id=steps.llm_generate
```

You can also run with `edit` set to `false` to generate code without using the existing code as a reference.

```bash
# Generate code without using existing code as a reference
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
    edit=false
```

See the [codebase_generator](../../recipes/codebase_generator/README.md) recipe documentation for more details on the parameters you can specify.

## Generating Documentation

The Recipe Executor can generate its own documentation using the `document_generator` recipe. This is useful for creating up-to-date documentation based on the current state of the codebase.
To generate documentation, you can run the following command:

```bash
# Generate documentation for the Recipe Executor
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
    outline_file=blueprints/recipe_executor/outlines/recipe-json-authoring-guide.json \
    output_root=output/docs \
    model=openai/o4-mini
```

This command will create documentation from a structured outline configuration file, reading in referenced resources, including sections for each component, their specifications, and any relevant resources. The generated documentation will be saved in the specified output directory.

See the [document_generator](../../recipes/document_generator/README.md) recipe documentation for more details on the parameters you can specify.
