# 🌐 Recipe Tool MCP

MCP server exposing recipe-tool CLI capabilities for AI assistants.

## Quick Start

```bash
make install                        # From workspace root
recipe-tool-mcp-server              # stdio transport (default)
recipe-tool-mcp-server sse --port 3002  # SSE transport
```

## Tools

- `execute_recipe` - Execute recipe JSON files
- `create_recipe` - Create recipes from idea files

See the [main README](../../README.md) for setup and transport options.