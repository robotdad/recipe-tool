# Instructions for Testing the Blueprint Generator v4

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/blueprint_generator_v4/build.json \
   project_spec=blueprint_test/input/requirements_recipe_tool_ux.md \
   context_docs=blueprint_test/input/vision_recipe_tool_ux.md \
   output_dir=blueprint_test/output/blueprint_generator_v4 \
   model=openai/o4-mini
```

## Generate code from the blueprint

````bash
# Copy the generate code scripts from recipes/recipe_executor (TODO: move to a common location)
cp recipes/recipe_executor/build.json blueprint_test/output/blueprint_generator_v4/
# Copy the recipes/recipe_executor/recipes directory to the output directory
cp -r recipes/recipe_executor/recipes blueprint_test/output/blueprint_generator_v4/

# Copy the recipes/recipe_executor/components.json as a template
cp recipes/recipe_executor/components.json blueprint_test/output/blueprint_generator_v4/

# Edit the components.json file to include the components you want to generate
nano blueprint_test/output/blueprint_generator_v4/components.json

# Run the generate code script
```bash
recipe-tool --execute blueprint_test/output/youtube_viewer/build.json \
   output_root=blueprint_test/output/blueprint_generator_v4/code \
   output_path=blueprint_generator_v4 \
   recipe_root=blueprint_test/output/blueprint_generator_v4 \
   dev_guide_path=ai_context/DEV_GUIDE_FOR_PYTHON.md,ai_context/DEV_GUIDE_FOR_WEB.md \
   model=openai/o4-mini
````
