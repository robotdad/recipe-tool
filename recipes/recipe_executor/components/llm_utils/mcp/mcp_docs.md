# MCP Utility Usage

## Importing

```python
from recipe_executor.llm_utils.mcp import get_mcp_server
```

## Basic Usage

You can create an MCP server client using the `get_mcp_server` function. This function takes a logger and a configuration object as arguments.

```python
def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any]
) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.
    """
```

The configuration object should contain the necessary parameters for the MCP server. The function will create an instance of `MCPServer` based on the provided configuration.

For HTTP servers:

- `url`: str - the URL of the MCP server.
- `headers`: Optional[Dict[str, Any]] -headers to include in the request.

For stdio servers:

- `command`: str - the command to run the MCP server.
- `args`: List[str] - arguments to pass to the command.
- `env`: Optional[Dict[str, str]] - environment variables to set for the command.
  - If an env var is set to "", an attempt will be made to load the variable from the system environment variables and `.env` file.
- `working_dir`: The working directory for the command.

Use the provided `MCPServer` client to connect to an MCP server for external tool calls:

```python
from recipe_executor.llm_utils.mcp import get_mcp_server

mcp_server = get_mcp_server(
    logger=logger,
    config={
        "url": "http://localhost:3001/sse",
        "headers": {
            "Authorization": "{{token}}"
        }
    }
)

# List available tools
tools = await mcp_server.list_tools()
print([t.name for t in tools.tools])

# Call a specific tool
result = await mcp_server.call_tool("get_stock", {"item_id": 123})
print(result)
```

## Error Handling

Tools list and calls will raise exceptions on failures:

```python
try:
    result = await client.call_tool("bad_tool", {})
except RuntimeError as e:
    print(f"Tool call failed: {e}")
```

## Important Notes

- **MCPServer** does not maintain an active connection to the server. Each tool list/call creates a new connection.
