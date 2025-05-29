# Documentation MCP Server

An MCP (Model Context Protocol) server that provides access to project documentation files. This server allows AI assistants to read, search, and analyze documentation from configured directories.

## Features

- **List Documentation**: List all available documentation files and URLs
- **Read Files**: Read the contents of specific documentation files or URLs
- **Search**: Search for content across all documentation files and URLs
- **Statistics**: Get statistics about the documentation (file counts, sizes, etc.)
- **Caching**: Efficient caching system for better performance (works for both files and URLs)
- **URL Support**: Include remote documentation from URLs (e.g., GitHub raw files)
- **Flexible Configuration**: Configure via environment variables, CLI arguments, or config file

## Installation

```bash
# Install in development mode
make install

# Or install directly with uv
uv pip install -e .
```

## Usage

### Basic Usage

```bash
# Serve current directory documentation via stdio (default)
docs-server

# Serve specific directories
docs-server --paths "/path/to/docs,/another/path"

# Include URLs in documentation paths
docs-server --paths "/local/docs,https://raw.githubusercontent.com/user/repo/main/README.md"

# Use SSE transport
docs-server sse --port 3003
```

### Configuration Options

#### Command Line Arguments

- `--paths`: Comma-separated list of documentation paths
- `--include`: File patterns to include (default: `*.md,*.txt,*.rst`)
- `--exclude`: File patterns to exclude (default: `.*,__pycache__,*.pyc`)
- `--host`: Host for SSE server (default: localhost)
- `--port`: Port for SSE server (default: 3003)
- `--no-cache`: Disable content caching
- `--config`: Path to JSON configuration file

#### Environment Variables

```bash
export DOCS_SERVER_DOC_PATHS="/home/user/project/docs,/home/user/project/README.md,https://raw.githubusercontent.com/user/repo/main/docs/guide.md"
export DOCS_SERVER_INCLUDE_PATTERNS="*.md,*.txt"
export DOCS_SERVER_EXCLUDE_PATTERNS="test_*,.*"
export DOCS_SERVER_MAX_FILE_SIZE="2097152"  # 2MB
export DOCS_SERVER_ENABLE_CACHE="true"
export DOCS_SERVER_CACHE_TTL="300"  # 5 minutes (default)
```

#### Configuration File

Create a `config.json` file:

```json
{
  "doc_paths": [
    "/path/to/docs",
    "/another/path",
    "https://raw.githubusercontent.com/user/repo/main/README.md"
  ],
  "include_patterns": ["*.md", "*.rst", "*.txt"],
  "exclude_patterns": [".*", "test_*"],
  "max_file_size": 2097152,
  "enable_cache": true,
  "cache_ttl": 300
}
```

Then use it:

```bash
docs-server --config config.json
```

## MCP Tools

The server provides the following tools:

### `list_docs`
List all available documentation files.

**Returns**: List of file paths (absolute paths for local files, URLs as-is).

### `read_doc`
Read the contents of a documentation file.

**Parameters**:
- `file_path` (string): Path to the documentation file (can be relative or absolute)

**Returns**: The contents of the file, or an error message if the file cannot be read.

### `search_docs`
Search for documentation files containing the specified query.

**Parameters**:
- `query` (string): The search query string
- `max_results` (integer, optional): Maximum number of results to return (default: 10)

**Returns**: List of search results with file paths and matching snippets.

### `get_doc_stats`
Get statistics about the documentation.

**Returns**: Dictionary containing:
- `total_files`: Total number of documentation files
- `total_size_bytes`: Total size in bytes
- `total_size_mb`: Total size in megabytes
- `file_types`: Count of files by extension
- `doc_paths`: Configured documentation paths
- `cache_enabled`: Whether caching is enabled

### `clear_cache`
Clear the documentation cache and force a refresh.

**Returns**: Confirmation message.

## Integration with AI Assistants

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "docs": {
      "command": "docs-server",
      "args": [
        "--paths",
        "/path/to/your/docs,https://raw.githubusercontent.com/your/repo/main/README.md"
      ]
    }
  }
}
```

### Using with PydanticAI

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Configure the MCP server
server = MCPServerStdio(
    'docs-server',
    args=[
        '--paths',
        '/path/to/docs,https://raw.githubusercontent.com/user/repo/main/docs/api.md'
    ]
)

# Create agent with MCP server
agent = Agent('openai:gpt-4o', mcp_servers=[server])

# Use the agent
async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('What does the README say about installation?')
    print(result.output)
```

## Development

```bash
# Run tests
make test

# Format code
make format

# Lint code
make lint

# Type check
make type-check
```

## License

MIT