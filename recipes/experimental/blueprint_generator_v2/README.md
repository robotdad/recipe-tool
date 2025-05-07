# Instructions for Testing the Blueprint Generator v2

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/experimental/blueprint_generator_v2/build.json \
   requirements_doc_path=blueprint_test/input/requirements_recipe_tool_ux.md \
   vision_doc_path=blueprint_test/input/vision_recipe_tool_ux.md \
   output_dir=blueprint_test/output/blueprint_generator_v2 \
   model=openai/o4-mini
```
