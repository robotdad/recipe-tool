#!/bin/bash
# Build and publish packages in correct dependency order
# Usage: ./scripts/publish.sh [--dry-run] [--test-pypi]

set -e

DRY_RUN=false
TEST_PYPI=false
PUBLISH_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --test-pypi)
            TEST_PYPI=true
            PUBLISH_ARGS="--repository testpypi"
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo "🏗️  Building and publishing packages..."
if [ "$DRY_RUN" = true ]; then
    echo "🔍 DRY RUN MODE - No actual publishing"
fi

if [ "$TEST_PYPI" = true ]; then
    echo "🧪 Using Test PyPI"
fi

# Function to build and publish a package
build_and_publish() {
    local package_name=$1
    local package_path=$2
    
    echo ""
    echo "📦 Building $package_name..."
    
    # Clean previous builds
    rm -rf "$package_path/dist/" || true
    
    # Build the package
    uv build --package "$package_name"
    
    if [ "$DRY_RUN" = false ]; then
        echo "🚀 Publishing $package_name..."
        uv publish --package "$package_name" $PUBLISH_ARGS
        
        # Wait a bit for PyPI to process
        echo "⏳ Waiting for PyPI to process..."
        sleep 10
    else
        echo "📋 Would publish: $(ls $package_path/dist/)"
    fi
}

# Function to check if package exists on PyPI
check_package_exists() {
    local package_name=$1
    local version=$2
    
    if pip index versions "$package_name" 2>/dev/null | grep -q "$version"; then
        return 0  # exists
    else
        return 1  # doesn't exist
    fi
}

# Pre-flight checks
echo "🔍 Pre-flight checks..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "recipe-tool" ]; then
    echo "❌ Please run from the workspace root directory"
    exit 1
fi

# Check if we have credentials for publishing
if [ "$DRY_RUN" = false ]; then
    if [ -z "$TWINE_USERNAME" ] && [ -z "$UV_PUBLISH_TOKEN" ]; then
        echo "❌ No publishing credentials found. Set TWINE_USERNAME/TWINE_PASSWORD or UV_PUBLISH_TOKEN"
        exit 1
    fi
fi

# Check workspace is clean
if ! git diff --quiet HEAD; then
    echo "⚠️  Warning: Working directory has uncommitted changes"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run tests first
echo "🧪 Running tests..."
uv run pytest --no-cov

echo "✅ Pre-flight checks passed!"

# Publish in dependency order
echo ""
echo "📚 Publishing packages in dependency order..."

# 1. Python Code Tools (no internal dependencies)
build_and_publish "python-code-tools" "mcp-servers/python-code-tools"

# 2. Recipe Executor (depends on python-code-tools)
build_and_publish "recipe-executor" "recipe-executor"

# 3. Recipe Tool (depends on recipe-executor)
build_and_publish "recipe-tool" "recipe-tool"

# 4. Apps (depend on core libraries)
build_and_publish "document-generator-app" "apps/document-generator"
build_and_publish "recipe-executor-app" "apps/recipe-executor"
build_and_publish "recipe-tool-app" "apps/recipe-tool"

# 5. Recipe Tool MCP Server (depends on recipe-tool)
build_and_publish "recipe-tool-mcp-server" "mcp-servers/recipe-tool"

echo ""
echo "🎉 All packages published successfully!"

if [ "$TEST_PYPI" = true ]; then
    echo ""
    echo "🧪 Test installations:"
    echo "pip install --index-url https://test.pypi.org/simple/ recipe-tool"
else
    echo ""
    echo "🚀 Installation:"
    echo "pip install recipe-tool"
    echo ""
    echo "📝 Don't forget to:"
    echo "1. Create and push git tags for the releases"
    echo "2. Update version numbers for next development cycle"
fi
