# DocpackExtractStep Component Usage

## Importing

```python
from recipe_executor.steps.docpack_extract import DocpackExtractStep, DocpackExtractConfig
```

## Configuration

### DocpackExtractConfig Parameters

```python
class DocpackExtractConfig(StepConfig):
    """
    Configuration for DocpackExtractStep.

    Fields:
        docpack_path (str): Path to .docpack file to extract (may be templated).
        extract_dir (str): Directory to extract files to (may be templated).
        outline_key (str): Context key to store outline JSON (may be templated).
        resources_key (str): Context key to store resource file paths (may be templated).
    """
    docpack_path: str
    extract_dir: str
    outline_key: str = "outline_data"
    resources_key: str = "resource_files"
```

## Step Registration

The DocpackExtractStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.docpack_extract import DocpackExtractStep

STEP_REGISTRY["docpack_extract"] = DocpackExtractStep
```

## Usage in Recipes

### Basic Usage

```json
{
  "type": "docpack_extract",
  "config": {
    "docpack_path": "input/package.docpack",
    "extract_dir": "session/extracted"
  }
}
```

### With Custom Context Keys

```json
{
  "type": "docpack_extract",
  "config": {
    "docpack_path": "{{ input_docpack }}",
    "extract_dir": "{{ session_dir }}/unpacked",
    "outline_key": "imported_outline",
    "resources_key": "imported_resources"
  }
}
```

### With Template Variables

```json
{
  "type": "docpack_extract",
  "config": {
    "docpack_path": "uploads/{{ docpack_filename }}",
    "extract_dir": "{{ output_root }}/import_{{ timestamp }}",
    "outline_key": "user_outline",
    "resources_key": "user_resources"
  }
}
```

## Context Integration

### Input Context Keys

The step reads configuration values and resolves template variables from context:

- All path parameters support Liquid template rendering
- Template variables are resolved before file operations

### Output Context Keys

**Outline Data** (default key: `outline_data`):
```json
{
  "title": "Document Title",
  "general_instruction": "Document description",
  "resources": [
    {
      "key": "resource1",
      "path": "/extracted/path/file1.txt",
      "title": "Resource 1",
      "description": "First resource file"
    }
  ],
  "sections": [...]
}
```

**Resource Files** (default key: `resource_files`):
```json
[
  "/extracted/path/file1.txt",
  "/extracted/path/file2.csv",
  "/extracted/path/document.md"
]
```

## Integration with Other Steps

### Common Patterns

**Import and Process Docpack**:
```json
[
  {
    "type": "docpack_extract",
    "config": {
      "docpack_path": "{{ user_upload }}",
      "extract_dir": "{{ session_dir }}/imported",
      "outline_key": "imported_outline"
    }
  },
  {
    "type": "llm_generate",
    "config": {
      "prompt": "Enhance this outline: {{ imported_outline | json }}",
      "output_key": "enhanced_outline"
    }
  }
]
```

**Extract for Resource Processing**:
```json
[
  {
    "type": "docpack_extract",
    "config": {
      "docpack_path": "templates/base.docpack", 
      "extract_dir": "working/template",
      "resources_key": "template_files"
    }
  },
  {
    "type": "read_files",
    "config": {
      "paths": "{{ template_files }}",
      "output_key": "template_content"
    }
  }
]
```

**Recipe Bundle Extraction** (Future):
```json
[
  {
    "type": "docpack_extract",
    "config": {
      "docpack_path": "shared/recipe-bundle.docpack",
      "extract_dir": "{{ temp_dir }}/recipes",
      "outline_key": "recipe_manifest",
      "resources_key": "recipe_files"
    }
  },
  {
    "type": "execute_recipe",
    "config": {
      "recipe_path": "{{ temp_dir }}/recipes/main.json"
    }
  }
]
```

## File Organization

### Extraction Structure

When extracting a .docpack, files are organized as:

```
extract_dir/
├── outline.json          # Main outline file
└── files/               # Resource files subdirectory
    ├── resource1.txt
    ├── resource2.csv
    └── document.md
```

### Path Updates

- Resource paths in outline JSON are automatically updated to point to extracted locations
- Original filenames are preserved unless conflicts require renaming
- All paths use absolute paths for recipe compatibility

## Important Notes

- .docpack files must be valid ZIP archives with outline.json
- Missing or corrupted .docpack files will cause step failure
- Extraction directory is created automatically if it doesn't exist
- Resource paths in the outline are updated to absolute paths
- Files subdirectory contains all resource files from the archive
- Template rendering occurs before any file operations
- All file paths support cross-platform compatibility via pathlib