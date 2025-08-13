# Document Generator

Recipes for generating comprehensive documents from structured JSON outlines, with support for creating and consuming portable docpack files.

## Recipe Overview

The document generator provides four main workflows:

1. **Direct document generation** - Generate documents from pre-existing JSON outlines
2. **Two-step generation** - Generate outline from resources, then generate document
3. **Docpack creation** - Create portable docpack files from resource files and descriptions  
4. **Docpack consumption** - Extract docpack files and generate documents from their contents

## Recipes

### Core Recipes

#### `document_generator_recipe.json`
Core recipe for generating documents from JSON outlines with embedded resource files.

#### `recipes/generate_outline.json`  
Generates a JSON outline from resource files and a document description. Can be used standalone.

### Docpack Recipes

#### `generate_docpack.json` 
Creates a portable `.docpack` file containing an outline and embedded resource files.

#### `generate_document_from_docpack.json`
Extracts a `.docpack` file and generates the final document from its contents.

## Quick Examples

### Direct Document Generation
```bash
# Basic usage
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=recipes/document_generator/examples/readme.json

# With custom parameters
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=custom/outline.json \
   output_root=output/docs
```

### Two-Step Generation (Outline → Document)
```bash
# Step 1: Generate outline from resource files
recipe-tool --execute recipes/document_generator/recipes/generate_outline.json \
  document_description="Comprehensive README analyzing Recipe Executor architecture and implementation" \
  resources=ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md,ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md \
  output_root=output

# Step 2: Generate document from the created outline
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
  outline_file=output/outline.json \
  output_root=output
```

### Docpack Workflow (Portable)
```bash
# Step 1: Create docpack from resource files
recipe-tool --execute recipes/document_generator/generate_docpack.json \
  document_description="Generate a comprehensive README analyzing the Recipe Executor architecture and implementation" \
  resources=ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md,ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md \
  docpack_name="recipe_executor_readme.docpack" \
  output_root=output

# Step 2: Generate final document from docpack
recipe-tool --execute recipes/document_generator/generate_document_from_docpack.json \
  docpack_path=output/recipe_executor_readme.docpack \
  output_root=output
```

## Docpack Format

Docpack files (`.docpack`) are portable ZIP archives containing:
- `outline.json` - Generated document structure and resource references
- `files/` directory - All referenced resource files

This allows documents to be generated on one system and processed on another, with all dependencies included.

## Array Parameter Support

The docpack recipes support CLI array parameters using comma-separated syntax:

```bash
# Multiple resource files
resources=file1.md,file2.csv,file3.txt

# Equivalent to programmatic: ["file1.md", "file2.csv", "file3.txt"]
```

## Examples with Repository Files

Using files from this repository:

```bash
# Create docpack analyzing Recipe Executor 
recipe-tool --execute recipes/document_generator/generate_docpack.json \
  document_description="Technical analysis of Recipe Executor architecture" \
  resources=ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md,ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md \
  docpack_name="analysis.docpack"

# Create docpack analyzing project structure
recipe-tool --execute recipes/document_generator/generate_docpack.json \
  document_description="Project overview and implementation guide" \
  resources=README.md,CLAUDE.md \
  docpack_name="project_guide.docpack"
```

JSON outline format: `title`, `general_instructions`, `resources` array, and `sections` array. See `examples/readme.json`.
