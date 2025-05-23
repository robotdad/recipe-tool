# Recipe Tool Workspace

A collection of tools for executing natural language recipe-like instructions to create complex workflows. This workspace includes core libraries, user interface applications, and MCP protocol servers for recipe execution and creation.

**NOTE** This project is a very early, experimental project that is being explored in the open. There is no support offered and it will include frequent breaking changes. This project may be abandoned at any time. If you find it useful, it is strongly encouraged to create a fork and remain on a commit that works for your needs unless you are willing to make the necessary changes to use the latest version. This project is currently **NOT** accepting contributions and suggestions; please see the [docs/dev_guidance.md](docs/dev_guidance.md) for more details.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Quick Start

```bash
git clone https://github.com/microsoft/recipe-tool.git
cd recipe-tool
make install    # Install all dependencies and show available commands
```

## Workspace Overview

This workspace is organized into several interconnected projects:

### 🔧 Core Libraries & CLI Tools

- **⚙️ Recipe Executor Core** (`recipe-executor/`) - Core execution engine for JSON recipes
- **🔧 Recipe Tool Core** (`recipe-tool/`) - Recipe execution and creation from natural language

### 🖥️ User Interface Applications

- **🖥️ Document Generator App** (`apps/document-generator/`) - UX for document generation recipes
- **🖥️ Recipe Executor App** (`apps/recipe-executor/`) - UX for recipe execution
- **🖥️ Recipe Tool App** (`apps/recipe-tool/`) - UX for recipe creation and execution

### 🌐 MCP Servers

- **🌐 Python Code Tools MCP** (`mcp-servers/python-code-tools/`) - MCP server for Python development tools
- **🌐 Recipe Tool MCP** (`mcp-servers/recipe-tool/`) - MCP server exposing recipe-tool capabilities

### 📚 Content Collections

- **📄 Recipes** (`recipes/`) - JSON recipe files for execution
- **📐 Blueprints** (`blueprints/`) - Markdown blueprint files for code generation
- **🤖 AI Context** (`ai_context/`) - Context files for AI tools and development
- **📚 Documentation** (`docs/`) - Essential project documentation
- **🛠️ Tools** (`tools/`) - Utility scripts and development tools

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

2. **Configure environment (optional):**

   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY and other optional API keys
   ```

3. **Install workspace dependencies:**

   ```bash
   make install    # Installs all dependencies and shows available commands
   ```

4. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate    # Linux/Mac
   # OR: .venv\Scripts\activate  # Windows
   ```

5. **Test the installation:**
   ```bash
   recipe-executor --help       # Direct script call
   recipe-tool --help          # Direct script call
   document-generator-app      # Launch document generator UI
   recipe-tool-app            # Launch recipe tool UI
   ```

## Usage

### Command Line Interface

#### Execute a Recipe

```bash
# Using recipe-executor directly (fast, minimal features)
recipe-executor path/to/your/recipe.json

# Using recipe-tool (with additional context capabilities)
recipe-tool --execute path/to/your/recipe.json
```

You can pass context variables:

```bash
recipe-tool --execute path/to/your/recipe.json context_key=value context_key2=value2
```

Example:

```bash
recipe-tool --execute recipes/example_simple/test_recipe.json model=azure/o4-mini
```

#### Create New Recipes from Natural Language

```bash
recipe-tool --create path/to/your/recipe_idea.md
```

You can provide additional context files:

```bash
recipe-tool --create path/to/your/recipe_idea.md \
   files=path/to/other_file.txt,path/to/another_file.txt
```

Example:

```bash
recipe-tool --create recipes/recipe_creator/recipe_ideas/sample_recipe_idea.md

# Test the generated recipe
recipe-tool --execute output/analyze_codebase.json \
   input=ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md,ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md
```

### User Interface Applications

Launch interactive web applications:

```bash
document-generator-app    # Document generation with live preview
recipe-executor-app       # Recipe execution with GUI
recipe-tool-app          # Full recipe creation and execution interface
```

#### Recipe Tool App Advanced Usage

The Recipe Tool app supports command-line options and configuration:

```bash
# Command-line options
recipe-tool-app --help              # Show all options
recipe-tool-app --host 127.0.0.1 --port 8000  # Custom host/port
recipe-tool-app --no-mcp            # Disable MCP server
recipe-tool-app --debug             # Enable debug mode
```

**API Integration**: The app exposes Gradio API endpoints (`execute_recipe`, `create_recipe`, `load_example`) for programmatic access via gradio_client.

**MCP Integration**: Functions as an MCP server at `http://host:port/gradio_api/mcp/sse` for AI assistant integration.

