import logging
from typing import Any, Dict, Optional

from pydantic import Field

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template

# Import inside methods to avoid circular deps and unnecessary imports if not invoked


class McpConfig(StepConfig):
    """
    Configuration for McpStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key to store the tool result.
    """

    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = Field(default="tool_result")


class McpStep(BaseStep[McpConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, McpConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render all templated string fields in config
        rendered_server: Dict[str, Any] = {}
        for k, v in self.config.server.items():
            if isinstance(v, str):
                rendered_server[k] = render_template(v, context)
            else:
                rendered_server[k] = v
        tool_name: str = render_template(self.config.tool_name, context)
        result_key: str = render_template(self.config.result_key, context) if self.config.result_key else "tool_result"
        # Arguments: also resolve any string values as templates
        rendered_arguments: Dict[str, Any] = {}
        args = self.config.arguments or {}
        for k, v in args.items():
            if isinstance(v, str):
                rendered_arguments[k] = render_template(v, context)
            else:
                rendered_arguments[k] = v

        # Select connection type
        sse_client = None
        stdio_client = None
        ClientSession = None
        StdioServerParameters = None
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.sse import sse_client
            from mcp.client.stdio import stdio_client
        except ImportError as exc:
            raise ValueError("mcp package is required for McpStep but not installed.") from exc

        # Connect and call tool
        session = None
        tool_result: Optional[Any] = None
        try:
            # Decide client type based on config
            if "url" in rendered_server and rendered_server["url"]:
                url = rendered_server["url"]
                headers = rendered_server.get("headers")
                self.logger.debug(f"Connecting to MCP server via SSE at {url} (tool={tool_name})")
                async with sse_client(url, headers=headers) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        self.logger.debug(f"Calling tool '{tool_name}' with arguments: {rendered_arguments}")
                        tool_result = await session.call_tool(tool_name, arguments=rendered_arguments)
            elif "command" in rendered_server and rendered_server["command"]:
                command = rendered_server["command"]
                args_list = rendered_server.get("args", [])
                env = rendered_server.get("env")
                working_dir = rendered_server.get("working_dir")
                server_params = StdioServerParameters(
                    command=command,
                    args=args_list,
                    env=env,
                    cwd=working_dir,
                )
                self.logger.debug(
                    f"Connecting to MCP stdio server: {command} {args_list} (cwd={working_dir}, tool={tool_name})"
                )
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        self.logger.debug(f"Calling tool '{tool_name}' with arguments: {rendered_arguments}")
                        tool_result = await session.call_tool(tool_name, arguments=rendered_arguments)
            else:
                raise ValueError("Invalid MCP server configuration: must provide either 'url' or 'command'.")
        except Exception as exc:
            # Wrap in ValueError with details as spec requires
            server_info = rendered_server.get("url") or rendered_server.get("command") or str(rendered_server)
            raise ValueError(f"Failed to call MCP tool '{tool_name}' on service '{server_info}': {exc}") from exc

        # Convert the result to dict if possible
        # If not already a dict, try to use .dict() if available, otherwise as-is
        result_dict: Dict[str, Any]
        if isinstance(tool_result, dict):
            result_dict = tool_result
        elif hasattr(tool_result, "dict"):
            result_dict = tool_result.dict()  # type: ignore
        else:
            result_dict = {"result": tool_result}

        context[result_key] = result_dict
