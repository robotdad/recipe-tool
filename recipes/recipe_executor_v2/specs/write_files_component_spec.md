# WriteFileStep Component Specification

## Purpose

The WriteFileStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

1. Write one or more files to disk from the context
2. Support both FileGenerationResult and list of FileSpec formats
3. Create directories as needed for file paths
4. Apply template rendering to file paths
5. Provide appropriate logging for file operations
6. Follow minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Component Dependencies

The WriteFileStep component depends on:

1. **Steps Base** - Extends BaseStep with a specific config type
2. **Context** - Retrieves file content from the context
3. **Models** - Uses FileGenerationResult and FileSpec models
4. **Utils** - Uses render_template for path resolution

## Error Handling

- Validate that the artifact exists in context
- Ensure artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Future Considerations

1. File overwrite confirmation/protection
2. Custom file permissions and ownership
3. Support for binary file writing
4. Dry-run mode that logs without writing
