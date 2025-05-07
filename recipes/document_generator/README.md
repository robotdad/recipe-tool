# Instructions for Testing the Recipe Docs recipe

## Run the Recipe Docs recipe

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/document_generator/build.json \
   outline_file=recipes/document_generator/recipe-json-authoring-guide.json \
   output_root=output/docs \
   model=openai/o4-mini
```
