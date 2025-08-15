# DocpackCreateStep Component Usage

## Importing

```python
from recipe_executor.steps.docpack_create import DocpackCreateStep, DocpackCreateConfig
```

## Configuration

### DocpackCreateConfig Parameters

```python
class DocpackCreateConfig(StepConfig):
    """
    Configuration for DocpackCreateStep.

    Fields:
        outline_path (str): Path to outline JSON file (may be templated).
        resource_files (Union[str, List[str]]): Comma-separated string or list of resource file paths (may be templated).
        output_path (str): Path for the created .docpack file (may be templated).
        output_key (Optional[str]): Context key to store result info (may be templated).
    """
    outline_path: str
    resource_files: Union[str, List[str]]
    output_path: str
    output_key: Optional[str] = None
```

## Step Registration

The DocpackCreateStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.docpack_create import DocpackCreateStep

STEP_REGISTRY["docpack_create"] = DocpackCreateStep
```

## Usage in Recipes

### Basic Usage

```json
{
  "type": "docpack_create",
  "config": {
    "outline_path": "output/outline.json",
    "resource_files": "data/file1.txt,data/file2.csv",
    "output_path": "output/package.docpack"
  }
}
```

### With Template Variables

```json
{
  "type": "docpack_create", 
  "config": {
    "outline_path": "{{ output_root }}/outline.json",
    "resource_files": "{{ resources }}",
    "output_path": "{{ output_root }}/{{ docpack_name }}",
    "output_key": "docpack_result"
  }
}
```

### With Resource List from Context

```json
{
  "type": "docpack_create",
  "config": {
    "outline_path": "session/outline.json",
    "resource_files": "{{ resource_paths | join: ',' }}",
    "output_path": "session/bundle.docpack"
  }
}
```

## Context Integration

### Input Context Keys

The step reads configuration values and can resolve template variables from context:

- Resource file paths can be provided as comma-separated strings
- All path parameters support Liquid template rendering
- Template variables are resolved before file operations

### Output Context Keys

When `output_key` is specified, stores packaging results:

```python
{
    "output_path": "/path/to/created.docpack",
    "resource_count": 5,
    "success": True
}
```

## Integration with Other Steps

### Common Patterns

**After Outline Generation**:
```json
[
  {
    "type": "llm_generate",
    "config": {
      "prompt": "Generate document outline...",
      "output_key": "outline_json"
    }
  },
  {
    "type": "write_files",
    "config": {
      "files": [
        {
          "path": "{{ output_root }}/outline.json",
          "content": "{{ outline_json }}"
        }
      ]
    }
  },
  {
    "type": "docpack_create",
    "config": {
      "outline_path": "{{ output_root }}/outline.json",
      "resource_files": "{{ resources }}",
      "output_path": "{{ output_root }}/document.docpack"
    }
  }
]
```

**With Resource Collection**:
```json
[
  {
    "type": "read_files",
    "config": {
      "paths": ["data/*.txt", "templates/*.md"],
      "output_key": "collected_resources"
    }
  },
  {
    "type": "docpack_create",
    "config": {
      "outline_path": "config/outline.json", 
      "resource_files": "{{ collected_resources | map: 'path' | join: ',' }}",
      "output_path": "dist/package.docpack"
    }
  }
]
```

## Important Notes

- Outline file must exist and contain valid JSON before packaging
- Resource files are validated for existence before inclusion
- Missing resource files generate warnings but don't fail the packaging
- File name conflicts are automatically resolved with numeric suffixes
- The .docpack format is a ZIP archive compatible with standard tools
- All file paths support cross-platform compatibility via pathlib
- Template rendering occurs before any file operations