**Configuration**: Apps can be configured via environment variables (e.g., `RECIPE_APP_*` variables) or `.env` files. See individual app directories for specific configuration options.

### MCP Servers

Start MCP servers for integration with Claude Desktop or other MCP clients:

```bash
# Recipe tool capabilities
recipe-tool-mcp-server                    # stdio transport (default)
recipe-tool-mcp-server stdio              # stdio transport (explicit)
recipe-tool-mcp-server sse                # SSE transport
recipe-tool-mcp-server sse --port 3002    # SSE with custom port

# Convenience commands
recipe-tool-mcp-server-stdio              # stdio transport
recipe-tool-mcp-server-sse                # SSE transport

# Python code quality tools (Ruff linting/fixing)
python-code-tools stdio                   # stdio transport
python-code-tools sse --port 3001         # SSE transport with custom port

# Convenience commands
python-code-tools-stdio                   # stdio transport
python-code-tools-sse                     # SSE transport
```

**Transport Options**:
- **stdio**: For direct subprocess communication (Claude Desktop, pydantic-ai)
- **SSE**: For HTTP-based communication with custom host/port

#### Python Code Tools MCP

Provides code linting tools for AI assistants:

- **lint_code** - Lint and fix Python code snippets
- **lint_project** - Lint and fix entire Python projects with file patterns

Requirements: Python 3.10+, MCP Python SDK, Ruff

## Development

### Workspace Commands

Available make commands for development:

```bash
make help            # Show all available commands
make install         # Install all dependencies
make workspace-info  # Show project structure and available commands
make doctor          # Check workspace health

# Code quality
make lint            # Run linting across all projects
make format          # Format code across all projects
make test            # Run tests across all projects

# Development utilities
make ai-context-files  # Generate AI context files for development
make activate          # Show virtual environment activation command
```

### Individual Package Development

You can also work on individual packages using the VSCode multi-root workspace:

```bash
# Open the full workspace in VSCode
code recipe-tool-workspace.code-workspace

# Or focus on a single project
cd recipe-tool
code .  # Focus on just recipe-tool
pytest  # Run tests for this package only (after activating venv)
```

### VSCode Integration

The project includes a comprehensive VSCode workspace configuration:
- **Multi-root workspace**: Organized by project type with emojis
- **Python extension**: Pre-configured with proper interpreter paths
- **Testing**: Individual project test discovery and execution
- **Linting**: Ruff integration for code quality
- **Extensions**: Recommended extensions for optimal development experience

## Architecture

### Dependency Flow

```
recipe-executor (core execution engine)
    ↓
recipe-tool (execution + creation wrapper)
    ↓
apps/* (user interfaces)
```

### Content Flow

```
Natural Language Ideas → recipe-tool --create → JSON Recipes → recipe-executor
Blueprint Files → codebase-generator recipe → Generated Code
```

## Building from Recipes

One of the interesting aspects of this project is that it can generate its own code using recipes. The workspace includes recipes for:

- **Code generation from blueprints** - Transform markdown specifications into working code
- **Documentation generation** - Create comprehensive documentation from outlines  
- **Context file creation** - Generate AI context files for development assistance
- **Self-improvement** - The recipe-executor itself is generated by its own recipes

### Key Workflow Integration

The workspace is designed for seamless AI-assisted development:

1. **📐 Write specifications** in `blueprints/` using markdown
2. **🔧 Generate code** using blueprint recipes in `recipes/codebase_generator/`
3. **🤖 Update AI context** with `make ai-context-files` for better assistant support
4. **🖥️ Test interactively** using the UI applications
5. **⚙️ Validate quality** with `make lint`, `make format`, and `make test`

#### Codebase Generator

Generate code from blueprints (the Recipe Executor generates its own code!):

```bash
# Generate all Recipe Executor code
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json

# Generate specific component
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   component_id=steps.llm_generate

# Advanced options
recipe-tool --execute recipes/codebase_generator/codebase_generator_recipe.json \
   edit=true \
   model=openai/gpt-4o \
   output_root=custom_output
```

## Package Installation

Individual packages can be installed independently:

```bash
# Core tools (available via pip when published)
pip install recipe-executor         # Core execution engine
pip install recipe-tool             # Execution + creation tools

# UI Applications  
pip install document-generator-app  # Document generation UI
pip install recipe-executor-app     # Recipe execution UI
pip install recipe-tool-app         # Full recipe UI

# Development setup (recommended)
git clone https://github.com/microsoft/recipe-tool.git
cd recipe-tool
make install                        # Get everything with development tools
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
