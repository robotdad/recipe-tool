# MCPStep Component Usage

## Importing

```python
from recipe_executor.steps.mcp import MCPStep, MCPConfig
```

## Configuration

The MCPStep is configured with a `MCPConfig`:

```python
class MCPConfig(StepConfig):
    """
    Configuration for MCPStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key under which to store the tool result as a dictionary.
    """
    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = "tool_result"
```

The `server` field is a dictionary containing the server configuration, which can include:

For HTTP servers:

- `url`: str - the URL of the MCP server.
- `headers`: Optional[Dict[str, Any]] -headers to include in the request.

For stdio servers:

- `command`: str - the command to run the MCP server.
- `args`: List[str] - arguments to pass to the command.
- `env`: Optional[Dict[str, str]] - environment variables to set for the command.
  - If an env var is set to "", an attempt will be made to load the variable from the system environment variables and `.env` file.
- `working_dir`: The working directory for the command.

## Basic Usage in Recipes

The `MCPStep` is available via the `mcp` step type in recipes:

```json
{
  "steps": [
    {
      "type": "mcp",
      "config": {
        "server": {
          "url": "http://localhost:5000",
          "headers": {
            "api_key": "your_api_key"
          }
        },
        "tool_name": "get_stock",
        "arguments": { "item_id": "{{item_id}}" },
        "result_key": "stock_info"
      }
    }
  ]
}
```

After execution, the context contains:

```json
{
  "stock_info": {
    "item_id": 123,
    "name": "Widget",
    "price": 19.99,
    "in_stock": true,
    "quantity": 42
  }
}
```

## Template-Based Configuration

All string configuration fields support templating using context variables.
