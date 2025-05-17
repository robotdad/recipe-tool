# Instructions for Testing the Document Generator Recipe

## Run the Document Generator Recipe

```bash
# From the repo root, run the document generator recipe to create a readme for the codebase.
recipe-tool --execute recipes/document_generator/document-generator-recipe.json \
   outline_file=recipes/document_generator/examples/readme.json \
  output_root=output/docs \
  model=openai/o4-mini
```

While the recipe runs, progress information is printed to the console so you can
see each step being executed.
