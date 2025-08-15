# DocpackExtractStep Component Specification

## Purpose

The Docpack Extract step unpacks .docpack archives to extract outline JSON files and associated resource files for use in recipe execution. It provides a secure, template-aware interface to the docpack-file library's extract functionality within the recipe execution system.

## Core Requirements

- Extract .docpack archives to specified directories
- Support Liquid template rendering for all configuration parameters
- Validate .docpack files before extraction
- Organize extracted files with clear directory structure
- Store extraction results in context for subsequent steps
- Follow the standard step interface pattern with configuration validation
- Update resource paths in outline JSON to point to extracted locations
- Provide detailed extraction metadata including file lists and paths

## Implementation Considerations

- Use DocpackHandler.extract_package() from docpack-file library directly
- Validate docpack_path exists and is a valid .docpack file before extraction
- Create extraction directory if it doesn't exist
- Support template rendering for all path parameters
- Use pathlib.Path for all file operations to ensure cross-platform compatibility
- Store both outline data and extracted file paths in context
- Handle extraction errors gracefully with helpful error messages  
- Preserve original file structure while updating paths for recipe compatibility
- Initialize `abs_resources` variable before try block to ensure it's always bound, even if path resolution fails

### Method Implementation Guidelines

- The execute method must be async (`async def execute(self, context: ContextProtocol) -> None:`) to match BaseStep interface
- Pass Path objects directly to DocpackHandler.extract_package() without string conversion
- Use proper error handling patterns for file operations and validation
- Ensure type safety in path resolution and context storage

## Component Dependencies

### Internal Components

- **Base Step** - (Required) Inherits from BaseStep for standard step lifecycle
- **Context** - (Required) Uses Context to retrieve configuration and store results
- **Templates** - (Required) Uses render_template for dynamic path resolution

### External Libraries

- **docpack-file** - (Required) Uses DocpackHandler for .docpack extraction functionality
- **pathlib** - (Required) Uses Path for file system operations
- **json** - (Required) Uses json.dumps/loads for outline data handling
- **pydantic** - (Required) Uses BaseModel for configuration validation

### Configuration Dependencies

None

## Output Files

- `recipe_executor/steps/docpack_extract.py`

## Logging

- Debug: Log configuration parameters, extraction directory, and detailed file list
- Info: Log successful extraction with .docpack path, destination, and file count
- Error: Log specific errors for missing files, invalid archives, or extraction failures

## Error Handling

- Validate docpack_path exists and is a readable .docpack file before extraction
- Check that extraction directory is writable or can be created
- Provide specific error messages identifying problematic files or paths
- Include original exception details for debugging extraction failures
- Raise ValueError for configuration issues, IOError for file system problems
- Handle corrupted or invalid .docpack files gracefully

## Dependency Integration Considerations

### DocpackHandler Integration

The step should use DocpackHandler.extract_package() with proper error handling:

```python
outline_data, resource_files = DocpackHandler.extract_package(
    docpack_path,
    extract_dir
)
```

The extracted outline_data and resource_files list should be stored in context with the specified keys for use by subsequent recipe steps.