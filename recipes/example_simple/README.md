# Simple Recipe Example

Basic workflow demonstrating file reading, code generation, and writing.

## Quick Examples

```bash
# Generate code from a simple specification, producing a Hello World script.
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/hello-world-spec.txt
```

```bash
# Generate code for a Hello World app using Gradio.
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/hello-world-gradio-spec.md
```

```bash
# Generate a roll-up file from all text files in a directory.
recipe-tool --execute recipes/example_simple/code_from_spec_recipe.json \
   spec_file=recipes/example_simple/specs/file-rollup-tool-spec.md
```
