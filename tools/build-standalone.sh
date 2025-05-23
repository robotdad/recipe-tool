#!/bin/bash
# Build a single package outside of the workspace
# Usage: ./tools/build-standalone.sh [package-name]
# Example: ./tools/build-standalone.sh recipe-tool

set -e

PACKAGE=${1:-recipe-tool}

echo "🔨 Building $PACKAGE as standalone package..."

# Validate package name
case $PACKAGE in
    "recipe-tool"|"recipe-executor"|"python-code-tools"|"recipe-tool-mcp-server"|"document-generator-app"|"recipe-executor-app"|"recipe-tool-app")
        ;;
    *)
        echo "❌ Unknown package: $PACKAGE"
        echo "Available packages:"
        echo "  Core Libraries: recipe-tool, recipe-executor"
        echo "  Apps: document-generator-app, recipe-executor-app, recipe-tool-app"
        echo "  MCP Servers: python-code-tools, recipe-tool-mcp-server"
        exit 1
        ;;
esac

# Determine package directory
case $PACKAGE in
    "recipe-tool")
        PACKAGE_DIR="recipe-tool"
        ;;
    "recipe-executor")
        PACKAGE_DIR="recipe-executor"
        ;;
    "python-code-tools")
        PACKAGE_DIR="mcp-servers/python-code-tools"
        ;;
    "recipe-tool-mcp-server")
        PACKAGE_DIR="mcp-servers/recipe-tool"
        ;;
    "document-generator-app")
        PACKAGE_DIR="apps/document-generator"
        ;;
    "recipe-executor-app")
        PACKAGE_DIR="apps/recipe-executor"
        ;;
    "recipe-tool-app")
        PACKAGE_DIR="apps/recipe-tool"
        ;;
esac

echo "📁 Package directory: $PACKAGE_DIR"

# Create temporary directory for standalone build
TEMP_DIR=$(mktemp -d)
echo "📦 Building in: $TEMP_DIR"

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up temporary directory..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Copy package to temp location
cp -r "$PACKAGE_DIR" "$TEMP_DIR/"
cd "$TEMP_DIR/$(basename $PACKAGE_DIR)"

echo "🔧 Setting up standalone build environment..."

# Create minimal uv project if not present
if [ ! -f "uv.lock" ]; then
    uv init --no-readme --no-src
fi

# Install dependencies and build
echo "📥 Installing dependencies..."
uv sync

echo "🏗️  Building package..."
uv build

# Copy results back
echo "📋 Build results:"
ls -la dist/

# Copy build artifacts back to original location
BUILD_DIR="$(pwd)/../../$PACKAGE_DIR/dist"
mkdir -p "$BUILD_DIR"
cp dist/* "$BUILD_DIR/"

echo "✅ Standalone build complete!"
echo "📦 Build artifacts copied to: $BUILD_DIR"
echo ""
echo "🚀 To install locally:"
echo "pip install $BUILD_DIR/*.whl"
echo ""
echo "🔍 To test:"
case $PACKAGE in
    "recipe-tool")
        echo "recipe-tool --help"
        ;;
    "recipe-executor")
        echo "recipe-executor --help"
        ;;
    "python-code-tools")
        echo "python-code-tools --help"
        ;;
    "recipe-tool-mcp-server")
        echo "recipe-tool-mcp-server --help"
        ;;
    "document-generator-app")
        echo "document-generator-app --help"
        ;;
    "recipe-executor-app")
        echo "recipe-executor-app --help"
        ;;
    "recipe-tool-app")
        echo "recipe-tool-app --help"
        ;;
esac
