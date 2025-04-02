# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both FileGenerationResult and list of FileSpec formats
- Create directories as needed for file paths
- Apply template rendering to file paths
- Provide appropriate logging for file operations
- Follow minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Component Dependencies

The WriteFilesStep component depends on:

- **Steps Base** - Extends BaseStep with a specific config type
- **Context** - Retrieves file content from the context
- **Models** - Uses FileGenerationResult and FileSpec models
- **Utils** - Uses render_template for path resolution

## Error Handling

- Validate that the artifact exists in context
- Ensure artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Future Considerations

- Dry-run mode that logs without writing
