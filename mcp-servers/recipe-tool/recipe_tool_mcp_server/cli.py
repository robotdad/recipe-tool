"""Command-line interface for the Recipe Tool MCP server."""

import argparse
import sys
from typing import List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from recipe_tool import create_recipe as cli_create
from recipe_tool import execute_recipe as cli_execute

# Load environment variables from .env if present
load_dotenv()


def create_mcp_server(host: str = "localhost", port: int = 3002) -> FastMCP:
    """Create the MCP server with recipe tools."""
    mcp = FastMCP("Recipe Tool Server")

    @mcp.tool()
    async def execute_recipe(recipe_path: str, context: dict[str, str] | None = None, log_dir: str = "logs") -> str:
        """
        Execute a recipe JSON file.
        """
        # Convert context dict to CLI-style key=value strings
        context_list = [f"{k}={v}" for k, v in (context or {}).items()]
        # Call the underlying recipe-tool logic
        await cli_execute(recipe_path, context_list, log_dir)
        return f"Recipe executed successfully (logs in {log_dir})"

    @mcp.tool()
    async def create_recipe(idea_path: str, context: dict[str, str] | None = None, log_dir: str = "logs") -> str:
        """
        Create a recipe from an idea file.
        """
        context_list = [f"{k}={v}" for k, v in (context or {}).items()]
        await cli_create(idea_path, context_list, log_dir)
        return f"Recipe created successfully (logs in {log_dir})"

    return mcp


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Recipe Tool MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        nargs="?",
        default="stdio",
        help="Transport protocol to use (stdio or sse, default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3002,
        help="Port for SSE server (default: 3002)",
    )

    args = parser.parse_args(argv)

    try:
        # Create the MCP server with the specified settings
        mcp = create_mcp_server(host=args.host, port=args.port)

        # Run the server with the appropriate transport
        print(f"Starting Recipe Tool MCP server with {args.transport} transport")
        if args.transport == "sse":
            print(f"Server URL: http://{args.host}:{args.port}/sse")

        mcp.run(transport=args.transport)
        return 0
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def stdio_main() -> int:
    """Convenience entry point for stdio transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    return main(["stdio"])


def sse_main() -> int:
    """Convenience entry point for SSE transport.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Get any command-line arguments after the script name
    argv = sys.argv[1:]

    # Pre-populate the 'transport' argument
    all_args = ["sse"] + argv

    return main(all_args)


if __name__ == "__main__":
    sys.exit(main())
