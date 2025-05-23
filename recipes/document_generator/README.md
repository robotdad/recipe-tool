# Document Generator

Recipe for generating comprehensive documents from structured JSON outlines.

## Quick Examples

```bash
# Basic usage
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=recipes/document_generator/examples/readme.json

# With custom parameters
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=custom/outline.json \
   output_root=output/docs
```

JSON outline format: `title`, `general_instructions`, and `sections` array. See `examples/readme.json`.
