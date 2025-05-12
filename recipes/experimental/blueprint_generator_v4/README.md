# Instructions for Testing the Blueprint Generator v4

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/experimental/blueprint_generator_v4/build.json \
   project_spec=blueprint_test/input/requirements_recipe_tool_ux.md \
   context_docs=blueprint_test/input/vision_recipe_tool_ux.md \
   output_dir=blueprint_test/output/blueprint_generator_v4 \
   model=openai/o4-mini
```

## Youtube Viewer Example with Code Generation

```bash
# Run the Youtube Viewer example
recipe-tool --execute recipes/experimental/blueprint_generator_v4/build.json \
   project_spec=blueprint_test/input/youtube_viewer.md \
   context_docs=blueprint_test/input/videos.json \
   output_dir=blueprint_test/output/youtube_viewer \
   model=openai/o4-mini

# TODO: Handle this in the blueprint generator recipes
# Copy the code generation recipes from the recipe executor
cp recipes/recipe_executor/build.json blueprint_test/output/youtube_viewer/
cp -r recipes/recipe_executor/recipes blueprint_test/output/youtube_viewer/

# Create a simple components.json file
nano blueprint_test/output/youtube_viewer/components.json
# Add single entry:
[
   {
      "id": "main",
      "deps": [],
      "refs": ["blueprint_test/input/videos.json"]
   }
]

# Run the code generation recipe
recipe-tool --execute blueprint_test/output/youtube_viewer/build.json \
   output_root=blueprint_test/output/youtube_viewer/code \
   output_path=youtube_viewer \
   recipe_root=blueprint_test/output/youtube_viewer \
   dev_guide_path=ai_context/DEV_GUIDE_FOR_PYTHON.md,ai_context/DEV_GUIDE_FOR_WEB.md \
   model=openai/o4-mini
```
