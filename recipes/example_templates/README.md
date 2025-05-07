# Example Templates

# Extras Demo

This example shows how to use the `extras` feature of the Python Liquid support in `recipe_executor` to create a Markdown file for each item in a JSON array.

## Run the Recipe

```bash
# From the repo root, run the recipe with the test project
recipe-tool --execute recipes/example_templates/extras_demo.json \
   input_file=recipes/example_templates/data/items.json \
   output_root=output/templates \
   model=openai/o4-mini
```

## What’s happening

- **`read_files`** loads your data file and pulls in a JSON array as `items`.
- **`loop`** iterates each `item` and:
  - creates a `slug` via `snakecase`
  - parses & reformats `item.timestamp` with `datetime`
  - pretty-prints `item.metadata` with `json`
- **`write_files`** spits out one Markdown file per item, using those context vars in both filename and body.
