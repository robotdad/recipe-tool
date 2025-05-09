# Recipe Tool

A tool for executing recipe-like natural language instructions to create complex workflows. This project includes a recipe executor and a recipe creator, both of which can be used to automate tasks and generate new recipes.

**NOTE** This project is a very early, experimental project that is being explored in the open. There is no support offered and it will include frequent breaking changes. This project may be abandoned at any time. If you find it useful, it is strongly encouraged to create a fork and remain on a commit that works for your needs unless you are willing to make the necessary changes to use the latest version. This project is currently **NOT** accepting contributions and suggestions; please see the [dev_guidance.md](docs/dev_guidance.md) for more details.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Getting Started

```bash
git clone https://github.com/microsoft/recipe-tool.git
cd recipe-tool
```

## Overview

This project is designed to help you automate tasks and generate new recipes using a flexible orchestration system. It consists of two main components: the Recipe Executor and the Recipe Creator.

### Recipe Executor

The Recipe Executor is a tool for executing recipes defined in JSON format. It can perform various tasks, including file reading/writing, LLM generation, and sub-recipe execution. The executor uses a context system to manage shared state and data between steps.

### Recipe Creator

The Recipe Creator is a tool for generating new recipes based on a recipe idea. It uses the Recipe Executor to create JSON recipe files that can be executed later. The creator can also take additional files as input to provide context for the recipe generation.

## Key Components

- **Recipe Executor**: Executes recipes defined in JSON format.
- **Recipe Creator**: Generates new recipes based on a recipe idea.
- **Recipe Format**: JSON-based recipe definitions with steps
- **Context Management**: Manages shared state and data between steps in a recipe.
- **Step Types**: Various operations including file reading/writing, LLM generation, and sub-recipe execution
  - **LLM Integration**: Supports various LLMs for generating content and executing tasks.
  - **File Management**: Reads and writes files as part of the recipe execution process.
  - **Sub-Recipe Execution**: Allows for executing other recipes as part of a larger recipe.
- **Logging**: Provides logging for debugging and tracking recipe execution.
- **Template Rendering**: Liquid templates for dynamic content generation

## Setup and Installation

### Prerequisites

Recommended installers:

- Linux: apt or your distribution's package manager
- macOS: [brew](https://brew.sh/)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

#### Azure CLI for Azure OpenAI using Managed Identity

If you plan on using Azure OpenAI with Managed Identity, you need to install the Azure CLI. Follow the instructions for your platform:

- **Windows**: [Install the Azure CLI on Windows](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
- **Linux**: [Install the Azure CLI on Linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux)
- **macOS**: [Install the Azure CLI on macOS](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos)

Execute the following command to log in:

```bash
az login
```

This command will open a browser window for you to log in. If you are using Managed Identity, ensure that your Azure CLI is configured to use the correct identity.

#### Development tools

The core dependencies you need to install are:

- `make` - for scripting installation steps of the various projects within this repo
- `uv` - for managing installed versions of `python` - for installing python dependencies
- `GitHub cli` - for `ai-context-files` manipulation tool

Linux:

    # make is installed by default on linux
    sudo apt update && sudo apt install pipx && sudo apt install gh
    pipx ensurepath
    pipx install uv

macOS:

    brew install make
    brew install uv
    brew install gh

Windows:

    winget install ezwinports.make -e
    winget install astral-sh.uv  -e
    winget install GitHub.cli -e

### Setup Steps

1. Clone this repository
2. Copy the environment file and configure your API keys:
   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY and other optional API keys
   ```
3. Run the setup command to create a virtual environment and install dependencies:
   ```bash
   make
   ```
4. Activate the virtual environment:
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .\.venv\Scripts\activate
     ```
5. Test the installation by running the example recipe:
   ```bash
   make recipe-executor-create
   ```

## Using the Makefile

The project includes several useful make commands:

- **`make`**: Sets up the virtual environment and installs all dependencies
- **`make ai-context-files`**: Builds AI context files for recipe executor development
- **`make recipe-executor-create`**: Generates recipe executor code from scratch using the recipe itself
- **`make recipe-executor-edit`**: Revises existing recipe executor code using recipes

## Running Recipes via Command Line

Execute a recipe using the command line interface:

```bash
recipe-tool --execute path/to/your/recipe.json
```

You can also pass context variables:

```bash
recipe-tool --execute path/to/your/recipe.json context_key=value context_key2=value2
```

Example:

```bash
recipe-tool --execute recipes/example_simple/test_recipe.json model=azure/o4-mini
```

## Creating New Recipes from a Recipe Idea

Create a new recipe using the command line interface:

```bash
recipe-tool --create path/to/your/recipe_idea.txt
```

This will generate a new recipe file based on the provided idea.
You can also pass additional files for context:

```bash
recipe-tool --create path/to/your/recipe_idea.txt files=path/to/other_file.txt,path/to/another_file.txt
```

Example:

```bash
recipe-tool --create recipes/recipe_creator/prompts/sample_recipe_idea.md

# Test it out
recipe-tool --execute output/analyze_codebase.json input=ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md,ai_context/generated/RECIPE_EXECUTOR_RECIPE_FILES.md
```

## Project Structure

The project contains:

- **`recipe_tool.py`**: The main entry point for the command line interface for both recipe execution and creation
- **`recipe_executor/`**: Core implementation with modules for execution, context management, and steps
- **`recipes/`**: Recipe definition files that can be executed

## Building from Recipes

One of the more interesting aspects of this project is that it can _generate its own code using recipes_:

1. To generate the code from scratch:

   ```bash
   make recipe-executor-create
   ```

2. To edit/revise existing code:
   ```bash
   make recipe-executor-edit
   ```

This demonstrates the power of the Recipe Executor for code generation and maintenance tasks.

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
