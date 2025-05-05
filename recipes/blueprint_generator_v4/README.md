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
