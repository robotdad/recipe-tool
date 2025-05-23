# 🌐 Python Code Tools MCP

MCP server providing Python code quality tools (Ruff linting/fixing) for AI assistants.

## Quick Start

```bash
make install                            # From workspace root
python-code-tools stdio                # stdio transport
python-code-tools sse --port 3001      # SSE transport
```

## Tools

- `lint_code` - Lint and fix Python code snippets
- `lint_project` - Lint and fix entire Python projects

See the [main README](../../README.md) for setup and transport options.
