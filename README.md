# Recipe Tool Workspace

A collection of tools for executing natural language recipe-like instructions to create complex workflows. This workspace includes core libraries, user interface applications, and MCP protocol servers for recipe execution and creation.

**NOTE** This project is a very early, experimental project that is being explored in the open. There is no support offered and it will include frequent breaking changes. This project may be abandoned at any time. If you find it useful, it is strongly encouraged to create a fork and remain on a commit that works for your needs unless you are willing to make the necessary changes to use the latest version. This project is currently **NOT** accepting contributions and suggestions; please see the [docs/dev_guidance.md](docs/dev_guidance.md) for more details.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Getting Started

```bash
git clone https://github.com/microsoft/recipe-tool.git
cd recipe-tool
```

## Workspace Overview

This workspace is organized into several interconnected projects:

### 🏗️ Core Libraries & CLI Tools

- **`recipe-executor/`** - Core execution engine for JSON recipes (library + CLI)
- **`recipe-tool/`** - Recipe execution and creation from natural language (library + CLI)

### 📱 User Interface Applications

- **`apps/document-generator/`** - UX for using the document-generator recipe
- **`apps/recipe-executor/`** - UX for using the recipe-executor library
- **`apps/recipe-tool/`** - UX for recipe execution and creation features

### 🌐 MCP Protocol Servers

- **`mcp-servers/python-code-tools/`** - MCP server exposing Python coding tools
- **`mcp-servers/recipe-tool/`** - MCP server exposing recipe-tool capabilities

### 📄 Content Collections

- **`recipes/`** - JSON recipe files for execution
- **`blueprints/`** - Markdown blueprint files for code generation
- **`ai_context/`** - Context files for AI tools
- **`tools/`** - Utility scripts and tools

## Key Concepts

### Recipe Executor

The Recipe Executor is a tool for executing recipes defined in JSON format. It can perform various tasks, including file reading/writing, LLM generation, and sub-recipe execution. The executor uses a context system to manage shared state and data between steps.

### Recipe Tool

The Recipe Tool combines recipe execution with recipe creation capabilities. It can both execute existing JSON recipes and generate new recipes from natural language descriptions.

### Key Features

- **Recipe Format**: JSON-based recipe definitions with steps
- **Context Management**: Manages shared state and data between steps in a recipe
- **Step Types**: Various operations including:
  - **LLM Integration**: Supports various LLMs for generating content and executing tasks
  - **MCP Server Integration**: Connects to MCP servers for executing tasks
  - **File Management**: Reads and writes files as part of the recipe execution process
  - **Flow Control**: Conditional execution and branching based on context variables
  - **Context Manipulation**: Allows for modifying context variables during execution
  - **Parallel & Loop Execution**: Supports parallel execution of steps and looping constructs
  - **Sub-Recipe Execution**: Allows for executing other recipes as part of a larger recipe
- **Logging**: Provides logging for debugging and tracking recipe execution
- **Template Rendering**: Liquid templates for dynamic content generation

## Setup and Installation

### Prerequisites

The workspace requires:

- **`uv`** - for Python dependency management and virtual environments
- **`GitHub CLI`** - for ai-context-files manipulation tool

#### Platform-specific Installation

**Linux:**

```bash
sudo apt update && sudo apt install pipx gh
pipx ensurepath
pipx install uv
```

**macOS:**

```bash
brew install uv gh
```

**Windows:**

```bash
winget install astral-sh.uv -e
winget install GitHub.cli -e
```

#### Azure CLI (Optional)

If you plan on using Azure OpenAI with Managed Identity, install the Azure CLI:

- **Windows**: [Install the Azure CLI on Windows](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
- **Linux**: [Install the Azure CLI on Linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux)
- **macOS**: [Install the Azure CLI on macOS](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos)

Then login:

```bash
az login
```

### Setup Steps

1. **Clone and enter the repository:**

   ```bash
   git clone https://github.com/microsoft/recipe-tool.git
   cd recipe-tool
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY and other optional API keys
   ```

3. **Install workspace dependencies:**

   ```bash
   uv sync --group dev
   ```

4. **Test the installation:**
   ```bash
   uv run recipe-executor --help
   uv run recipe-tool --help
   ```

## Usage

### Command Line Interface

#### Execute a Recipe

```bash
# Using recipe-executor directly
uv run recipe-executor path/to/your/recipe.json

# Using recipe-tool (with additional context capabilities)
uv run recipe-tool --execute path/to/your/recipe.json
```

You can pass context variables:

```bash
uv run recipe-tool --execute path/to/your/recipe.json context_key=value context_key2=value2
```

Example:

```bash
uv run recipe-tool --execute recipes/example_simple/test_recipe.json model=azure/o4-mini
```

#### Create New Recipes from Natural Language

```bash
uv run recipe-tool --create path/to/your/recipe_idea.md
```

You can provide additional context files:

```bash
uv run recipe-tool --create path/to/your/recipe_idea.md \
   files=path/to/other_file.txt,path/to/another_file.txt
```

Example:

```bash
uv run recipe-tool --create recipes/recipe_creator/prompts/sample_recipe_idea.md

# Test the generated recipe
uv run recipe-tool --execute output/analyze_codebase.json \
   input=ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md,ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md
```

## Development

### Helper Scripts

Use the development helper script for common tasks:

```bash
# Setup workspace
./scripts/dev.sh sync

# Run tests
./scripts/dev.sh test              # All tests
./scripts/dev.sh test core         # Core libraries only
./scripts/dev.sh test apps         # Apps only

# Code quality
./scripts/dev.sh lint              # Lint all code
./scripts/dev.sh format            # Format all code
./scripts/dev.sh check             # Full check (lint + types + tests)

# Building
./scripts/dev.sh build             # Build all packages
./scripts/dev.sh build recipe-tool # Build specific package

# Utilities
./scripts/dev.sh clean             # Clean generated files
./scripts/dev.sh run recipe-tool --help  # Run any command
```

### VS Code Development

**Simple approach (recommended):**

```bash
code .  # Open root folder
```

**Multi-root workspace (optional):**

```bash
code recipe-tool-workspace.code-workspace  # Organized sidebar view
```

### Individual Package Development

You can also work on individual packages:

```bash
cd recipe-tool
code .  # Focus on just recipe-tool
uv run pytest  # Run tests for this package only
```

### Building and Distribution

Build individual packages for distribution:

```bash
# Build all packages
./scripts/dev.sh build

# Publish to PyPI (in dependency order)
./scripts/publish.sh --test-pypi  # Test first
./scripts/publish.sh              # Production
```

## Architecture

### Dependency Flow

```
recipe-executor (core execution engine)
    ↓
recipe-tool (execution + creation wrapper)
    ↓
apps/* (user interfaces)
    ↓
mcp-servers/* (protocol servers)
```

### Content Flow

```
Natural Language Ideas → recipe-tool --create → JSON Recipes → recipe-executor
Blueprint Files → codebase-generator recipe → Generated Code
```

## Building from Recipes

One of the interesting aspects of this project is that it can generate its own code using recipes. The workspace includes recipes for:

- Code generation from blueprints
- Documentation generation
- Context file creation for AI tools

## Package Installation

Individual packages can be installed independently:

```bash
# Install just what you need
pip install recipe-executor         # Core execution engine
pip install recipe-tool            # Execution + creation tools
pip install document-generator-app  # Document generation UI
pip install recipe-executor-app     # Recipe execution UI
pip install recipe-tool-app         # Full recipe UI
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

This project is currently **NOT** accepting contributions and suggestions; please see the [dev_guidance.md](docs/dev_guidance.md) for more details.

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
