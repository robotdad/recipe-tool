"""Command-line interface for the Documentation MCP server."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from .config import DocsServerSettings
from .server import create_docs_server

# Load environment variables from .env if present
load_dotenv()


def parse_doc_paths(paths_str: str) -> List[Path]:
    """Parse comma-separated list of documentation paths."""
    if not paths_str:
        return [Path(".")]

    paths = []
    for path_str in paths_str.split(","):
        path_str = path_str.strip()
        if path_str:
            paths.append(Path(path_str))

    return paths


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="Documentation MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Serve current directory documentation via stdio
  docs-server
  
  # Serve specific directories via SSE
  docs-server sse --paths "/path/to/docs,/another/path"
  
  # Use custom file patterns
  docs-server --include "*.md,*.rst,*.txt" --exclude "test_*,.*"
  
  # Configure via environment variables
  export DOCS_SERVER_DOC_PATHS="/home/user/project/docs"
  export DOCS_SERVER_INCLUDE_PATTERNS="*.md,*.txt"
  docs-server
        """,
    )

    parser.add_argument(
        "transport",
        choices=["stdio", "sse"],
        nargs="?",
        default="stdio",
        help="Transport protocol to use (stdio or sse, default: stdio)",
    )

    parser.add_argument(
        "--paths",
        help="Comma-separated list of documentation paths (default: current directory)",
    )

    parser.add_argument(
        "--include",
        help="Comma-separated list of file patterns to include (default: *.md,*.txt,*.rst)",
    )

    parser.add_argument(
        "--exclude",
        help="Comma-separated list of file patterns to exclude (default: .*,__pycache__,*.pyc)",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE server (default: localhost)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3003,
        help="Port for SSE server (default: 3003)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching of documentation content",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON configuration file",
    )

    args = parser.parse_args(argv)

    try:
        # Load settings from environment and defaults
        settings = DocsServerSettings()

        # Load from config file if provided
        if args.config and args.config.exists():
            with open(args.config) as f:
                config_data = json.load(f)
                settings = DocsServerSettings(**config_data)

        # Override with command line arguments
        if args.paths:
            settings.doc_paths = parse_doc_paths(args.paths)

        if args.include:
            settings.include_patterns = [p.strip() for p in args.include.split(",")]

        if args.exclude:
            settings.exclude_patterns = [p.strip() for p in args.exclude.split(",")]

        if args.no_cache:
            settings.enable_cache = False

        settings.host = args.host
        settings.port = args.port

        # Create and run the server
        mcp = create_docs_server(settings)

        print(f"Starting Documentation MCP server with {args.transport} transport")
        print(f"Documentation paths: {', '.join(str(p) for p in settings.doc_paths)}")
        print(f"Include patterns: {', '.join(settings.include_patterns)}")
        print(f"Exclude patterns: {', '.join(settings.exclude_patterns)}")

        if args.transport == "sse":
            print(f"Server URL: http://{settings.host}:{settings.port}/sse")

        mcp.run(transport=args.transport)
        return 0

    except KeyboardInterrupt:
        print("\nServer stopped", file=sys.stderr)
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
