# recipe_executor

[collect-files]

**Search:** ['recipe_executor']
**Exclude:** ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc', '*.ruff_cache']
**Include:** ['README.md', 'pyproject.toml', '.env.example']
**Date:** 5/7/2025, 2:40:51 PM
**Files:** 27

=== File: .env.example ===
# Optional for the project
#LOG_LEVEL=DEBUG

# Required for the project
OPENAI_API_KEY=

# Additional APIs
#ANTHROPIC_API_KEY=
#GEMINI_API_KEY=

# Azure OpenAI
#AZURE_OPENAI_BASE_URL=
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_USE_MANAGED_IDENTITY=false
#AZURE_OPENAI_API_KEY=

#(Optional) The client ID of the specific managed identity to use.
#  If not provided, DefaultAzureCredential will be used.
#AZURE_MANAGED_IDENTITY_CLIENT_ID=


=== File: README.md ===
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

Linux:

    # make is installed by default on linux
    sudo apt update && sudo apt install pipx
    pipx ensurepath
    pipx install uv

macOS:

    brew install make
    brew install uv

Windows:

    winget install ezwinports.make -e
    winget install astral-sh.uv  -e

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


=== File: pyproject.toml ===
[project]
name = "recipe-tool"
version = "0.1.0"
description = "A tool for executing natural language recipe-like instructions"
authors = [{ name = "MADE:Explorations Team" }]
license = "MIT"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "azure-identity>=1.21.0",
    "dotenv>=0.9.9",
    "jsonschema>=4.23.0",
    "pydantic-ai-slim[anthropic,openai,mcp]>=0.1.3",
    "pydantic-settings>=2.8.1",
    "python-code-tools>=0.1.0",
    "python-dotenv>=1.1.0",
    "python-liquid>=2.0.1",
    "pyyaml>=6.0.2",
]

[dependency-groups]
dev = [
    "debugpy>=1.8.14",
    "pyright>=1.1.389",
    "pytest>=8.3.5",
    "pytest-cov>=6.1.1",
    "pytest-mock>=3.14.0",
    "ruff>=0.11.2",
]

[project.scripts]
recipe-executor = "recipe_executor.main:main"
recipe-tool = "recipe_tool:main"
python-code-tools = "python_code_tools.cli:main"

[tool.uv]
package = true

[tool.uv.sources]
 python-code-tools = { path = "mcp-servers/python-code-tools", editable = true }
 recipe-tool-mcp-server = { path = "mcp-servers/recipe-tool", editable = true }

