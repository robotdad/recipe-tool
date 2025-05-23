# Instructions for Testing the Blueprint Generator v4

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/experimental/blueprint_generator_v4/build.json \
   project_spec=blueprints/experimental/requirements_recipe_tool_ux.md \
   context_docs=blueprints/experimental/vision_recipe_tool_ux.md \
   output_dir=output/blueprint_generator_v4 \
   model=openai/o4-mini
```

If any components have further details needed, a file will be created in the root of the output directory with the name of the component included as: `<component_name>_review_needed.md`.

Review these files and add any additional details needed to them and then change the file name to `<component_name>_review_provided.md`. After this, re-run the blueprint generator with the same command as above. This will cause the generator to read those files and use the information in them to update the in-progress blueprint and try to continue from there.

## Youtube Viewer Example with Code Generation

```bash
# Run the Youtube Viewer example
recipe-tool --execute recipes/experimental/blueprint_generator_v4/build.json \
   project_spec=blueprints/experimental/youtube_viewer.md \
   context_docs=blueprints/experimental/videos.json \
   output_dir=output/youtube_viewer \
   model=openai/o4-mini

# TODO: Handle this in the blueprint generator recipes
# Copy the code generation recipes from the recipe executor
cp recipes/recipe_executor/build.json output/youtube_viewer/
cp -r recipes/recipe_executor/recipes output/youtube_viewer/

# Create a simple components.json file
nano output/youtube_viewer/components.json
# Add single entry:
[
   {
      "id": "main",
      "deps": [],
      "refs": ["blueprints/experimental/videos.json"]
   }
]

# Run the code generation recipe
recipe-tool --execute output/youtube_viewer/build.json \
   output_root=output/youtube_viewer/code \
   output_path=youtube_viewer \
   recipe_root=output/youtube_viewer \
   dev_guide_path=ai_context/DEV_GUIDE_FOR_PYTHON.md,ai_context/DEV_GUIDE_FOR_WEB.md \
   model=openai/o4-mini
```
