"""
MCPStep component for invoking tools on remote MCP servers and storing results in context.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult

from recipe_executor.steps.base import BaseStep, ContextProtocol, StepConfig
from recipe_executor.utils.templates import render_template


class MCPConfig(StepConfig):  # type: ignore
    """
    Configuration for MCPStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key under which to store the tool result.
    """
    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = "tool_result"


class MCPStep(BaseStep[MCPConfig]):  # type: ignore
    """
    Step that connects to an MCP server, invokes a tool, and stores the result in the context.
    """
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        cfg = MCPConfig.model_validate(config)  # type: ignore
        super().__init__(logger, cfg)

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve the tool name
        tool_name: str = render_template(self.config.tool_name, context)

        # Resolve arguments
        raw_args: Dict[str, Any] = self.config.arguments or {}
        arguments: Dict[str, Any] = {}
        for key, value in raw_args.items():
            if isinstance(value, str):
                arguments[key] = render_template(value, context)
            else:
                arguments[key] = value

        server_conf: Dict[str, Any] = self.config.server
        service_desc: str
        client_cm: Any

        # Choose transport based on server config
        if "command" in server_conf:
            # stdio transport
            cmd: str = render_template(server_conf.get("command", ""), context)
            raw_args_list = server_conf.get("args", []) or []
            args_list: List[str] = []
            for item in raw_args_list:
                if isinstance(item, str):
                    args_list.append(render_template(item, context))
                else:
                    args_list.append(str(item))

            # Environment variables
            config_env: Optional[Dict[str, str]] = None
            if server_conf.get("env") is not None:
                config_env = {}
                for env_k, env_v in server_conf.get("env", {}).items():
                    if isinstance(env_v, str):
                        rendered = render_template(env_v, context)
                        # Load from .env if empty
                        if rendered == "":
                            env_file = os.path.join(os.getcwd(), ".env")
                            if os.path.exists(env_file):
                                load_dotenv(env_file)
                                env_value = os.getenv(env_k)
                                if env_value is not None:
                                    rendered = env_value
                        config_env[env_k] = rendered
                    else:
                        config_env[env_k] = str(env_v)

            # Working directory
            cwd: Optional[str] = None
            if server_conf.get("working_dir") is not None:
                cwd = render_template(server_conf.get("working_dir", ""), context)

            server_params = StdioServerParameters(
                command=cmd,
                args=args_list,
                env=config_env,
                cwd=cwd,
            )
            client_cm = stdio_client(server_params)
            service_desc = f"stdio command '{cmd}'"
        else:
            # SSE transport
            url: str = render_template(server_conf.get("url", ""), context)
            headers_conf: Optional[Dict[str, Any]] = None
            if server_conf.get("headers") is not None:
                headers_conf = {}
                for hk, hv in server_conf.get("headers", {}).items():
                    if isinstance(hv, str):
                        headers_conf[hk] = render_template(hv, context)
                    else:
                        headers_conf[hk] = hv
            client_cm = sse_client(url, headers=headers_conf)
            service_desc = f"SSE server '{url}'"

        # Connect and invoke tool
        self.logger.debug(f"Connecting to MCP server: {service_desc}")
        try:
            async with client_cm as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    self.logger.debug(
                        f"Invoking tool '{tool_name}' with arguments {arguments}"
                    )
                    try:
                        result: CallToolResult = await session.call_tool(
                            name=tool_name,
                            arguments=arguments,
                        )
                    except Exception as e:
                        raise ValueError(
                            f"Tool invocation failed for '{tool_name}' on {service_desc}: {e}"
                        ) from e
        except ValueError:
            # Propagate invocation errors
            raise
        except Exception as e:
            raise ValueError(
                f"Failed to call tool '{tool_name}' on {service_desc}: {e}"
            ) from e

        # Convert result to a dictionary
        try:
            result_dict: Dict[str, Any] = result.__dict__  # type: ignore
        except Exception:
            result_dict = {
                attr: getattr(result, attr)
                for attr in dir(result)
                if not attr.startswith("_")
            }

        # Store result in context
        context[self.config.result_key] = result_dict