[tool.hatch.build.targets.wheel]
packages = ["recipe_executor"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"


=== File: recipe_executor/context.py ===
from typing import Any, Dict, Iterator, Optional
import copy
import json

from recipe_executor.protocols import ContextProtocol

__all__ = ["Context"]


class Context(ContextProtocol):
    """
    Context is a shared state container for the Recipe Executor system.
    It provides a dictionary-like interface for runtime artifacts and
    holds a separate configuration store.
    """

    def __init__(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        # Deep copy initial data to avoid side effects from external modifications
        self._artifacts: Dict[str, Any] = (
            copy.deepcopy(artifacts) if artifacts is not None else {}
        )
        self._config: Dict[str, Any] = (
            copy.deepcopy(config) if config is not None else {}
        )

    def __getitem__(self, key: str) -> Any:
        try:
            return self._artifacts[key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found in Context.")

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        # Let KeyError propagate naturally if key is missing
        del self._artifacts[key]

    def __contains__(self, key: object) -> bool:
        # Only string keys are valid artifact keys
        return isinstance(key, str) and key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Iterate over a snapshot of keys to prevent issues during mutation
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.
        """
        return self.__iter__()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the value for key if present, otherwise return default.
        """
        return self._artifacts.get(key, default)

    def clone(self) -> ContextProtocol:
        """
        Create a deep copy of this Context, including artifacts and config.
        """
        # __init__ will deep-copy the provided dicts
        return Context(artifacts=self._artifacts, config=self._config)

    def dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts as a standard dict.
        """
        return copy.deepcopy(self._artifacts)

    def json(self) -> str:
        """
        Return a JSON string representation of the artifacts.
        """
        return json.dumps(self.dict())

    def get_config(self) -> Dict[str, Any]:
        """
        Return a deep copy of the configuration store.
        """
        return copy.deepcopy(self._config)

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Replace the configuration store with a deep copy of the provided dict.
        """
        self._config = copy.deepcopy(config)


=== File: recipe_executor/executor.py ===
import os
import logging
import inspect
from pathlib import Path
from typing import Union, Dict, Any

from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
from recipe_executor.models import Recipe
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Concrete implementation of ExecutorProtocol. Loads, validates, and executes
    recipes step by step using a shared context. Stateless between runs.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load a recipe (from file path, JSON string, dict, or Recipe model),
        validate it, and execute its steps sequentially using the provided context.
        """
        # Load or use provided Recipe model
        if isinstance(recipe, Recipe):
            self.logger.debug("Using provided Recipe model instance.")
            recipe_model = recipe
        else:
            # Path input
            if isinstance(recipe, Path):
                path_str = str(recipe)
                if not recipe.exists():
                    raise ValueError(f"Recipe file not found: {path_str}")
                self.logger.debug(f"Loading recipe from file path: {path_str}")
                try:
                    content = recipe.read_text(encoding="utf-8")
                except Exception as e:
                    raise ValueError(f"Failed to read recipe file {path_str}: {e}") from e
                try:
                    recipe_model = Recipe.model_validate_json(content)
                except Exception as e:
                    raise ValueError(f"Failed to parse recipe JSON from file {path_str}: {e}") from e
            # String input: file path or JSON
            elif isinstance(recipe, str):
                if os.path.isfile(recipe):
                    self.logger.debug(f"Loading recipe from file path: {recipe}")
                    try:
                        content = Path(recipe).read_text(encoding="utf-8")
                    except Exception as e:
                        raise ValueError(f"Failed to read recipe file {recipe}: {e}") from e
                    try:
                        recipe_model = Recipe.model_validate_json(content)
                    except Exception as e:
                        raise ValueError(f"Failed to parse recipe JSON from file {recipe}: {e}") from e
                else:
                    self.logger.debug("Loading recipe from JSON string.")
                    try:
                        recipe_model = Recipe.model_validate_json(recipe)
                    except Exception as e:
                        raise ValueError(f"Failed to parse recipe JSON string: {e}") from e
            # Dict input
            elif isinstance(recipe, dict):
                self.logger.debug("Loading recipe from dict.")
                try:
                    recipe_model = Recipe.model_validate(recipe)
                except Exception as e:
                    raise ValueError(f"Invalid recipe structure: {e}") from e
            else:
                raise TypeError(f"Unsupported recipe type: {type(recipe)}")

        # Log recipe summary
        try:
            summary = recipe_model.model_dump()
        except Exception:
            summary = {}
        step_count = len(getattr(recipe_model, 'steps', []))
        self.logger.debug(f"Recipe loaded: {summary}. Steps count: {step_count}")

        # Execute each step sequentially
        for idx, step in enumerate(recipe_model.steps):  # type: ignore
            step_type = step.type
            config = step.config or {}
            self.logger.debug(
                f"Executing step {idx} of type '{step_type}' with config: {config}"
            )

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}")

            step_cls = STEP_REGISTRY[step_type]
            step_instance = step_cls(self.logger, config)

            try:
                result = step_instance.execute(context)
                if inspect.isawaitable(result):  # type: ignore
                    await result
            except Exception as e:
                msg = f"Error executing step {idx} ('{step_type}'): {e}"
                raise ValueError(msg) from e

            self.logger.debug(f"Step {idx} ('{step_type}') completed successfully.")

        self.logger.debug("All recipe steps completed successfully.")


=== File: recipe_executor/llm_utils/azure_openai.py ===
import logging
import os
from typing import Optional

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def _mask_secret(secret: Optional[str]) -> str:
    """
    Mask a secret, showing only the first and last character.
    """
    if not secret:
        return "<None>"
    if len(secret) <= 2:
        return "**"
    return f"{secret[0]}***{secret[-1]}"


def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None,
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from environment variables for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o4-mini".
        deployment_name (Optional[str]): Azure deployment name; defaults to model_name or env var.

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance created from AsyncAzureOpenAI client.

    Raises:
        Exception: If required environment variables are missing or client/model creation fails.
    """
    # Load configuration
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("1", "true", "yes")
    azure_endpoint = os.getenv("AZURE_OPENAI_BASE_URL")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    env_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_client_id = os.getenv("AZURE_CLIENT_ID")

    if not azure_endpoint:
        logger.error("Environment variable AZURE_OPENAI_BASE_URL is required")
        raise Exception("Missing AZURE_OPENAI_BASE_URL")

    # Determine deployment
    deployment = deployment_name or env_deployment or model_name

    # Log loaded config
    masked_key = _mask_secret(os.getenv("AZURE_OPENAI_API_KEY"))
    logger.debug(
        f"Azure OpenAI config: endpoint={azure_endpoint}, api_version={azure_api_version}, "
        f"deployment={deployment}, use_managed_identity={use_managed_identity}, "
        f"client_id={azure_client_id or '<None>'}, api_key={masked_key}"
    )

    # Create Azure OpenAI client
    try:
        if use_managed_identity:
            logger.info("Using Azure Managed Identity for authentication")
            if azure_client_id:
                credential = ManagedIdentityCredential(client_id=azure_client_id)
            else:
                credential = DefaultAzureCredential()

            token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "Azure Managed Identity"
        else:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                logger.error("Environment variable AZURE_OPENAI_API_KEY is required for API key authentication")
                raise Exception("Missing AZURE_OPENAI_API_KEY")
            logger.info("Using API key authentication for Azure OpenAI")
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=deployment,
            )
            auth_method = "API Key"
    except Exception as err:
        logger.error(f"Failed to create AsyncAzureOpenAI client: {err}")
        raise

    # Wrap in PydanticAI provider and model
    logger.info(f"Creating Azure OpenAI model '{model_name}' with {auth_method}")
    provider = OpenAIProvider(openai_client=azure_client)
    try:
        model = OpenAIModel(model_name=model_name, provider=provider)
    except Exception as err:
        logger.error(f"Failed to create OpenAIModel: {err}")
        raise

    return model


=== File: recipe_executor/llm_utils/llm.py ===
import os
import time
import logging
from typing import Optional, List, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.mcp import MCPServer

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model


def get_model(model_id: str, logger: logging.Logger) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    Supported providers: openai, azure, anthropic, ollama.
    """
    parts = model_id.split('/')
    if len(parts) < 2:
        raise ValueError(f"Invalid model_id format: '{model_id}'")
    provider = parts[0].lower()

    # OpenAI provider
    if provider == 'openai':
        if len(parts) != 2:
            raise ValueError(f"Invalid OpenAI model_id: '{model_id}'")
        model_name = parts[1]
        return OpenAIModel(model_name)

    # Azure OpenAI provider
    if provider == 'azure':
        if len(parts) == 2:
            model_name = parts[1]
            deployment_name = None
        elif len(parts) == 3:
            model_name = parts[1]
            deployment_name = parts[2]
        else:
            raise ValueError(f"Invalid Azure model_id: '{model_id}'")
        return get_azure_openai_model(
            logger=logger, model_name=model_name, deployment_name=deployment_name
        )

    # Anthropic provider
    if provider == 'anthropic':
        if len(parts) != 2:
            raise ValueError(f"Invalid Anthropic model_id: '{model_id}'")
        model_name = parts[1]
        return AnthropicModel(model_name)

    # Ollama provider (uses OpenAIModel with custom provider URL)
    if provider == 'ollama':
        if len(parts) != 2:
            raise ValueError(f"Invalid Ollama model_id: '{model_id}'")
        model_name = parts[1]
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        provider_obj = OpenAIProvider(base_url=f"{base_url}/v1")
        return OpenAIModel(model_name=model_name, provider=provider_obj)

    raise ValueError(f"Unsupported LLM provider: '{provider}' in model_id '{model_id}'")


class LLM:
    """
    Unified interface for interacting with various LLM providers
    and optional MCP servers.
    """
    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        max_tokens: Optional[int] = None,
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        self.logger: logging.Logger = logger
        self.default_model_id: str = model
        self.default_max_tokens: Optional[int] = max_tokens
        self.default_mcp_servers: List[MCPServer] = mcp_servers or []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        model_id = model or self.default_model_id
        tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        servers = mcp_servers if mcp_servers is not None else self.default_mcp_servers

        # Info log: model selection
        try:
            provider = model_id.split('/', 1)[0]
        except Exception:
            provider = 'unknown'
        self.logger.info(
            "LLM generate using provider=%s model_id=%s", provider, model_id
        )

        # Debug log: request details
        output_name = getattr(output_type, '__name__', str(output_type))
        self.logger.debug(
            "LLM request payload prompt=%r model_id=%s max_tokens=%s output_type=%s",
            prompt, model_id, tokens, output_name
        )

        # Initialize model
        try:
            model_instance = get_model(model_id, self.logger)
        except ValueError as e:
            self.logger.error("Invalid model_id '%s': %s", model_id, str(e))
            raise

        # Prepare agent
        agent_kwargs = {
            'model': model_instance,
            'output_type': output_type,
            'mcp_servers': servers,
        }
        if tokens is not None:
            agent_kwargs['model_settings'] = ModelSettings(max_tokens=tokens)

        agent: Agent = Agent(**agent_kwargs)  # type: ignore

        # Execute request
        start_time = time.time()
        try:
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
        except Exception as e:
            self.logger.error(
                "LLM call failed for model_id=%s error=%s", model_id, str(e)
            )
            raise
        end_time = time.time()

        # Log result summary
        usage = None
        try:
            usage = result.usage()
        except Exception:
            usage = None
        duration = end_time - start_time
        if usage:
            self.logger.info(
                "LLM result time=%.3f sec requests=%d tokens_total=%d (req=%d res=%d)",
                duration,
                usage.requests,
                usage.total_tokens,
                usage.request_tokens,
                usage.response_tokens,
            )
        else:
            self.logger.info(
                "LLM result time=%.3f sec (usage unavailable)", duration
            )

        # Debug log: raw result
        self.logger.debug("LLM raw result: %r", result)

        return result.output


=== File: recipe_executor/llm_utils/mcp.py ===
import os
import logging
from typing import Any, Dict, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

# Attempt to import load_dotenv for .env support; optional
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

__all__ = ["get_mcp_server"]


def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any]
) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.

    Raises:
        ValueError: If the configuration is invalid.
        RuntimeError: On underlying errors when creating the server instance.
    """
    # Validate config type
    if not isinstance(config, dict):
        raise ValueError("MCP server configuration must be a dict")

    # Mask sensitive values for debug logging
    masked: Dict[str, Any] = {}
    for key, value in config.items():
        if key in ("headers", "env") and isinstance(value, dict):
            masked[key] = {k: "***" for k in value.keys()}
        else:
            masked[key] = value
    logger.debug("MCP server configuration: %s", masked)

    # HTTP transport
    if 'url' in config:
        url = config.get('url')
        if not isinstance(url, str) or not url:
            raise ValueError("HTTP MCP server requires a non-empty 'url' string")
        headers = config.get('headers')
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("HTTP MCP server 'headers' must be a dict if provided")

        logger.info("Creating HTTP MCP server for URL: %s", url)
        try:
            # Only pass headers if provided
            server = MCPServerHTTP(url=url, headers=headers) if headers is not None else MCPServerHTTP(url=url)
        except Exception as exc:
            raise RuntimeError(f"Failed to create HTTP MCP server: {exc}") from exc
        return server

    # Stdio transport
    if 'command' in config:
        command = config.get('command')
        if not isinstance(command, str) or not command:
            raise ValueError("Stdio MCP server requires a non-empty 'command' string")

        args = config.get('args')
        if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            raise ValueError("Stdio MCP server 'args' must be a list of strings")

        env_cfg = config.get('env')
        env: Optional[Dict[str, str]] = None
        if env_cfg is not None:
            if not isinstance(env_cfg, dict):
                raise ValueError("Stdio MCP server 'env' must be a dict if provided")
            # Load .env if any value is empty and dotenv is available
            if load_dotenv and any(v == "" for v in env_cfg.values()):  # type: ignore
                load_dotenv()  # type: ignore
            env = {}
            for k, v in env_cfg.items():
                if not isinstance(v, str):
                    raise ValueError(f"Environment variable '{k}' must be a string")
                if v == "":
                    # attempt to get from system environment
                    sys_val = os.getenv(k)
                    if sys_val is not None:
                        env[k] = sys_val
                else:
                    env[k] = v

        working_dir = config.get('working_dir')
        if working_dir is not None and not isinstance(working_dir, str):
            raise ValueError("Stdio MCP server 'working_dir' must be a string if provided")

        logger.info("Creating stdio MCP server with command: %s %s", command, args)
        try:
            server = MCPServerStdio(
                command=command,
                args=args,
                cwd=working_dir,
                env=env
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to create stdio MCP server: {exc}") from exc
        return server

    # Neither HTTP nor Stdio specified
    raise ValueError("Invalid MCP server configuration: must contain 'url' for HTTP or 'command' for stdio transport")


=== File: recipe_executor/logger.py ===
import os
import sys
import logging
from typing import Any

def init_logger(
    log_dir: str = "logs", stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR" (case-insensitive).

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Get root logger and set lowest level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Create log directory
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as exc:
        raise Exception(f"Failed to create log directory '{log_dir}': {exc}")

    # Define formatter for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set up file handlers: debug.log, info.log, error.log
    level_map = [
        ("debug", logging.DEBUG),
        ("info", logging.INFO),
        ("error", logging.ERROR),
    ]
    for name, level in level_map:
        path = os.path.join(log_dir, f"{name}.log")
        try:
            file_handler = logging.FileHandler(path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as exc:
            raise Exception(f"Failed to set up {name} log file '{path}': {exc}")

    # Configure console (stdout) handler
    level_name = stdio_log_level.upper()
    if level_name == "WARN":
        level_name = "WARNING"
    if level_name not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        level_name = "INFO"
    console_level: Any = getattr(logging, level_name, logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Initialization logs
    logger.debug("Logger initialized: log_dir='%s', stdio_log_level='%s'", log_dir, level_name)
    logger.info("Logger initialized successfully")

    return logger


=== File: recipe_executor/main.py ===
import argparse
import asyncio
import logging
import os
import sys
import time
import traceback
from typing import Dict, List

from dotenv import load_dotenv

from .context import Context
from .executor import Executor
from .logger import init_logger


def parse_key_value_pairs(pairs: List[str]) -> Dict[str, str]:
    """
    Parse a list of strings in the form key=value into a dictionary.
    Raises ValueError on malformed entries.
    """
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid key=value format '{pair}'")
        key, value = pair.split("=", 1)
        if not key:
            raise ValueError(f"Invalid key in pair '{pair}'")
        result[key] = value
    return result


async def main_async() -> None:
    # Load environment variables from .env
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Recipe Executor CLI")
    parser.add_argument(
        "recipe_path",
        type=str,
        help="Path to the recipe file to execute"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log files"
    )
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Context artifact values as key=value pairs"
    )
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        help="Static configuration values as key=value pairs"
    )
    args = parser.parse_args()

    # Ensure log directory exists
    try:
        os.makedirs(args.log_dir, exist_ok=True)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: cannot create log directory '{args.log_dir}': {e}\n")
        raise SystemExit(1)

    # Initialize logging
    try:
        logger: logging.Logger = init_logger(args.log_dir)
    except Exception as e:
        sys.stderr.write(f"Logger Initialization Error: {e}\n")
        raise SystemExit(1)

    logger.debug("Starting Recipe Executor Tool")
    logger.debug("Parsed arguments: %s", args)

    # Parse context and config key=value pairs
    try:
        artifacts = parse_key_value_pairs(args.context)
        config = parse_key_value_pairs(args.config)
    except ValueError as ve:
        # Invalid context/config formatting
        raise ve

    logger.debug("Initial context artifacts: %s", artifacts)

    # Create execution context
    context = Context(artifacts=artifacts, config=config)

    # Create and run executor
    executor = Executor(logger)
    logger.info("Executing recipe: %s", args.recipe_path)

    start_time = time.time()
    try:
        await executor.execute(args.recipe_path, context)
    except Exception as exec_err:
        logger.error(
            "An error occurred during recipe execution: %s", exec_err,
            exc_info=True
        )
        raise
    duration = time.time() - start_time

    logger.info(
        "Recipe execution completed successfully in %.2f seconds",
        duration
    )


def main() -> None:
    try:
        asyncio.run(main_async())
    except ValueError as ve:
        sys.stderr.write(f"Context Error: {ve}\n")
        sys.exit(1)
    except SystemExit as se:
        # Preserve explicit exit codes
        sys.exit(se.code)
    except Exception:
        # Unexpected errors: print traceback
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()


=== File: recipe_executor/models.py ===
"""
Models for Recipe Executor system.

Defines Pydantic models for file specifications and recipe structures.
"""
from typing import Any, Dict, List, Union

from pydantic import BaseModel


class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file, which can be a string,
                 a mapping, or a list of mappings for structured outputs.
    """
    path: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """
    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps: A list of steps defining the recipe.
    """
    steps: List[RecipeStep]

=== File: recipe_executor/protocols.py ===
"""
Protocols definitions for the Recipe Executor system.

This module provides structural interfaces (Protocols) for core components:
- ContextProtocol
- StepProtocol
- ExecutorProtocol

These serve as the single source of truth for component contracts, enabling loose coupling
and clear type annotations without introducing direct dependencies on concrete implementations.
"""
from typing import Protocol, runtime_checkable, Any, Dict, Iterator, Union
from pathlib import Path
from logging import Logger

from recipe_executor.models import Recipe


@runtime_checkable
class ContextProtocol(Protocol):
    """
    Defines a dict-like context for sharing data across steps and executors.

    Methods mirror built-in dict behaviors plus cloning and serialization.
    """

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: str) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def get(self, key: str, default: Any = None) -> Any:
        ...

    def clone(self) -> "ContextProtocol":
        ...

    def dict(self) -> Dict[str, Any]:
        ...

    def json(self) -> str:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def get_config(self) -> Dict[str, Any]:
        ...

    def set_config(self, config: Dict[str, Any]) -> None:
        ...


@runtime_checkable
class StepProtocol(Protocol):
    """
    Defines the interface for a recipe step implementation.

    Each step is initialized with a logger and configuration, and
    exposes an asynchronous execute method.
    """

    def __init__(self, logger: Logger, config: Dict[str, Any]) -> None:
        ...

    async def execute(self, context: ContextProtocol) -> None:
        ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    """
    Defines the interface for an executor implementation.

    The executor runs a recipe given its definition and a context.
    """

    def __init__(self, logger: Logger) -> None:
        ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None:
        ...


=== File: recipe_executor/steps/__init__.py ===
"""
Package for recipe execution steps.

This module imports all standard step implementations and registers them
in the global STEP_REGISTRY for dynamic lookup by the executor.
"""
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.conditional import ConditionalStep
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import MCPStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.set_context import SetContextStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register standard steps by updating the registry
STEP_REGISTRY.update({
    "conditional": ConditionalStep,
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "set_context": SetContextStep,
    "write_files": WriteFilesStep,
})

__all__ = [
    "STEP_REGISTRY",
    "ConditionalStep",
    "ExecuteRecipeStep",
    "LLMGenerateStep",
    "LoopStep",
    "MCPStep",
    "ParallelStep",
    "ReadFilesStep",
    "SetContextStep",
    "WriteFilesStep",
]


=== File: recipe_executor/steps/base.py ===
"""
Base step component for the Recipe Executor.
Defines a generic BaseStep class and the base Pydantic StepConfig.
"""

from __future__ import annotations

import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for steps.
    Extend this class to add step-specific fields.
    """

    # No common fields; each step should subclass and define its own
    pass


StepConfigType = TypeVar("StepConfigType", bound=StepConfig)


class BaseStep(Generic[StepConfigType]):
    """
    Base class for all steps in the recipe executor.

    Each step must implement the async execute method.
    Subclasses should call super().__init__ in their constructor,
    passing a logger and an instance of a StepConfig subclass.
    """

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        """
        Initialize a step with a logger and validated configuration.

        Args:
            logger: Logger instance for the step.
            config: Pydantic-validated configuration for the step.
        """
        self.logger: logging.Logger = logger
        self.config: StepConfigType = config
        # Log initialization with debug-level detail
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config!r}")

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute the step logic. Must be overridden by subclasses.

        Args:
            context: Execution context adhering to ContextProtocol.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement the execute method")


=== File: recipe_executor/steps/conditional.py ===
import logging
import os
import re
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.utils.templates import render_template


class ConditionalConfig(StepConfig):
    """
    Configuration for ConditionalStep.

    Fields:
        condition: Expression or boolean to evaluate against the context.
        if_true: Optional branch configuration when condition is true.
        if_false: Optional branch configuration when condition is false.
    """
    condition: Any
    if_true: Optional[Dict[str, Any]] = None
    if_false: Optional[Dict[str, Any]] = None


# Utility functions for condition evaluation

def file_exists(path: Any) -> bool:
    """Check if a given path exists on the filesystem."""
    try:
        return isinstance(path, str) and os.path.exists(path)
    except Exception:
        return False


def all_files_exist(paths: Any) -> bool:
    """Check if all paths in a list or tuple exist."""
    try:
        if not isinstance(paths, (list, tuple)):
            return False
        return all(isinstance(p, str) and os.path.exists(p) for p in paths)
    except Exception:
        return False


def file_is_newer(src: Any, dst: Any) -> bool:
    """Check if src file is newer than dst file."""
    try:
        if not (isinstance(src, str) and isinstance(dst, str)):
            return False
        if not (os.path.exists(src) and os.path.exists(dst)):
            return False
        return os.path.getmtime(src) > os.path.getmtime(dst)
    except Exception:
        return False


def and_(*args: Any) -> bool:
    """Logical AND over all arguments."""
    return all(bool(a) for a in args)


def or_(*args: Any) -> bool:
    """Logical OR over all arguments."""
    return any(bool(a) for a in args)


def not_(val: Any) -> bool:
    """Logical NOT of the value."""
    return not bool(val)


def evaluate_condition(
    expr: Any, context: ContextProtocol, logger: logging.Logger
) -> bool:
    """
    Render and evaluate a condition expression against the context.
    Supports boolean literals, file checks, comparisons, and logical operations.
    Raises ValueError on render or evaluation errors.
    """
    # Direct boolean
    if isinstance(expr, bool):
        logger.debug("Using boolean condition: %s", expr)
        return expr

    # Ensure expression is a string for rendering
    expr_str = expr if isinstance(expr, str) else str(expr)
    try:
        rendered = render_template(expr_str, context)
    except Exception as err:
        raise ValueError(f"Error rendering condition '{expr_str}': {err}")

    logger.debug("Rendered condition '%s': '%s'", expr_str, rendered)
    text = rendered.strip()
    lowered = text.lower()

    # Boolean literal handling
    if lowered in ("true", "false"):
        result = (lowered == "true")
        logger.debug("Interpreted boolean literal '%s' as %s", text, result)
        return result

    # Replace function-like logical keywords to avoid Python keyword conflicts
    transformed = re.sub(r"\band\(", "and_(", text)
    transformed = re.sub(r"\bor\(", "or_(", transformed)
    transformed = re.sub(r"\bnot\(", "not_(", transformed)
    logger.debug("Transformed expression for eval: '%s'", transformed)

    # Safe globals for eval
    safe_globals: Dict[str, Any] = {
        "__builtins__": {},
        # File utilities
        "file_exists": file_exists,
        "all_files_exist": all_files_exist,
        "file_is_newer": file_is_newer,
        # Logical helpers
        "and_": and_,
        "or_": or_,
        "not_": not_,
        # Boolean literals
        "true": True,
        "false": False,
    }

    try:
        result = eval(transformed, safe_globals, {})  # nosec
    except Exception as err:
        raise ValueError(f"Invalid condition expression '{transformed}': {err}")

    outcome = bool(result)
    logger.debug("Condition '%s' evaluated to %s", transformed, outcome)
    return outcome


class ConditionalStep(BaseStep[ConditionalConfig]):
    """
    Step that branches execution based on a boolean condition.
    """

    def __init__(
        self, logger: logging.Logger, config: Dict[str, Any]
    ) -> None:
        config_model = ConditionalConfig.model_validate(config)
        super().__init__(logger, config_model)

    async def execute(self, context: ContextProtocol) -> None:
        expr = self.config.condition
        self.logger.debug("Evaluating conditional expression: '%s'", expr)
        try:
            result = evaluate_condition(expr, context, self.logger)
        except ValueError as err:
            raise RuntimeError(f"Condition evaluation error: {err}")

        branch = self.config.if_true if result else self.config.if_false
        branch_name = "if_true" if result else "if_false"
        self.logger.debug(
            "Condition '%s' is %s, executing '%s' branch",
            expr,
            result,
            branch_name,
        )

        if isinstance(branch, dict) and branch.get("steps"):
            await self._execute_branch(branch, context)
        else:
            self.logger.debug("No branch to execute for this condition result")

    async def _execute_branch(
        self, branch: Dict[str, Any], context: ContextProtocol
    ) -> None:
        steps: List[Any] = branch.get("steps") or []
        if not isinstance(steps, list):
            self.logger.debug("Branch 'steps' is not a list, skipping execution")
            return

        for step_def in steps:
            if not isinstance(step_def, dict):
                continue

            step_type = step_def.get("type")
            step_conf = step_def.get("config") or {}
            if not step_type:
                self.logger.debug("Step definition missing 'type', skipping")
                continue

            step_cls = STEP_REGISTRY.get(step_type)
            if step_cls is None:
                raise RuntimeError(
                    f"Unknown step type in conditional branch: {step_type}"
                )

            self.logger.debug(
                "Executing step '%s' in conditional branch", step_type
            )
            step_instance = step_cls(self.logger, step_conf)
            await step_instance.execute(context)


=== File: recipe_executor/steps/execute_recipe-tmp.py ===
import os
import ast
import logging
from typing import Any, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template

__all__ = ["ExecuteRecipeConfig", "ExecuteRecipeStep"]

def _render_override(value: Any, context: ContextProtocol) -> Any:
    """
    Recursively render and parse override values.

    - Strings are template-rendered, then if the result is a valid Python literal
      (dict or list), parsed via ast.literal_eval into Python objects and
      processed recursively.
    - Lists and dicts are processed recursively.
    - Other types are returned as-is.
    """
    if isinstance(value, str):
        rendered = render_template(value, context)
        try:
            parsed = ast.literal_eval(rendered)
        except (ValueError, SyntaxError):
            return rendered
        else:
            if isinstance(parsed, (dict, list)):
                return _render_override(parsed, context)
            return rendered
    if isinstance(value, list):  # type: ignore[type-arg]
        return [_render_override(item, context) for item in value]
    if isinstance(value, dict):  # type: ignore[type-arg]
        return {key: _render_override(val, context) for key, val in value.items()}
    return value


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the sub-recipe to execute (templateable).
        context_overrides: Optional values to override in the context.
    """
    recipe_path: str
    context_overrides: Dict[str, Any] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    """Step to execute a sub-recipe with shared context and optional overrides."""

    def __init__(
        self,
        logger: logging.Logger,
        config: Dict[str, Any]
    ) -> None:
        validated: ExecuteRecipeConfig = ExecuteRecipeConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        # Render and validate the sub-recipe path
        rendered_path = render_template(self.config.recipe_path, context)
        if not os.path.isfile(rendered_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_path}")

        # Apply context overrides before executing the sub-recipe
        for key, override_value in self.config.context_overrides.items():
            rendered_value = _render_override(override_value, context)
            context[key] = rendered_value

        try:
            # Import here to avoid circular dependencies
            from recipe_executor.executor import Executor

            self.logger.info(f"Starting sub-recipe execution: {rendered_path}")
            executor = Executor(self.logger)
            await executor.execute(rendered_path, context)
            self.logger.info(f"Completed sub-recipe execution: {rendered_path}")
        except Exception as exc:
            self.logger.error(f"Error executing sub-recipe '{rendered_path}': {exc}")
            raise RuntimeError(f"Failed to execute sub-recipe '{rendered_path}': {exc}") from exc


=== File: recipe_executor/steps/execute_recipe.py ===
import os
import json
from typing import Any, Dict

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template

__all__ = ["ExecuteRecipeConfig", "ExecuteRecipeStep"]


def _render_override(value: Any, context: ContextProtocol) -> Any:
    """
    Recursively render and parse override values.

    - Strings are template-rendered, then if the result is valid JSON (dict or list), parsed into Python objects.
    - Lists and dicts are processed recursively.
    - Other types are returned as-is.
    """
    if isinstance(value, str):
        rendered = render_template(value, context)
        # Attempt to parse JSON if it represents an object or array
        try:
            parsed = json.loads(rendered)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass
        return rendered
    if isinstance(value, list):  # type: ignore[type-arg]
        return [_render_override(item, context) for item in value]
    if isinstance(value, dict):  # type: ignore[type-arg]
        return {key: _render_override(val, context) for key, val in value.items()}
    return value


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the sub-recipe to execute (templateable).
        context_overrides: Optional values to override in the context.
    """
    recipe_path: str
    context_overrides: Dict[str, Any] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    """Step to execute a sub-recipe with shared context and optional overrides."""

    def __init__(
        self,
        logger,  # type: ignore[valid-type]
        config: Dict[str, Any]
    ) -> None:
        validated: ExecuteRecipeConfig = ExecuteRecipeConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        """
        Execute a sub-recipe located at the rendered recipe_path.

        Applies context_overrides before execution, shares the same context,
        and logs progress.
        """
        # Render and validate recipe path
        rendered_path = render_template(self.config.recipe_path, context)
        if not os.path.isfile(rendered_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {rendered_path}")

        # Apply context overrides with templating and JSON parsing
        for key, override_value in self.config.context_overrides.items():
            rendered_value = _render_override(override_value, context)
            context[key] = rendered_value

        try:
            # Import here to avoid circular dependencies
            from recipe_executor.executor import Executor

            self.logger.info(f"Starting sub-recipe execution: {rendered_path}")
            executor = Executor(self.logger)
            await executor.execute(rendered_path, context)
            self.logger.info(f"Completed sub-recipe execution: {rendered_path}")
        except Exception as exc:
            # Log and propagate with context
            self.logger.error(f"Error executing sub-recipe '{rendered_path}': {exc}")
            raise RuntimeError(
                f"Failed to execute sub-recipe '{rendered_path}': {exc}"
            ) from exc


=== File: recipe_executor/steps/llm_generate.py ===
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.models import json_object_to_pydantic_model
from recipe_executor.utils.templates import render_template


class LLMGenerateConfig(StepConfig):
    """
    Config for LLMGenerateStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        max_tokens: The maximum number of tokens for the LLM response.
        mcp_servers: List of MCP server configurations for access to tools.
        output_format: The format of the LLM output (text, files, or JSON/list schemas).
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    max_tokens: Optional[Union[str, int]] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any], List[Any]]
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


def _render_config(config: Dict[str, Any], context: ContextProtocol) -> Dict[str, Any]:
    """
    Recursively render templated strings in a dict.
    """
    result: Dict[str, Any] = {}
    for key, value in config.items():
        if isinstance(value, str):
            result[key] = render_template(value, context)
        elif isinstance(value, dict):
            result[key] = _render_config(value, context)
        elif isinstance(value, list):
            items: List[Any] = []
            for item in value:
                if isinstance(item, dict):
                    items.append(_render_config(item, context))
                else:
                    items.append(item)
            result[key] = items
        else:
            result[key] = value
    return result


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    """
    Step to generate content via a large language model (LLM).
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render templates for core inputs
        prompt: str = render_template(self.config.prompt, context)
        model_id: str = render_template(self.config.model, context)
        output_key: str = render_template(self.config.output_key, context)

        # Prepare max_tokens
        raw_max = self.config.max_tokens
        max_tokens: Optional[int] = None
        if raw_max is not None:
            max_str = render_template(str(raw_max), context)
            try:
                max_tokens = int(max_str)
            except ValueError:
                raise ValueError(f"Invalid max_tokens value: {raw_max!r}")

        # Collect MCP server configurations
        mcp_cfgs: List[Dict[str, Any]] = []
        if self.config.mcp_servers:
            mcp_cfgs.extend(self.config.mcp_servers)
        ctx_mcp = context.get_config().get("mcp_servers") or []
        if isinstance(ctx_mcp, list):
            mcp_cfgs.extend(ctx_mcp)

        mcp_servers: List[Any] = []
        for cfg in mcp_cfgs:
            rendered = _render_config(cfg, context)
            server = get_mcp_server(logger=self.logger, config=rendered)
            mcp_servers.append(server)

        # Initialize LLM client
        llm = LLM(
            logger=self.logger,
            model=model_id,
            mcp_servers=mcp_servers or None,
        )
        output_format = self.config.output_format
        result: Any = None

        try:
            self.logger.debug(
                "Calling LLM: model=%s, format=%r, max_tokens=%s, mcp_servers=%r",
                model_id,
                output_format,
                max_tokens,
                mcp_servers,
            )
            # Text output
            if output_format == "text":  # type: ignore
                kwargs: Dict[str, Any] = {"output_type": str}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                context[output_key] = result

            # Files output
            elif output_format == "files":  # type: ignore
                kwargs = {"output_type": FileSpecCollection}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                # Store only the list of FileSpec
                context[output_key] = result.files

            # JSON object schema
            elif isinstance(output_format, dict):
                schema_model = json_object_to_pydantic_model(output_format, model_name="LLMObject")
                kwargs = {"output_type": schema_model}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                context[output_key] = result.model_dump()

            # List schema
            elif isinstance(output_format, list):  # type: ignore
                if len(output_format) != 1 or not isinstance(output_format[0], dict):
                    raise ValueError(
                        "When output_format is a list, it must be a single-item list containing a schema object."
                    )
                item_schema = output_format[0]
                wrapper_schema: Dict[str, Any] = {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": item_schema}},
                    "required": ["items"],
                }
                schema_model = json_object_to_pydantic_model(wrapper_schema, model_name="LLMListWrapper")
                kwargs = {"output_type": schema_model}
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                result = await llm.generate(prompt, **kwargs)
                wrapper = result.model_dump()
                context[output_key] = wrapper.get("items", [])

            else:
                raise ValueError(f"Unsupported output_format: {output_format!r}")

        except Exception as exc:
            self.logger.error("LLM generate failed: %r", exc, exc_info=True)
            raise


=== File: recipe_executor/steps/loop.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template

__all__ = ["LoopStep", "LoopStepConfig"]


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.
    """
    items: Union[str, List[Any], Dict[Any, Any]]
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    """
    LoopStep: iterate over a collection, execute substeps for each item.
    """
    def __init__(
        self, logger: logging.Logger, config: Dict[str, Any]
    ) -> None:
        # Validate configuration via Pydantic
        validated = LoopStepConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        # dynamic import to avoid circular dependencies
        from recipe_executor.executor import Executor  # type: ignore

        # Resolve items definition (could be path or direct list/dict)
        items_def: Union[str, List[Any], Dict[Any, Any]] = self.config.items
        if isinstance(items_def, str):
            # Render template to get path
            rendered_path: str = render_template(items_def, context)
            items_obj: Any = _resolve_path(rendered_path, context)
        else:
            # Direct list or dict provided
            items_obj = items_def  # type: ignore

        # Validate items_obj
        if items_obj is None:
            raise ValueError(
                f"LoopStep: Items collection '{items_def}' not found in context."
            )
        if not isinstance(items_obj, (list, dict)):
            raise ValueError(
                f"LoopStep: Items collection must be a list or dict, got {type(items_obj).__name__}."
            )

        # Build list of (key/index, value)
        items_list: List[Tuple[Any, Any]] = []
        if isinstance(items_obj, list):
            for idx, value in enumerate(items_obj):
                items_list.append((idx, value))
        else:
            for key, value in items_obj.items():
                items_list.append((key, value))
        total_items: int = len(items_list)

        self.logger.info(
            f"LoopStep: Processing {total_items} items with max_concurrency={self.config.max_concurrency}."
        )

        # Handle empty collection
        if total_items == 0:
            # Preserve type (list or dict)
            empty_result: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
            context[self.config.result_key] = empty_result
            self.logger.info("LoopStep: No items to process.")
            return

        # Prepare result and error containers
        results: Union[List[Any], Dict[Any, Any]] = [] if isinstance(items_obj, list) else {}
        errors: Union[List[Dict[str, Any]], Dict[Any, Dict[str, Any]]] = (
            [] if isinstance(items_obj, list) else {}
        )

        # Concurrency control
        semaphore: Optional[asyncio.Semaphore] = None
        max_c = self.config.max_concurrency
        if max_c and max_c > 0:
            semaphore = asyncio.Semaphore(max_c)

        # Executor for substeps
        step_executor: ExecutorProtocol = Executor(self.logger)
        substeps_recipe: Dict[str, Any] = {"steps": self.config.substeps}

        fail_fast_triggered: bool = False
        tasks: List[asyncio.Task] = []
        completed_count: int = 0

        async def process_single_item(
            key: Any, value: Any
        ) -> Tuple[Any, Any, Optional[str]]:
            # Clone context for isolation
            item_ctx: ContextProtocol = context.clone()
            item_ctx[self.config.item_key] = value
            # Attach iteration metadata
            if isinstance(items_obj, list):
                item_ctx["__index"] = key
            else:
                item_ctx["__key"] = key
            try:
                self.logger.debug(f"LoopStep: Starting item {key}.")
                await step_executor.execute(substeps_recipe, item_ctx)
                # Retrieve processed item result
                result = item_ctx.get(self.config.item_key, value)
                self.logger.debug(f"LoopStep: Finished item {key}.")
                return key, result, None
            except Exception as exc:
                self.logger.error(f"LoopStep: Error processing item {key}: {exc}")
                return key, None, str(exc)

        async def run_sequential() -> None:
            nonlocal fail_fast_triggered, completed_count
            for key, value in items_list:
                if fail_fast_triggered:
                    break
                idx, res, err = await process_single_item(key, value)
                if err:
                    # Record error
                    if isinstance(errors, list):
                        errors.append({"index": idx, "error": err})
                    else:
                        errors[idx] = {"error": err}
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break
                else:
                    # Record success
                    if isinstance(results, list):
                        results.append(res)
                    else:
                        results[idx] = res
                completed_count += 1

        async def run_parallel() -> None:
            nonlocal fail_fast_triggered, completed_count

            async def worker(k: Any, v: Any) -> Tuple[Any, Any, Optional[str]]:
                if semaphore:
                    async with semaphore:
                        return await process_single_item(k, v)
                return await process_single_item(k, v)

            # Launch tasks with optional delay
            for idx, (k, v) in enumerate(items_list):  # type: ignore
                if fail_fast_triggered:
                    break
                task = asyncio.create_task(worker(k, v))
                tasks.append(task)
                if self.config.delay and idx < total_items - 1:
                    await asyncio.sleep(self.config.delay)

            # Collect task results as they complete
            for fut in asyncio.as_completed(tasks):
                if fail_fast_triggered:
                    break
                try:
                    k, res, err = await fut
                    if err:
                        if isinstance(errors, list):
                            errors.append({"index": k, "error": err})
                        else:
                            errors[k] = {"error": err}
                        if self.config.fail_fast:
                            fail_fast_triggered = True
                            continue
                    else:
                        if isinstance(results, list):
                            results.append(res)
                        else:
                            results[k] = res
                    completed_count += 1
                except Exception as exc:
                    self.logger.error(f"LoopStep: Unexpected exception: {exc}")
                    if self.config.fail_fast:
                        fail_fast_triggered = True
                        break

        # Execute in chosen mode
        if self.config.max_concurrency and self.config.max_concurrency > 1:
            await run_parallel()
        else:
            await run_sequential()

        # Store results and errors in parent context
        context[self.config.result_key] = results
        has_errors = bool(errors) if isinstance(errors, list) else bool(errors)
        if has_errors:
            context[f"{self.config.result_key}__errors"] = errors

        self.logger.info(
            f"LoopStep: Processed {completed_count} items. Errors: "
            f"{len(errors) if has_errors else 0}."
        )


def _resolve_path(path: str, context: ContextProtocol) -> Any:
    """
    Resolve a dot-notated path against the context or nested dicts.
    """
    current: Any = context
    for part in path.split('.'):
        if isinstance(current, ContextProtocol):
            current = current.get(part, None)
        elif isinstance(current, dict):
            current = current.get(part, None)
        else:
            return None
        if current is None:
            return None
    return current


=== File: recipe_executor/steps/mcp.py ===
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


=== File: recipe_executor/steps/parallel.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional, Set

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.protocols import ContextProtocol, StepProtocol


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each a dict with 'type' and 'config'.
        max_concurrency: Maximum number of substeps to run concurrently. 0 means unlimited.
        delay: Optional delay (in seconds) between launching each substep.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """Step to execute multiple sub-steps in parallel."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        substeps: List[Dict[str, Any]] = self.config.substeps or []
        total: int = len(substeps)
        max_conc: int = self.config.max_concurrency
        delay: float = self.config.delay

        self.logger.info(
            f"Starting ParallelStep: {total} substeps, "
            f"max_concurrency={max_conc}, delay={delay}"
        )

        if total == 0:
            self.logger.info("ParallelStep has no substeps to execute. Skipping.")
            return

        # Determine concurrency limit
        concurrency: int = max_conc if max_conc > 0 else total
        semaphore: asyncio.Semaphore = asyncio.Semaphore(concurrency)

        # Holder for first failure
        failure: Dict[str, Optional[Any]] = {"exc": None, "idx": None}
        tasks: List[asyncio.Task] = []

        async def run_substep(idx: int, spec: Dict[str, Any]) -> None:
            sub_logger = self.logger.getChild(f"substep_{idx}")
            try:
                sub_logger.debug(
                    f"Cloning context and preparing substep {idx} ({spec.get('type')})"
                )
                sub_context = context.clone()

                step_type = spec.get("type")
                step_cfg = spec.get("config", {})
                if not step_type or step_type not in STEP_REGISTRY:
                    raise RuntimeError(
                        f"Unknown or missing step type '{step_type}' for substep {idx}"
                    )
                StepClass = STEP_REGISTRY[step_type]
                step_instance: StepProtocol = StepClass(sub_logger, step_cfg)

                sub_logger.info(f"Launching substep {idx} of type '{step_type}'")
                await step_instance.execute(sub_context)
                sub_logger.info(f"Substep {idx} completed successfully")

            except Exception as exc:
                # Record first exception
                if failure["exc"] is None:
                    failure["exc"] = exc
                    failure["idx"] = idx
                sub_logger.error(
                    f"Substep {idx} failed: {exc}", exc_info=True
                )
                raise

            finally:
                semaphore.release()

        # Launch substeps with concurrency control and optional delay
        for idx, spec in enumerate(substeps):
            if failure["exc"]:
                self.logger.debug(
                    f"Fail-fast: aborting launch of remaining substeps at index {idx}"
                )
                break

            await semaphore.acquire()
            if delay > 0:
                await asyncio.sleep(delay)

            task = asyncio.create_task(run_substep(idx, spec))
            tasks.append(task)

        if not tasks:
            self.logger.info("No substeps were launched. Nothing to wait for.")
            return

        # Wait for first exception or all to finish
        done: Set[asyncio.Task] = set()
        pending: Set[asyncio.Task] = set()
        try:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_EXCEPTION
            )
        except Exception:
            # Should not happen; tasks errors handled below
            pass

        if failure["exc"]:
            failed_idx: Optional[int] = failure.get("idx")
            self.logger.error(
                f"A substep failed at index {failed_idx}; cancelling remaining tasks"
            )
            for p in pending:
                p.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            raise RuntimeError(
                f"ParallelStep aborted due to failure in substep {failed_idx}"
            ) from failure["exc"]

        # All succeeded; ensure finalization
        await asyncio.gather(*done)
        success_count: int = len(done)
        self.logger.info(
            f"Completed ParallelStep: {success_count}/{total} substeps succeeded"
        )


=== File: recipe_executor/steps/read_files.py ===
import json
import logging
import os
from typing import Any, Dict, List, Union

import yaml

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name under which to store file content in the context (may be templated).
        optional (bool): Whether to continue if a file is not found (default: False).
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filename headers + content
            - "dict": Store a dictionary with file paths as keys and content as values
    """
    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    """
    Step that reads one or more files from disk and stores their content in the execution context.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        # Use model_validate to ensure proper pydantic validation
        validated = ReadFilesConfig.model_validate(config)
        super().__init__(logger, validated)

    async def execute(self, context: ContextProtocol) -> None:
        cfg = self.config
        # Resolve content_key template
        rendered_key = render_template(cfg.content_key, context)

        raw_path = cfg.path
        paths: List[str] = []

        # Render and normalize paths
        if isinstance(raw_path, str):
            rendered = render_template(raw_path, context)
            # Split comma-separated string into list
            if "," in rendered:
                parts = [p.strip() for p in rendered.split(",") if p.strip()]
                paths.extend(parts)
            else:
                paths.append(rendered)
        elif isinstance(raw_path, list):
            for entry in raw_path:
                if not isinstance(entry, str):
                    raise ValueError(f"Invalid path entry type: {entry!r}")
                rendered = render_template(entry, context)
                paths.append(rendered)
        else:
            raise ValueError(f"Invalid type for path: {type(raw_path)}")

        results: List[Any] = []
        result_map: Dict[str, Any] = {}

        for path in paths:
            self.logger.debug(f"Reading file at path: {path}")
            if not os.path.exists(path):
                msg = f"File not found: {path}"
                if cfg.optional:
                    self.logger.warning(f"Optional file missing, skipping: {path}")
                    continue
                raise FileNotFoundError(msg)

            # Read file content as UTF-8 text
            with open(path, mode="r", encoding="utf-8") as f:
                text = f.read()

            # Attempt to deserialize structured formats
            ext = os.path.splitext(path)[1].lower()
            content: Any = text
            try:
                if ext == ".json":
                    content = json.loads(text)
                elif ext in (".yaml", ".yml"):
                    content = yaml.safe_load(text)
            except Exception as exc:
                self.logger.warning(f"Failed to parse structured data from {path}: {exc}")
                content = text

            self.logger.info(f"Successfully read file: {path}")
            results.append(content)
            result_map[path] = content

        # Merge results according to merge_mode
        if not results:
            # No file was read
            if len(paths) <= 1:
                final_content: Any = ""
            elif cfg.merge_mode == "dict":
                final_content = {}
            else:
                final_content = ""
        elif len(results) == 1:
            # Single file => raw content
            final_content = results[0]
        else:
            # Multiple files
            if cfg.merge_mode == "dict":
                final_content = result_map
            else:
                segments: List[str] = []
                for p in paths:
                    if p in result_map:
                        raw = result_map[p]
                        segment = raw if isinstance(raw, str) else json.dumps(raw)
                        segments.append(f"{p}\n{segment}")
                final_content = "\n".join(segments)

        # Store content in context
        context[rendered_key] = final_content
        self.logger.info(f"Stored file content under key '{rendered_key}'")


=== File: recipe_executor/steps/registry.py ===
"""
Registry for mapping step type names to their implementation classes.

This registry is a simple global dictionary. Steps register themselves by
updating this mapping, allowing dynamic lookup based on the step type name.
"""
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global registry mapping step type names to their implementation classes.
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/set_context.py ===
from typing import Any, Dict, List, Literal, Union
import logging

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.protocols import ContextProtocol
from recipe_executor.utils.templates import render_template


def _has_unrendered_tags(s: str) -> bool:
    """
    Detect if the string still contains Liquid tags that need rendering.
    """
    return "{{" in s or "{%" in s


class SetContextConfig(StepConfig):
    """
    Config for SetContextStep.

    Fields:
        key: Name of the artifact in the Context.
        value: JSON-serialisable literal, list, dict or Liquid template string rendered against
               the current context.
        nested_render: Whether to render templates recursively until no tags remain.
        if_exists: Strategy when the key already exists:
                   • "overwrite" (default) – replace the existing value
                   • "merge" – combine the existing and new values
    """
    key: str
    value: Union[str, List[Any], Dict[str, Any]]
    nested_render: bool = False
    if_exists: Literal["overwrite", "merge"] = "overwrite"


class SetContextStep(BaseStep[SetContextConfig]):
    """
    Step to set or update an artifact in the execution context.
    """
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, SetContextConfig.model_validate(config))

    async def execute(self, context: ContextProtocol) -> None:
        key = self.config.key
        raw_value = self.config.value
        nested = self.config.nested_render
        existed = key in context

        # Render the provided value (single or nested passes)
        value = self._render_value(raw_value, context, nested)

        strategy = self.config.if_exists
        if strategy == "overwrite":
            context[key] = value
        elif strategy == "merge":
            if existed:
                old = context[key]
                merged = self._merge(old, value)
                context[key] = merged
            else:
                context[key] = value
        else:
            raise ValueError(f"Unknown if_exists strategy: '{strategy}'")

        self.logger.info(
            f"SetContextStep: key='{key}', strategy='{strategy}', existed={existed}"
        )

    def _render_value(
        self, raw: Any, context: ContextProtocol, nested: bool
    ) -> Any:
        """
        Recursively render Liquid templates in strings, lists, and dicts.

        If nested is True, re-render strings until no tags remain or no change.
        """
        if isinstance(raw, str):
            if not nested:
                return render_template(raw, context)
            # nested rendering loop
            result = render_template(raw, context)
            while _has_unrendered_tags(result):
                prev = result
                result = render_template(result, context)
                if result == prev:
                    break
            return result

        if isinstance(raw, list):
            return [self._render_value(item, context, nested) for item in raw]

        if isinstance(raw, dict):
            return {k: self._render_value(v, context, nested) for k, v in raw.items()}

        # Other JSON-serialisable types pass through
        return raw

    def _merge(self, old: Any, new: Any) -> Any:
        """
        Shallow merge helper for merging existing and new values.

        Merge semantics:
        - str + str => concatenate
        - list + list or item => append
        - dict + dict => shallow dict merge
        - mismatched types => [old, new]
        """
        # String concatenation
        if isinstance(old, str) and isinstance(new, str):
            return old + new

        # List append
        if isinstance(old, list):  # type: ignore
            if isinstance(new, list):  # type: ignore
                return old + new  # type: ignore
            return old + [new]  # type: ignore

        # Dict shallow merge
        if isinstance(old, dict) and isinstance(new, dict):  # type: ignore
            merged = old.copy()  # type: ignore
            merged.update(new)  # type: ignore
            return merged

        # Fallback for mismatched types
        return [old, new]


=== File: recipe_executor/steps/write_files.py ===
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils.templates import render_template


class WriteFilesConfig(StepConfig):
    """
    Configuration for WriteFilesStep.

    Attributes:
        files_key: Optional context key containing FileSpec or list/dict specs.
        files: Optional direct list of dicts with 'path'/'content' or their key references.
        root: Base directory for output files.
    """
    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes one or more files to disk based on FileSpec or dict inputs.
    """

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Resolve and render the root output directory
        raw_root: str = self.config.root or "."
        root: str = render_template(raw_root, context)

        files_to_write: List[Dict[str, Any]] = []

        # 1. Direct 'files' entries take precedence
        if self.config.files is not None:
            for entry in self.config.files:
                # Path extraction
                if "path" in entry:
                    raw_path = entry["path"]
                elif "path_key" in entry:
                    key = entry["path_key"]
                    if key not in context:
                        raise KeyError(f"Path key '{key}' not found in context.")
                    raw_path = context[key]
                else:
                    raise ValueError("Each file entry must have 'path' or 'path_key'.")
                path_str = str(raw_path)
                path = render_template(path_str, context)

                # Content extraction
                if "content" in entry:
                    raw_content = entry["content"]
                elif "content_key" in entry:
                    key = entry["content_key"]
                    if key not in context:
                        raise KeyError(f"Content key '{key}' not found in context.")
                    raw_content = context[key]
                else:
                    raise ValueError("Each file entry must have 'content' or 'content_key'.")

                files_to_write.append({"path": path, "content": raw_content})

        # 2. Use files from context via 'files_key'
        elif self.config.files_key:
            key = self.config.files_key
            if key not in context:
                raise KeyError(f"Files key '{key}' not found in context.")
            raw = context[key]

            if isinstance(raw, FileSpec):
                items: List[Union[FileSpec, Dict[str, Any]]] = [raw]
            elif isinstance(raw, dict):  # dict spec
                if "path" in raw and "content" in raw:
                    items = [raw]
                else:
                    raise ValueError(f"Malformed file dict under key '{key}': {raw}")
            elif isinstance(raw, list):  # list of specs
                items = raw  # type: ignore
            else:
                raise ValueError(f"Unsupported type for files_key '{key}': {type(raw)}")

            for item in items:
                if isinstance(item, FileSpec):
                    raw_path = item.path
                    raw_content = item.content
                elif isinstance(item, dict):
                    if "path" not in item or "content" not in item:
                        raise ValueError(f"Invalid file entry under '{key}': {item}")
                    raw_path = item["path"]
                    raw_content = item["content"]
                else:
                    raise ValueError(
                        f"Each file entry must be FileSpec or dict with 'path' and 'content', got {type(item)}"
                    )

                path_str = str(raw_path)
                path = render_template(path_str, context)
                files_to_write.append({"path": path, "content": raw_content})

        else:
            raise ValueError("Either 'files' or 'files_key' must be provided in WriteFilesConfig.")

        # Write each file to disk
        for entry in files_to_write:
            rel_path: str = entry.get("path", "")
            content = entry.get("content")

            # Compute the final filesystem path
            if root:
                combined = os.path.join(root, rel_path)
            else:
                combined = rel_path
            final_path = os.path.normpath(combined)

            try:
                # Ensure parent directories exist
                parent_dir = os.path.dirname(final_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                # Serialize content if needed
                if isinstance(content, (dict, list)):
                    try:
                        text = json.dumps(content, ensure_ascii=False, indent=2)
                    except Exception as err:
                        raise ValueError(
                            f"Failed to serialize content for '{final_path}': {err}"
                        )
                else:
                    # Convert None to empty string, others to string if not already
                    if content is None:
                        text = ""
                    elif not isinstance(content, str):
                        text = str(content)
                    else:
                        text = content

                # Debug log before writing
                self.logger.debug(f"[WriteFilesStep] Writing file: {final_path}\nContent:\n{text}")

                # Write file using UTF-8 encoding
                with open(final_path, "w", encoding="utf-8") as f:
                    f.write(text)

                # Info log after successful write
                size = len(text.encode("utf-8"))
                self.logger.info(f"[WriteFilesStep] Wrote file: {final_path} ({size} bytes)")

            except Exception as exc:
                self.logger.error(f"[WriteFilesStep] Error writing file '{rel_path}': {exc}")
                raise


=== File: recipe_executor/utils/models.py ===
"""
Utility functions for generating Pydantic models from JSON-Schema object definitions.
"""
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, create_model

__all__ = ["json_object_to_pydantic_model"]


def json_object_to_pydantic_model(
    schema: Dict[str, Any], model_name: str = "SchemaModel"
) -> Type[BaseModel]:
    """
    Convert a JSON-Schema object fragment into a Pydantic BaseModel subclass.

    Args:
        schema: A JSON-Schema fragment describing an object (type must be "object").
        model_name: Name for the generated Pydantic model class.

    Returns:
        A subclass of pydantic.BaseModel corresponding to the schema.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
    # Validate top-level schema
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary.")
    if "type" not in schema:
        raise ValueError('Schema missing required "type" property.')
    if schema["type"] != "object":
        raise ValueError('Root schema type must be "object".')

    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])
    if not isinstance(properties, dict):
        raise ValueError('Schema "properties" must be a dictionary if present.')
    if not isinstance(required_fields, list):
        raise ValueError('Schema "required" must be a list if present.')

    # Counter for naming nested models deterministically
    class _Counter:
        def __init__(self) -> None:
            self._cnt = 0

        def next(self) -> int:
            self._cnt += 1
            return self._cnt

    counter = _Counter()

    def _parse_field(
        field_schema: Dict[str, Any], field_name: str, parent_name: str
    ) -> Tuple[Any, Any]:
        # Ensure valid schema fragment
        if not isinstance(field_schema, dict):
            raise ValueError(f"Schema for field '{field_name}' must be a dictionary.")
        if "type" not in field_schema:
            raise ValueError(f"Schema for field '{field_name}' missing required 'type'.")

        ftype = field_schema["type"]
        # Primitive types
        if ftype == "string":
            return str, ...
        if ftype == "integer":
            return int, ...
        if ftype == "number":
            return float, ...
        if ftype == "boolean":
            return bool, ...
        # Nested object
        if ftype == "object":
            nested_name = f"{parent_name}_{field_name.capitalize()}Obj{counter.next()}"
            nested_model = _build_model(field_schema, nested_name)
            return nested_model, ...
        # Array / list
        if ftype in ("array", "list"):
            items = field_schema.get("items")
            if not isinstance(items, dict):
                raise ValueError(
                    f"Array field '{field_name}' missing valid 'items' schema."
                )
            item_type, _ = _parse_field(items, f"{field_name}_item", parent_name)
            return List[item_type], ...
        # Fallback
        return Any, ...

    def _wrap_optional(
        field_schema: Dict[str, Any], is_required: bool, field_name: str, parent_name: str
    ) -> Tuple[Any, Any]:
        type_hint, default = _parse_field(field_schema, field_name, parent_name)
        if not is_required:
            type_hint = Optional[type_hint]  # type: ignore
            default = None
        return type_hint, default

    def _build_model(obj_schema: Dict[str, Any], name: str) -> Type[BaseModel]:
        # Validate object schema
        if not isinstance(obj_schema, dict):
            raise ValueError(f"Nested schema '{name}' must be a dictionary.")
        if obj_schema.get("type") != "object":
            raise ValueError(f"Nested schema '{name}' type must be 'object'.")

        props = obj_schema.get("properties", {})
        req = obj_schema.get("required", [])
        if not isinstance(props, dict):
            raise ValueError(f"Nested schema '{name}' properties must be a dictionary.")
        if not isinstance(req, list):
            raise ValueError(f"Nested schema '{name}' required must be a list.")

        fields: Dict[str, Tuple[Any, Any]] = {}
        for prop, subschema in props.items():
            is_req = prop in req
            hint, default = _wrap_optional(subschema, is_req, prop, name)
            fields[prop] = (hint, default)

        return create_model(name, **fields)  # type: ignore

    # Build and return the top-level model
    return _build_model(schema, model_name)


