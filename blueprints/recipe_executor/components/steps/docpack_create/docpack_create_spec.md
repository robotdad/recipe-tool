# DocpackCreateStep Component Specification

## Purpose

The Docpack Create step packages outline JSON files and associated resource files into a single .docpack archive for distribution, sharing, or storage. It provides a secure, template-aware interface to the docpack-file library's create functionality within the recipe execution system.

## Core Requirements

- Create .docpack archives from outline JSON and resource files
- Support Liquid template rendering for all configuration parameters
- Validate input files exist before packaging
- Handle filename conflicts with automatic renaming
- Store results in context for subsequent steps
- Follow the standard step interface pattern with configuration validation
- Support both individual resource files and resource lists
- Provide clear error messages for missing or invalid inputs

## Implementation Considerations

- Use DocpackHandler.create_package() from docpack-file library directly
- Validate outline_path exists and is readable JSON before proceeding
- Convert resource file paths to Path objects for library compatibility
- Support template rendering for all path parameters
- Handle resource_files as either comma-separated string or list
- Use pathlib.Path for all file operations to ensure cross-platform compatibility
- Capture any packaging errors and re-raise with helpful context

### Type Annotation Guidelines

- Configuration fields should use concrete types (e.g., `str` for path fields)
- Method signatures should follow async patterns where appropriate for step consistency
- Use proper Union syntax when multiple types are needed (e.g., `Union[str, List[str]]`)
- Prefer standard library types and avoid incomplete type annotations

## Component Dependencies

### Internal Components

- **Base Step** - (Required) Inherits from BaseStep for standard step lifecycle
- **Context** - (Required) Uses Context to retrieve configuration and store results
- **Templates** - (Required) Uses render_template for dynamic path resolution

### External Libraries

- **docpack-file** - (Required) Uses DocpackHandler for .docpack creation functionality
- **pathlib** - (Required) Uses Path for file system operations
- **json** - (Required) Uses json.load for outline validation
- **pydantic** - (Required) Uses BaseModel for configuration validation

### Configuration Dependencies

None

## Output Files

- `recipe_executor/steps/docpack_create.py`

## Logging

- Debug: Log configuration parameters, input file paths, and successful packaging details
- Info: Log .docpack creation with output path and file count
- Error: Log specific errors for missing files, JSON parsing failures, or packaging errors

## Error Handling

- Validate outline_path exists and contains valid JSON before packaging
- Check that resource files exist and are readable
- Provide specific error messages identifying problematic files or paths
- Include original exception details for debugging packaging failures
- Raise ValueError for configuration issues, IOError for file system problems

## Dependency Integration Considerations

### DocpackHandler Integration

The step should use DocpackHandler.create_package() with proper error handling:

```python
DocpackHandler.create_package(
    outline_data=outline_data,
    resource_files=resource_file_paths,
    output_path=output_path
)
```

Where outline_data is loaded from the JSON file and resource_file_paths are converted to Path objects.