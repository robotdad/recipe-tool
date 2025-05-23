#!/bin/bash
# Development helper script
# Usage: ./scripts/dev.sh [command] [options]

set -e

case "$1" in
    "sync")
        echo "🔄 Syncing workspace..."
        uv sync --group dev
        ;;
    "test")
        if [ -n "$2" ]; then
            case "$2" in
                "core")
                    echo "🧪 Testing core libraries..."
                    uv run pytest recipe-executor/ recipe-tool/
                    ;;
                "apps")
                    echo "🧪 Testing apps..."
                    uv run pytest apps/
                    ;;
                "mcp")
                    echo "🧪 Testing MCP servers..."
                    uv run pytest mcp-servers/
                    ;;
                *)
                    echo "🧪 Testing package: $2"
                    uv run --package "$2" pytest
                    ;;
            esac
        else
            echo "🧪 Testing all packages..."
            uv run pytest
        fi
        ;;
    "lint")
        if [ -n "$2" ]; then
            echo "🔍 Linting package: $2"
            uv run ruff check "$2"
        else
            echo "🔍 Linting all packages..."
            uv run ruff check .
        fi
        ;;
    "format")
        if [ -n "$2" ]; then
            echo "✨ Formatting package: $2"
            uv run ruff format "$2"
        else
            echo "✨ Formatting all packages..."
            uv run ruff format .
        fi
        ;;
    "check")
        echo "🔍 Running full check..."
        uv run ruff check .
        uv run pyright
        uv run pytest --no-cov
        echo "✅ All checks passed!"
        ;;
    "build")
        if [ -n "$2" ]; then
            echo "📦 Building package: $2"
            uv build --package "$2"
        else
            echo "📦 Building all packages..."
            uv build --all
        fi
        ;;
    "clean")
        echo "🧹 Cleaning workspace..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        echo "✅ Workspace cleaned!"
        ;;
    "run")
        if [ -n "$2" ]; then
            echo "🚀 Running: $2"
            shift 2
            uv run "$2" "$@"
        else
            echo "❌ Please specify a command to run"
            exit 1
        fi
        ;;
    "refresh")
        echo "🔄 Refreshing workspace lock file..."
        rm -f uv.lock
        uv lock
        uv sync --group dev
        echo "✅ Workspace refreshed!"
        ;;
    *)
        echo "🛠️  Recipe Tool Workspace Development Helper"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  sync              - Install/update all dependencies"
        echo "  test [package]    - Run tests (all packages or specific package)"
        echo "    test core       - Test only core libraries (recipe-executor, recipe-tool)"
        echo "    test apps       - Test only apps (document-generator, recipe-executor-app, recipe-tool-app)"
        echo "    test mcp        - Test only MCP servers" 
        echo "  lint [package]    - Run linting (all packages or specific package)"
        echo "  format [package]  - Format code (all packages or specific package)"
        echo "  check             - Run full check (lint + types + tests)"
        echo "  build [package]   - Build packages (all or specific package)"
        echo "  clean             - Clean up generated files"
        echo "  run [command]     - Run arbitrary command with uv"
        echo "  refresh           - Refresh workspace lock file"
        echo ""
        echo "Examples:"
        echo "  $0 test recipe-tool"
        echo "  $0 test core"
        echo "  $0 test apps" 
        echo "  $0 lint recipe-executor"
        echo "  $0 run recipe-tool --help"
        ;;
esac