=== File: recipe_executor/utils/templates.py ===
"""
Utility functions for rendering Liquid templates using context data.

This module provides a `render_template` function that uses the Python Liquid templating engine
to render strings with variables sourced from a context object implementing ContextProtocol.
Custom filters (e.g., snakecase) and extra filters (json, datetime) are enabled via the environment.
"""
import re
from typing import Any

from liquid import Environment
from liquid.exceptions import LiquidError

# Import ContextProtocol inside the module to avoid circular dependencies
from recipe_executor.protocols import ContextProtocol

__all__ = ["render_template"]

# Create a module‐level Liquid environment with extra filters enabled
_env = Environment(autoescape=False, extra=True)

# Register a custom `snakecase` filter

def _snakecase(value: Any) -> str:
    """
    Convert a string to snake_case.

    Non-alphanumeric characters are replaced with underscores, camelCase
    boundaries are separated, and result is lowercased.
    """
    s = str(value)
    # Replace spaces and dashes with underscores
    s = re.sub(r"[\s\-]+", "_", s)
    # Insert underscore before capital letters preceded by lowercase/digits
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)
    # Lowercase the string
    s = s.lower()
    # Remove any remaining invalid characters
    s = re.sub(r"[^a-z0-9_]", "", s)
    # Collapse multiple underscores
    s = re.sub(r"__+", "_", s)
    # Strip leading/trailing underscores
    return s.strip("_")

_env.filters["snakecase"] = _snakecase


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Python Liquid template using the provided context.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering,
                    includes details about the template and context.
    """
    try:
        # Parse and render the template with all context values
        template = _env.from_string(text)
        rendered = template.render(**context.dict())
        return rendered
    except LiquidError as e:
        # Liquid-specific errors
        raise ValueError(
            f"Liquid template rendering error: {e}. "
            f"Template: {text!r}. Context: {context.dict()!r}"
        )
    except Exception as e:
        # Generic errors
        raise ValueError(
            f"Error rendering template: {e}. "
            f"Template: {text!r}. Context: {context.dict()!r}"
        )

