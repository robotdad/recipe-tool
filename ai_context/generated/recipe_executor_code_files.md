# AI Context Files
Date: 4/22/2025, 1:55:48 PM
Files: 24

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
# Recipe Tools

A tool for executing recipe-like natural language instructions to create complex workflows. This project includes a recipe executor and a recipe creator, both of which can be used to automate tasks and generate new recipes.

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
recipe-tool --execute recipes/example_simple/test_recipe.json model=azure/o3-mini
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
recipe-tool --execute output/analyze_codebase.json input=ai_context/generated/recipe_executor_code_files.md,ai_context/generated/recipe_executor_recipe_files.md
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

## Contributing & Development

We have a doc just for that... [dev_guidance.md](docs/dev_guidance.md)


=== File: pyproject.toml ===
[project]
name = "recipe-executor"
version = "0.1.0"
description = "A tool for executing natural language recipe-like instructions"
authors = [{ name = "Brian Krabach" }]
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

[tool.hatch.build.targets.wheel]
packages = ["recipe_executor"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"


=== File: recipe_executor/__init__.py ===


=== File: recipe_executor/context.py ===
import copy
import json as jsonlib
from typing import Any, Dict, Iterator, Optional

from recipe_executor.protocols import ContextProtocol


class Context(ContextProtocol):
    def __init__(
        self,
        artifacts: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self._config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        if key not in self._artifacts:
            raise KeyError(f"Key '{key}' not found in Context.")
        return self._artifacts[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._artifacts[key] = value

    def __delitem__(self, key: str) -> None:
        if key not in self._artifacts:
            raise KeyError(f"Key '{key}' not found in Context.")
        del self._artifacts[key]

    def __contains__(self, key: str) -> bool:
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        # Return iterator over a static list of keys to prevent issues on modification
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        return len(self._artifacts)

    def get(self, key: str, default: Any = None) -> Any:
        return self._artifacts.get(key, default)

    def clone(self) -> "Context":
        return Context(
            artifacts=copy.deepcopy(self._artifacts),
            config=copy.deepcopy(self._config),
        )

    def dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._artifacts)

    def json(self) -> str:
        return jsonlib.dumps(self._artifacts)

    def keys(self) -> Iterator[str]:
        return iter(list(self._artifacts.keys()))

    def get_config(self) -> Dict[str, Any]:
        return self._config

    def set_config(self, config: Dict[str, Any]) -> None:
        self._config = config


=== File: recipe_executor/executor.py ===
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union

from recipe_executor.models import Recipe
from recipe_executor.protocols import ContextProtocol, ExecutorProtocol
from recipe_executor.steps.registry import STEP_REGISTRY


class Executor(ExecutorProtocol):
    """
    Stateless executor for loading, validating, and running recipe steps.
    Implements ExecutorProtocol. Does NOT retain state between runs.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger: logging.Logger = logger

    async def execute(
        self,
        recipe: Union[str, Path, Dict[str, Any], Recipe],
        context: ContextProtocol,
    ) -> None:
        """
        Load the recipe from any supported type, validate structure, and execute each step sequentially.
        On error, raises ValueError with context about which step or input failed.
        """
        recipe_obj: Recipe = self._load_recipe(recipe)
        self.logger.debug(f"Loaded recipe ({len(recipe_obj.steps)} steps): {recipe_obj.model_dump()}")
        for index, step in enumerate(recipe_obj.steps):
            step_type: str = step.type
            step_config: Dict[str, Any] = step.config or {}
            self.logger.debug(f"Executing step {index}: type='{step_type}', config={step_config}")
            step_class = STEP_REGISTRY.get(step_type)
            if step_class is None:
                raise ValueError(f"Unknown step type '{step_type}' at index {index}")
            try:
                step_instance = step_class(self.logger, step_config)
                result = step_instance.execute(context)
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:
                raise ValueError(f"Step {index} ('{step_type}') failed: {exc}") from exc
            self.logger.debug(f"Step {index} ('{step_type}') executed successfully.")
        self.logger.debug("All recipe steps executed successfully.")

    def _load_recipe(self, recipe: Union[str, Path, Dict[str, Any], Recipe]) -> Recipe:
        # If already validated model
        if isinstance(recipe, Recipe):
            self.logger.debug("Recipe input is already a Recipe model.")
            return recipe
        # Dict
        if isinstance(recipe, dict):
            self.logger.debug("Recipe input is a dict; validating against Recipe model.")
            try:
                return Recipe.model_validate(recipe)
            except Exception as exc:
                raise ValueError(f"Invalid recipe dictionary: {exc}") from exc
        # If Path or string: determine whether file path or raw JSON
        recipe_str: str
        if isinstance(recipe, Path):
            recipe_str = str(recipe)
        else:
            recipe_str = recipe
        if not isinstance(recipe_str, str):
            raise TypeError(f"Recipe argument must be a str, Path, dict, or Recipe model, not {type(recipe)}")
        if os.path.isfile(recipe_str):
            self.logger.debug(f"Recipe input is a file path: {recipe_str}")
            try:
                with open(recipe_str, "r", encoding="utf-8") as file:
                    loaded = json.load(file)
            except Exception as exc:
                raise ValueError(f"Error reading recipe file '{recipe_str}': {exc}") from exc
            try:
                return Recipe.model_validate(loaded)
            except Exception as exc:
                raise ValueError(f"Invalid recipe in file '{recipe_str}': {exc}") from exc
        else:
            self.logger.debug("Recipe input is a raw JSON string.")
            try:
                loaded = json.loads(recipe_str)
            except Exception as exc:
                raise ValueError(f"Error parsing recipe JSON string: {exc}") from exc
            try:
                return Recipe.model_validate(loaded)
            except Exception as exc:
                raise ValueError(f"Invalid recipe JSON string: {exc}") from exc


=== File: recipe_executor/llm_utils/azure_openai.py ===
import logging
import os
from typing import Optional

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Constants
_DEFAULT_API_VERSION = "2025-03-01-preview"
_AZURE_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"


def _mask_api_key(api_key: Optional[str]) -> str:
    if not api_key:
        return ""  # pragma: nocover
    if len(api_key) <= 6:
        return api_key[0] + "***" + api_key[-1]
    return api_key[:2] + "***" + api_key[-2:]


def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None,
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from environment variables for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o3-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance created from AsyncAzureOpenAI client.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
    env = os.environ
    use_managed_identity = env.get("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
    api_key = env.get("AZURE_OPENAI_API_KEY")
    base_url = env.get("AZURE_OPENAI_BASE_URL") or env.get("AZURE_OPENAI_ENDPOINT")
    version = env.get("AZURE_OPENAI_API_VERSION", _DEFAULT_API_VERSION)
    env_deployment = env.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    managed_identity_client_id = env.get("AZURE_MANAGED_IDENTITY_CLIENT_ID") or env.get("AZURE_CLIENT_ID")

    deployment = deployment_name or env_deployment or model_name

    # Log environment variables with masking
    logger.debug(
        "AZURE_USE_MANAGED_IDENTITY=%r, AZURE_OPENAI_API_KEY=%s, AZURE_OPENAI_BASE_URL=%r, AZURE_OPENAI_API_VERSION=%r, AZURE_OPENAI_DEPLOYMENT_NAME=%r, AZURE_MANAGED_IDENTITY_CLIENT_ID=%r, AZURE_CLIENT_ID=%r",
        use_managed_identity,
        _mask_api_key(api_key),
        base_url,
        version,
        deployment,
        env.get("AZURE_MANAGED_IDENTITY_CLIENT_ID"),
        env.get("AZURE_CLIENT_ID"),
    )

    if not base_url:
        logger.error("AZURE_OPENAI_BASE_URL or AZURE_OPENAI_ENDPOINT must be set.")
        raise RuntimeError("Missing environment variable: AZURE_OPENAI_BASE_URL or AZURE_OPENAI_ENDPOINT.")
    if not deployment:
        logger.error("AZURE_OPENAI_DEPLOYMENT_NAME or model_name must be set.")
        raise RuntimeError("Missing deployment name for Azure OpenAI.")

    try:
        if use_managed_identity:
            logger.info(
                "Creating Azure OpenAI client using Azure Identity (managed identity%s) for deployment '%s' (model '%s').",
                f" (client_id={managed_identity_client_id})" if managed_identity_client_id else "",
                deployment,
                model_name,
            )
            # Pick which credential to use
            if managed_identity_client_id:
                credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id)
            else:
                credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(credential, _AZURE_COGNITIVE_SCOPE)
            azure_client = AsyncAzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=base_url,
                api_version=version,
                azure_deployment=deployment,
            )
            auth_method = f"managed_identity (client_id={managed_identity_client_id or 'default'})"

        else:
            if not api_key:
                logger.error("AZURE_OPENAI_API_KEY must be set for API key authentication.")
                raise RuntimeError("Missing environment variable: AZURE_OPENAI_API_KEY.")
            logger.info(
                "Creating Azure OpenAI client using API key for deployment '%s' (model '%s').", deployment, model_name
            )
            azure_client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=base_url,
                api_version=version,
                azure_deployment=deployment,
            )
            auth_method = "api_key"

        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(model_name, provider=provider)
        logger.info(
            "Azure OpenAIModel created successfully (model='%s', deployment='%s', auth_method='%s').",
            model_name,
            deployment,
            auth_method,
        )
        return openai_model
    except Exception as exc:
        logger.debug(f"Failed to create Azure OpenAIModel: {exc}", exc_info=True)
        logger.error(f"Could not create Azure OpenAI model ('{model_name}'): {exc}")
        raise


=== File: recipe_executor/llm_utils/llm.py ===
import logging
import os
import time
from typing import List, Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
from recipe_executor.llm_utils.mcp import MCPServer


def get_model(model_id: str, logger: logging.Logger) -> Union[OpenAIModel, AnthropicModel]:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.
    """
    if not isinstance(model_id, str):
        raise ValueError(
            "model_id must be a string of format 'provider/model_name' or 'provider/model_name/deployment_name'"
        )
    segments = model_id.split("/")
    if len(segments) < 2:
        raise ValueError(
            f"Invalid model_id: '{model_id}'. Expected format 'provider/model_name' or 'provider/model_name/deployment_name'."
        )

    provider: str = segments[0].lower()
    model_name: str = segments[1]
    deployment_name: Optional[str] = segments[2] if len(segments) > 2 else None

    if provider == "openai":
        return OpenAIModel(model_name=model_name)
    if provider == "azure":
        return get_azure_openai_model(logger=logger, model_name=model_name, deployment_name=deployment_name)
    if provider == "anthropic":
        return AnthropicModel(model_name=model_name)
    if provider == "ollama":
        ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        provider_obj: OpenAIProvider = OpenAIProvider(base_url=f"{ollama_base_url}/v1")
        return OpenAIModel(model_name=model_name, provider=provider_obj)

    raise ValueError(f"Unsupported provider: '{provider}'. Must be one of 'openai', 'azure', 'anthropic', 'ollama'.")


class LLM:
    def __init__(
        self,
        logger: logging.Logger,
        model: str = "openai/gpt-4o",
        mcp_servers: Optional[List[MCPServer]] = None,
    ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier.
            mcp_servers (Optional[List[MCPServer]]): MCP servers list.
        """
        self.logger: logging.Logger = logger
        self.model: str = model
        self.mcp_servers: List[MCPServer] = mcp_servers or []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.
        """
        actual_model_id: str = model if model is not None else self.model
        mcp_servers_to_use: List[MCPServer] = mcp_servers if mcp_servers is not None else self.mcp_servers
        # Info log: provider and model name
        provider = actual_model_id.split("/")[0] if "/" in actual_model_id else actual_model_id
        self.logger.info(f"LLM call with provider='{provider}' model='{actual_model_id}'")
        try:
            model_obj = get_model(actual_model_id, self.logger)
            agent: Agent[None, Union[str, BaseModel]] = Agent(
                model=model_obj,
                mcp_servers=mcp_servers_to_use,
                output_type=output_type,
            )
            self.logger.debug({
                "prompt": prompt,
                "model": actual_model_id,
                "output_type": output_type.__name__ if hasattr(output_type, "__name__") else str(output_type),
                "mcp_servers": [str(s) for s in mcp_servers_to_use],
            })
            start_time = time.monotonic()
            async with agent.run_mcp_servers():
                result = await agent.run(prompt)
            elapsed = time.monotonic() - start_time
            tokens_info = {}
            try:
                usage = result.usage()
                tokens_info = {
                    "requests": getattr(usage, "requests", None),
                    "request_tokens": getattr(usage, "request_tokens", None),
                    "response_tokens": getattr(usage, "response_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                }
            except Exception:
                pass
            self.logger.info({
                "elapsed_seconds": elapsed,
                **tokens_info,
            })
            self.logger.debug({"output": repr(result.output)})
            return result.output
        except Exception as exc:
            self.logger.error(f"LLM call failed: {exc}", exc_info=True)
            raise


=== File: recipe_executor/llm_utils/mcp.py ===
import copy
import logging
from typing import Any, Dict, Optional

from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio

# Example secrets to mask in logs
SENSITIVE_KEYS = {"authorization", "api_key", "token", "secret", "password", "access_token", "refresh_token"}


def _mask_sensitive(obj: Any) -> Any:
    """
    Recursively mask sensitive values in a dictionary (or lists of dictionaries) for logging.
    Returns a new object with sensitive values replaced.
    """
    if isinstance(obj, dict):
        masked = {}
        for key, value in obj.items():
            if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
                masked[key] = "***"
            else:
                masked[key] = _mask_sensitive(value)
        return masked
    elif isinstance(obj, list):
        return [_mask_sensitive(item) for item in obj]
    else:
        return obj


def get_mcp_server(
    logger: logging.Logger,
    config: Dict[str, Any],
) -> MCPServer:
    """
    Create an MCP server client based on the provided configuration.

    Args:
        logger: Logger for logging messages.
        config: Configuration for the MCP server.

    Returns:
        A configured PydanticAI MCP server client.

    Raises:
        ValueError: If the configuration is invalid or missing required information.
    """
    if not isinstance(config, dict):
        raise ValueError("config must be a dict")

    # Make a shallow copy for debugging/masking
    config_masked: Dict[str, Any] = _mask_sensitive(copy.deepcopy(config))
    logger.debug(f"get_mcp_server called with config: {config_masked}")

    # Determine whether to use HTTP or stdio transport (mutually exclusive)
    if "url" in config:
        url: str = config.get("url", "")
        if not isinstance(url, str) or not url:
            raise ValueError("'url' must be a non-empty string for MCPServerHTTP.")
        headers: Optional[Dict[str, str]] = config.get("headers")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError("'headers' must be a dictionary if provided.")
        # Mask headers for info log
        info_headers = _mask_sensitive(headers) if headers else None
        logger.info(f"Initializing MCPServerHTTP with url={url!r}, headers={info_headers!r}")
        try:
            return MCPServerHTTP(url=url, headers=headers)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MCPServerHTTP: {e}")
    elif "command" in config:
        command = config.get("command")
        if not isinstance(command, str) or not command:
            raise ValueError("'command' must be a non-empty string for MCPServerStdio.")
        args = config.get("args")
        if args is not None and not (isinstance(args, list) and all(isinstance(a, str) for a in args)):
            raise ValueError("'args' must be a list of strings if provided.")
        cwd = config.get("cwd")
        if cwd is not None and not isinstance(cwd, str):
            raise ValueError("'cwd' must be a string if provided.")
        logger.info(f"Initializing MCPServerStdio with command={command!r}, args={args!r}, cwd={cwd!r}")
        try:
            return MCPServerStdio(command, args=args or [], cwd=cwd)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MCPServerStdio: {e}")
    else:
        raise ValueError("Invalid MCP server config: must contain either 'url' for HTTP or 'command' for stdio.")


=== File: recipe_executor/logger.py ===
import logging
import os


def init_logger(log_dir: str = "logs", stdio_log_level: str = "INFO") -> logging.Logger:
    """
    Initializes and configures a logger instance writing to stdout and separate log files per level.
    Clears existing log files on each run.

    Args:
        log_dir (str): Directory for log files. Default: "logs".
        stdio_log_level (str): Log level for stdout. Default: "INFO". Case-insensitive.
            Options: "DEBUG", "INFO", "WARN", "ERROR".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If logger setup or file/directory access fails.
    """
    logger_name: str = "recipe_executor"
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Remove all previous handlers for full reset
    while logger.handlers:
        logger.handlers.pop()

    formatter: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Ensure log directory exists
    try:
        if not os.path.isdir(log_dir):
            logger.debug(f"Log directory '{log_dir}' does not exist. Attempting to create it.")
            os.makedirs(log_dir, exist_ok=True)
            logger.debug(f"Log directory '{log_dir}' created.")
    except Exception as error:
        error_message: str = f"Failed to create log directory '{log_dir}': {error}"
        logger.error(error_message)
        raise Exception(error_message)

    # Set up file handlers for debug, info, and error
    log_file_defs = [
        ("debug", os.path.join(log_dir, "debug.log"), logging.DEBUG),
        ("info", os.path.join(log_dir, "info.log"), logging.INFO),
        ("error", os.path.join(log_dir, "error.log"), logging.ERROR),
    ]

    for log_name, log_path, level in log_file_defs:
        try:
            file_handler: logging.FileHandler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.debug(f"Added file handler for '{log_path}' at level '{logging.getLevelName(level)}'.")
        except Exception as error:
            error_message: str = f"Failed to open log file '{log_path}': {error}"
            logger.error(error_message)
            raise Exception(error_message)

    # Set up stdout handler at INFO level by default
    try:
        stdio_log_level_norm: str = stdio_log_level.strip().upper()
        stdio_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARNING,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        stdio_level: int = stdio_map.get(stdio_log_level_norm, logging.INFO)
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(stdio_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.debug(f"Added stdout handler at level '{stdio_log_level_norm}'.")
    except Exception as error:
        error_message: str = f"Failed to initialize stdout logging: {error}"
        logger.error(error_message)
        raise Exception(error_message)

    logger.info("Logger initialized successfully.")
    return logger


=== File: recipe_executor/main.py ===
import argparse
import asyncio
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger


def parse_key_value_pairs(pairs: List[str], arg_name: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid {arg_name} format '{pair}'. Expected format: key=value.")
        key, value = pair.split("=", 1)
        if not key:
            raise ValueError(f"Invalid {arg_name} format '{pair}'. Key cannot be empty.")
        result[key] = value
    return result


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        sys.stderr.write("\nExecution interrupted by user.\n")
        sys.exit(1)


async def main_async() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Recipe Executor: command-line recipe runner.")
    parser.add_argument("recipe_path", type=str, help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory to write log files (default: 'logs').")
    parser.add_argument(
        "--context", action="append", default=[], help="Context artifact as key=value (can be repeated)."
    )
    parser.add_argument(
        "--config", action="append", default=[], help="Configuration value as key=value (can be repeated)."
    )
    args = parser.parse_args()

    logger: Optional[Any] = None
    exit_code: int = 0
    try:
        logger = init_logger(log_dir=args.log_dir)
    except Exception as exc:
        sys.stderr.write(f"Logger initialization failed: {str(exc)}\n")
        sys.exit(1)

    logger.info("Starting Recipe Executor Tool")
    start_time: float = time.time()

    try:
        logger.debug(f"Parsed arguments: {args}")
        try:
            artifacts: Dict[str, str] = parse_key_value_pairs(args.context, "--context")
            config: Dict[str, str] = parse_key_value_pairs(args.config, "--config")
        except ValueError as value_error:
            logger.error(f"Context Error: {str(value_error)}")
            sys.stderr.write(f"Context Error: {str(value_error)}\n")
            sys.exit(1)

        logger.debug(f"Initial context artifacts: {artifacts}")
        logger.debug(f"Initial config: {config}")

        context: Context = Context(artifacts=artifacts, config=config)
        executor: Executor = Executor(logger)

        logger.info(f"Executing recipe: {args.recipe_path}")
        await executor.execute(args.recipe_path, context)

        elapsed: float = time.time() - start_time
        logger.info(f"Recipe executed successfully in {elapsed:.2f} seconds.")
        print(f"Success: Recipe executed in {elapsed:.2f} seconds.")
        exit_code = 0
    except Exception as exc:
        if logger is not None:
            logger.error(f"An error occurred during recipe execution: {str(exc)}")
            logger.error(traceback.format_exc())
        sys.stderr.write(f"Execution failed: {str(exc)}\n")
        sys.stderr.write(traceback.format_exc())
        exit_code = 1
    sys.exit(exit_code)


=== File: recipe_executor/models.py ===
from typing import Any, Dict, List, Union

from pydantic import BaseModel


class FileSpec(BaseModel):
    """
    Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file.
    """

    path: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]


class RecipeStep(BaseModel):
    """
    A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
    """

    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """
    A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]


=== File: recipe_executor/protocols.py ===
"""
Protocols Component
-------------------

Defines protocols (interface contracts) for core components of the Recipe Executor system. These
enable loose coupling and prevent circular import dependencies. For usage and rationale, see
`protocols_docs.md`.
"""

import logging
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterator,
    Protocol,
    Union,
    runtime_checkable,
)

# Import only for type hints; concrete import in function signatures avoids cyclical dependencies.
from recipe_executor.models import Recipe


@runtime_checkable
class ContextProtocol(Protocol):
    def __getitem__(self, key: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...

    def __delitem__(self, key: str) -> None: ...

    def __contains__(self, key: str) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __len__(self) -> int: ...

    def get(self, key: str, default: Any = None) -> Any: ...

    def clone(self) -> "ContextProtocol": ...

    def dict(self) -> Dict[str, Any]: ...

    def json(self) -> str: ...

    def keys(self) -> Iterator[str]: ...

    def get_config(self) -> Dict[str, Any]: ...

    def set_config(self, config: Dict[str, Any]) -> None: ...


@runtime_checkable
class StepProtocol(Protocol):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None: ...

    async def execute(self, context: ContextProtocol) -> None: ...


@runtime_checkable
class ExecutorProtocol(Protocol):
    def __init__(self, logger: logging.Logger) -> None: ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None: ...


=== File: recipe_executor/steps/__init__.py ===
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import McpStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

# Register standard step implementations by updating the STEP_REGISTRY
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": McpStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})

__all__ = [
    "STEP_REGISTRY",
    "ExecuteRecipeStep",
    "LLMGenerateStep",
    "LoopStep",
    "McpStep",
    "ParallelStep",
    "ReadFilesStep",
    "WriteFilesStep",
]


=== File: recipe_executor/steps/base.py ===
import logging

# Delay import to avoid circular dependencies in type checking
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from recipe_executor.protocols import ContextProtocol


class StepConfig(BaseModel):
    """
    Base configuration model for steps.
    All step configs should inherit from this class.
    """

    pass


StepConfigType = TypeVar("StepConfigType", bound=StepConfig)


class BaseStep(Generic[StepConfigType]):
    """
    Minimal base class for all step classes. Provides config parsing/validation and logging.
    Enforces async execute(context) contract.
    """

    config: StepConfigType
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: StepConfigType) -> None:
        self.logger = logger
        self.config = config
        self.logger.debug(f"{self.__class__.__name__} initialized with config: {self.config}")

    async def execute(self, context: "ContextProtocol") -> None:
        """
        Perform the step's action.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.execute() must be implemented in a subclass.")


=== File: recipe_executor/steps/execute_recipe.py ===
import logging
import os
from typing import Any, Dict

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, str] = {}


class ExecuteRecipeStep(BaseStep[ExecuteRecipeConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ExecuteRecipeConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Import Executor here to avoid circular dependencies
        from recipe_executor.executor import Executor

        # 1. Render recipe_path as template
        try:
            rendered_recipe_path: str = render_template(self.config.recipe_path, context)
        except Exception as e:
            raise ValueError(f"Failed to render recipe_path template '{self.config.recipe_path}': {e}")

        # 2. Render context_overrides as templates
        rendered_context_overrides: Dict[str, str] = {}
        for key, raw_value in self.config.context_overrides.items():
            try:
                rendered_context_overrides[key] = render_template(raw_value, context)
            except Exception as e:
                raise ValueError(f"Failed to render context_overrides['{key}'] template '{raw_value}': {e}")

        # 3. Check if the recipe file exists
        if not os.path.exists(rendered_recipe_path):
            raise FileNotFoundError(f"Sub-recipe file does not exist: {rendered_recipe_path}")

        # 4. Apply context overrides
        for key, override_value in rendered_context_overrides.items():
            context[key] = override_value

        self.logger.info(f"Starting execution of sub-recipe: {rendered_recipe_path}")

        # 5. Execute the sub-recipe with the shared context
        executor = Executor(self.logger)
        try:
            result = await executor.execute(rendered_recipe_path, context)
        except Exception as e:
            raise RuntimeError(f"Error during execution of sub-recipe '{rendered_recipe_path}': {e}") from e

        self.logger.info(f"Finished execution of sub-recipe: {rendered_recipe_path}")


=== File: recipe_executor/steps/llm_generate.py ===
import logging
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, create_model

from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import FileSpec
from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class LLMGenerateConfig(StepConfig):
    prompt: str
    model: str = "openai/gpt-4o"
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: Union[str, Dict[str, Any]] = "text"
    output_key: str = "llm_output"


class FileSpecCollection(BaseModel):
    files: List[FileSpec]


class LLMGenerateStep(BaseStep[LLMGenerateConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LLMGenerateConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        prompt: str = render_template(self.config.prompt, context)
        model: str = render_template(self.config.model, context)
        output_key: str = render_template(self.config.output_key, context)
        mcp_servers: List[Any] = []
        mcp_server_configs: List[Dict[str, Any]] = []

        if self.config.mcp_servers is not None:
            mcp_server_configs.extend(self.config.mcp_servers)
        context_config: Dict[str, Any] = context.get_config()
        mcp_servers_from_context: Optional[List[Dict[str, Any]]] = context_config.get("mcp_servers", None)
        if mcp_servers_from_context is not None:
            mcp_server_configs.extend(mcp_servers_from_context)
        if mcp_server_configs:
            for mcp_server_config in mcp_server_configs:
                mcp_servers.append(get_mcp_server(self.logger, mcp_server_config))

        output_format: Union[str, Dict[str, Any]] = self.config.output_format
        rendered_output_format: Union[str, Dict[str, Any]] = output_format
        if isinstance(output_format, str):
            rendered_output_format = render_template(output_format, context)
        elif isinstance(output_format, dict):

            def render_schema(data: Any) -> Any:
                if isinstance(data, str):
                    return render_template(data, context)
                if isinstance(data, dict):
                    return {k: render_schema(v) for k, v in data.items()}
                if isinstance(data, list):
                    return [render_schema(x) for x in data]
                return data

            rendered_output_format = render_schema(output_format)

        output_type: Type[Union[str, BaseModel]] = str
        try:
            if rendered_output_format == "text":
                output_type = str
            elif rendered_output_format == "files":
                output_type = FileSpecCollection
            elif isinstance(rendered_output_format, dict):
                output_type = self._json_schema_to_pydantic_model(rendered_output_format)
            else:
                raise ValueError(f"Invalid output_format: {rendered_output_format}")

            self.logger.debug(
                f"Calling LLM: model={model} output_type={output_type} MCP_servers={'yes' if mcp_servers else 'no'}"
            )
            llm = LLM(
                logger=self.logger,
                model=model,
                mcp_servers=mcp_servers if mcp_servers else None,
            )
            result: Any = await llm.generate(prompt, output_type=output_type)
            if output_type is FileSpecCollection and isinstance(result, FileSpecCollection):
                context[output_key] = result.files
            else:
                context[output_key] = result
        except Exception as e:
            self.logger.error(f"LLM call failed for output_key '{output_key}': {e}", exc_info=True)
            raise

    def _json_schema_to_pydantic_model(self, schema: Dict[str, Any]) -> Type[BaseModel]:
        def build_type(subschema: Dict[str, Any]) -> Any:
            schema_type = subschema.get("type")
            if schema_type == "string":
                return (str, ...)
            if schema_type == "integer":
                return (int, ...)
            if schema_type == "number":
                return (float, ...)
            if schema_type == "boolean":
                return (bool, ...)
            if schema_type == "object":
                props = subschema.get("properties", {})
                required = set(subschema.get("required", []))
                fields = {}
                for pname, pschema in props.items():
                    ptype, _ = build_type(pschema)
                    default = ... if pname in required else None
                    fields[pname] = (ptype, default)
                model = create_model("JsonSchemaObj", **fields)  # type: ignore
                return (model, ...)
            if schema_type == "array" or schema_type == "list":
                items_schema = subschema.get("items", {})
                item_type, _ = build_type(items_schema)
                return (List[item_type], ...)
            return (Any, ...)

        if schema.get("type") == "array" or schema.get("type") == "list":
            item_schema = schema.get("items", {})
            item_type, _ = build_type(item_schema)
            return create_model("RootListModel", __root__=(List[item_type], ...))  # type: ignore
        if schema.get("type") == "object":
            props = schema.get("properties", {})
            required = set(schema.get("required", []))
            fields = {}
            for fname, fschema in props.items():
                ftype, _ = build_type(fschema)
                default = ... if fname in required else None
                fields[fname] = (ftype, default)
            return create_model("RootObjModel", **fields)  # type: ignore
        return create_model("AnyModel", __root__=(Any, ...))


=== File: recipe_executor/steps/loop.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from recipe_executor.protocols import ContextProtocol, ExecutorProtocol, StepProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Key in the context containing the collection to iterate over.
        item_key: Key to use when storing the current item in each iteration's context.
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error (default: True).
    """

    items: str
    item_key: str
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True


class LoopStep(BaseStep[LoopStepConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, LoopStepConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Validate required fields exist in context
        items_key: str = self.config.items
        item_key: str = self.config.item_key
        substeps: List[Dict[str, Any]] = self.config.substeps
        result_key: str = self.config.result_key
        fail_fast: bool = self.config.fail_fast

        if items_key not in context:
            self.logger.error(f"[LoopStep] Items key '{items_key}' not found in context.")
            raise ValueError(f"Items key '{items_key}' not found in context.")

        if not isinstance(substeps, list) or not substeps:
            self.logger.error("[LoopStep] Substeps must be a non-empty list.")
            raise ValueError("LoopStep requires at least one substep.")

        # Obtain the executor from the context
        executor: Optional[ExecutorProtocol] = context.get("__executor__", None)
        if executor is None:
            self.logger.error("[LoopStep] No executor found in context (missing '__executor__' key).")
            raise ValueError("LoopStep: No executor found in context (missing '__executor__' key).")

        # Support both arrays and objects
        raw_collection: Any = context[items_key]
        if isinstance(raw_collection, dict):
            collection = list(raw_collection.items())  # List[Tuple[str, Any]]
            is_dict = True
        elif isinstance(raw_collection, (list, tuple)):
            collection = list(enumerate(raw_collection))  # List[Tuple[int, Any]]
            is_dict = False
        else:
            self.logger.error(
                f"[LoopStep] The collection under key '{items_key}' "
                f"must be a list, tuple, or dict (got {type(raw_collection).__name__})."
            )
            raise ValueError(
                f"LoopStep: Items must be list/tuple/dict (got {type(raw_collection).__name__}) at key: {items_key}"
            )

        total_count: int = len(collection)
        self.logger.info(f"[LoopStep] Looping over {total_count} items from '{items_key}' to produce '{result_key}'.")
        if total_count == 0:
            self.logger.info(f"[LoopStep] Collection is empty. Storing empty results at '{result_key}'.")
            context[result_key] = []
            return

        results: List[Any] = []
        errors: List[Dict[str, Any]] = []

        async def process_item(item_info: Tuple[Union[int, str], Any]) -> Optional[Any]:
            key_or_index, item_value = item_info
            item_context: ContextProtocol = context.clone()
            item_context[item_key] = item_value
            if is_dict:
                item_context["__key"] = key_or_index
            else:
                item_context["__index"] = key_or_index
            item_id = f"{key_or_index}"
            self.logger.debug(f"[LoopStep] Starting processing item {item_id} ...")

            try:
                for substep_cfg in substeps:
                    step_type = substep_cfg.get("type")
                    if not step_type or step_type not in STEP_REGISTRY:
                        raise ValueError(f"Unknown or missing step type '{step_type}' in LoopStep substeps.")
                    step_cls = STEP_REGISTRY[step_type]
                    step_instance: StepProtocol = step_cls(self.logger, substep_cfg.get("config", {}))
                    if asyncio.iscoroutinefunction(step_instance.execute):
                        await step_instance.execute(item_context)
                    else:
                        # supporting legacy/non-async steps if any
                        await asyncio.get_event_loop().run_in_executor(None, step_instance.execute, item_context)
                    self.logger.debug(f"[LoopStep] Ran substep '{step_type}' for item {item_id}.")

                # Collect the processed result from item_context[item_key] (by default)
                result = item_context.get(item_key, None)
                self.logger.debug(f"[LoopStep] Finished processing item {item_id}.")
                return result
            except Exception as e:
                self.logger.error(f"[LoopStep] Error processing item {item_id}: {str(e)}", exc_info=True)
                errors.append({
                    "key": key_or_index if is_dict else None,
                    "index": key_or_index if not is_dict else None,
                    "error": str(e),
                })
                if fail_fast:
                    raise
                return None

        # Process all items sequentially (async for future scalability)
        for idx, item_info in enumerate(collection):
            try:
                result = await process_item(item_info)
                # Only add successful results
                if result is not None or not fail_fast:
                    results.append(result)
            except Exception:
                # On fail_fast, error already logged and exceptions bubble up
                break

        # Store the final results
        context[result_key] = results
        if errors:
            context["__errors"] = errors
        self.logger.info(f"[LoopStep] Stored results for {len(results)} items at '{result_key}'.")
        if errors:
            self.logger.error(f"[LoopStep] Encountered errors for {len(errors)} item(s): {errors}")


=== File: recipe_executor/steps/mcp.py ===
import logging
from typing import Any, Dict, Optional

from pydantic import Field

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template

# Import inside methods to avoid circular deps and unnecessary imports if not invoked


class McpConfig(StepConfig):
    """
    Configuration for McpStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key to store the tool result.
    """

    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = Field(default="tool_result")


class McpStep(BaseStep[McpConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, McpConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        # Render all templated string fields in config
        rendered_server: Dict[str, Any] = {}
        for k, v in self.config.server.items():
            if isinstance(v, str):
                rendered_server[k] = render_template(v, context)
            else:
                rendered_server[k] = v
        tool_name: str = render_template(self.config.tool_name, context)
        result_key: str = render_template(self.config.result_key, context) if self.config.result_key else "tool_result"
        # Arguments: also resolve any string values as templates
        rendered_arguments: Dict[str, Any] = {}
        args = self.config.arguments or {}
        for k, v in args.items():
            if isinstance(v, str):
                rendered_arguments[k] = render_template(v, context)
            else:
                rendered_arguments[k] = v

        # Select connection type
        sse_client = None
        stdio_client = None
        ClientSession = None
        StdioServerParameters = None
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.sse import sse_client
            from mcp.client.stdio import stdio_client
        except ImportError as exc:
            raise ValueError("mcp package is required for McpStep but not installed.") from exc

        # Connect and call tool
        session = None
        tool_result: Optional[Any] = None
        try:
            # Decide client type based on config
            if "url" in rendered_server and rendered_server["url"]:
                url = rendered_server["url"]
                headers = rendered_server.get("headers")
                self.logger.debug(f"Connecting to MCP server via SSE at {url} (tool={tool_name})")
                async with sse_client(url, headers=headers) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        self.logger.debug(f"Calling tool '{tool_name}' with arguments: {rendered_arguments}")
                        tool_result = await session.call_tool(tool_name, arguments=rendered_arguments)
            elif "command" in rendered_server and rendered_server["command"]:
                command = rendered_server["command"]
                args_list = rendered_server.get("args", [])
                env = rendered_server.get("env")
                working_dir = rendered_server.get("working_dir")
                server_params = StdioServerParameters(
                    command=command,
                    args=args_list,
                    env=env,
                    cwd=working_dir,
                )
                self.logger.debug(
                    f"Connecting to MCP stdio server: {command} {args_list} (cwd={working_dir}, tool={tool_name})"
                )
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        self.logger.debug(f"Calling tool '{tool_name}' with arguments: {rendered_arguments}")
                        tool_result = await session.call_tool(tool_name, arguments=rendered_arguments)
            else:
                raise ValueError("Invalid MCP server configuration: must provide either 'url' or 'command'.")
        except Exception as exc:
            # Wrap in ValueError with details as spec requires
            server_info = rendered_server.get("url") or rendered_server.get("command") or str(rendered_server)
            raise ValueError(f"Failed to call MCP tool '{tool_name}' on service '{server_info}': {exc}") from exc

        # Convert the result to dict if possible
        # If not already a dict, try to use .dict() if available, otherwise as-is
        result_dict: Dict[str, Any]
        if isinstance(tool_result, dict):
            result_dict = tool_result
        elif hasattr(tool_result, "dict"):
            result_dict = tool_result.dict()  # type: ignore
        else:
            result_dict = {"result": tool_result}

        context[result_key] = result_dict


=== File: recipe_executor/steps/parallel.py ===
import asyncio
import logging
from typing import Any, Dict, List, Optional

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step definitions, each with 'type' and 'config'.
        max_concurrency: Maximum concurrent substeps. 0 means no limit.
        delay: Delay in seconds between launching substeps.
    """

    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ParallelConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        total = len(self.config.substeps)
        self.logger.info("Starting parallel execution: %d substeps", total)

        semaphore: Optional[asyncio.Semaphore]
        if self.config.max_concurrency and self.config.max_concurrency > 0:
            semaphore = asyncio.Semaphore(self.config.max_concurrency)
        else:
            semaphore = None

        error_occurred = False
        first_exception: Optional[BaseException] = None

        async def run_substep(idx: int, substep_def: Dict[str, Any]) -> None:
            nonlocal error_occurred, first_exception
            if error_occurred:
                return

            if semaphore:
                await semaphore.acquire()

            try:
                # Clone context for isolation
                sub_context = context.clone()

                raw_step_type = substep_def.get("type")
                if not isinstance(raw_step_type, str):
                    raise ValueError(f"Invalid substep type: {raw_step_type}")
                step_type = raw_step_type
                step_conf = substep_def.get("config", {})
                step_cls = STEP_REGISTRY.get(step_type)
                if step_cls is None:
                    raise ValueError(f"Unknown substep type: {step_type}")

                sub_logger = self.logger.getChild(f"{step_type}[{idx}]")
                self.logger.debug("Launching substep %d of type %s", idx, step_type)
                step_instance = step_cls(sub_logger, step_conf)

                # Execute the substep (async or sync)
                await step_instance.execute(sub_context)

                self.logger.debug("Completed substep %d", idx)

            except Exception as exc:
                self.logger.error("Substep %d failed: %s", idx, str(exc), exc_info=True)
                if not error_occurred:
                    error_occurred = True
                    first_exception = exc
                raise

            finally:
                if semaphore:
                    semaphore.release()

        # Schedule tasks with optional delay
        tasks: List[asyncio.Task] = []
        for idx, sub_def in enumerate(self.config.substeps):
            if error_occurred:
                break
            task = asyncio.create_task(run_substep(idx, sub_def))
            tasks.append(task)
            if self.config.delay and idx < total - 1:
                await asyncio.sleep(self.config.delay)

        if not tasks:
            self.logger.info("No substeps to run.")
            return

        # Wait for tasks, fail-fast on first exception
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        # Check for exceptions in done
        for t in done:
            if t.cancelled():
                continue
            if t.exception():
                error_occurred = True
                if first_exception is None:
                    first_exception = t.exception()

        # Cancel any pending tasks
        if pending:
            for t in pending:
                t.cancel()
            # Allow cancelled tasks to finish
            await asyncio.gather(*pending, return_exceptions=True)

        if error_occurred and first_exception:
            # Propagate first exception
            raise first_exception

        self.logger.info("Parallel execution complete: %d/%d substeps succeeded", total, total)


=== File: recipe_executor/steps/read_files.py ===
import logging
import os
from typing import Any, Dict, List, Union

from recipe_executor.protocols import ContextProtocol
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        contents_key (str): Name to store the file contents in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + contents
            - "dict": Store a dictionary with filenames as keys and contents as values
    """

    path: Union[str, List[str]]
    contents_key: str
    optional: bool = False
    merge_mode: str = "concat"


class ReadFilesStep(BaseStep[ReadFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, ReadFilesConfig(**config))

    async def execute(self, context: ContextProtocol) -> None:
        rendered_path: Union[str, List[str]] = self._render_paths(self.config.path, context)
        paths: List[str] = self._parse_paths(rendered_path)

        if not paths:
            self.logger.info(f"No files to read for key '{self.config.contents_key}' (path: {self.config.path})")
            if self.config.merge_mode == "dict":
                context[self.config.contents_key] = {}
            else:
                context[self.config.contents_key] = ""
            return

        self.logger.debug(f"Resolved paths for reading: {paths}")

        contents_list: List[str] = []
        contents_dict: Dict[str, str] = {}
        missing_files: List[str] = []

        for path in paths:
            path_stripped: str = path.strip()
            self.logger.debug(f"Attempting to read file: {path_stripped}")
            if not os.path.isfile(path_stripped):
                if self.config.optional:
                    self.logger.warning(f"Optional file not found: {path_stripped} (step continues)")
                    missing_files.append(path_stripped)
                    continue
                else:
                    error_msg: str = f"File not found: {path_stripped} (required by read_files step)"
                    self.logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
            try:
                with open(path_stripped, encoding="utf-8") as file:
                    content: str = file.read()
                self.logger.info(f"Read file successfully: {path_stripped}")
                if self.config.merge_mode == "dict":
                    contents_dict[path_stripped] = content
                else:
                    contents_list.append(content)
            except Exception as exc:
                error_msg: str = f"Failed to read file {path_stripped}: {str(exc)}"
                if self.config.optional:
                    self.logger.warning(error_msg)
                    missing_files.append(path_stripped)
                    continue
                else:
                    self.logger.error(error_msg)
                    raise

        result: Union[str, Dict[str, str]]
        if self.config.merge_mode == "dict":
            result = contents_dict
        else:
            result = "\n".join(contents_list)

        # Backwards compatibility: optional + single file
        if len(paths) == 1 and self.config.merge_mode != "dict" and self.config.optional and not contents_list:
            result = ""

        context[self.config.contents_key] = result
        self.logger.info(
            f"Stored contents under key '{self.config.contents_key}' (mode: {self.config.merge_mode}, files read: {len(contents_list)})"
        )

    def _render_paths(self, path: Union[str, List[str]], context: ContextProtocol) -> Union[str, List[str]]:
        if isinstance(path, str):
            return render_template(path, context)
        if isinstance(path, list):
            return [render_template(single_path, context) for single_path in path]
        return path

    def _parse_paths(self, rendered_path: Union[str, List[str]]) -> List[str]:
        paths: List[str] = []
        if isinstance(rendered_path, str):
            if "," in rendered_path:
                parts: List[str] = [part.strip() for part in rendered_path.split(",") if part.strip()]
                paths.extend(parts)
            elif rendered_path.strip():
                paths.append(rendered_path.strip())
        elif isinstance(rendered_path, list):
            for element in rendered_path:
                if "," in element:
                    parts: List[str] = [part.strip() for part in element.split(",") if part.strip()]
                    paths.extend(parts)
                elif element.strip():
                    paths.append(element.strip())
        return paths


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Central registry for mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import logging
import os
from typing import Any, Dict, List, Optional

from recipe_executor.models import FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Fields:
        files_key: Optional name of the context key holding a List[FileSpec].
        files: Optional list of dictionaries with 'path' and 'content' keys.
        root: Optional base path to prepend to all output file paths.
    """

    files_key: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        super().__init__(logger, WriteFilesConfig(**config))

    async def execute(self, context) -> None:
        files_to_write: List[FileSpec] = []
        # Prefer files in config, fallback to files_key in context
        if self.config.files is not None:
            files_to_write = self._resolve_files_from_config(self.config.files, context)
        elif self.config.files_key is not None:
            if self.config.files_key not in context:
                msg = f"WriteFilesStep: Key '{self.config.files_key}' not found in context."
                self.logger.error(msg)
                raise ValueError(msg)
            artifact = context[self.config.files_key]
            files_to_write = self._normalize_files_from_context(artifact)
        else:
            msg = "WriteFilesStep: Either 'files' or 'files_key' must be provided in config."
            self.logger.error(msg)
            raise ValueError(msg)

        if not files_to_write:
            msg = "WriteFilesStep: No files to write."
            self.logger.warning(msg)
            return

        for file_spec in files_to_write:
            try:
                # Render root and path using templates
                rendered_root = render_template(self.config.root, context) if self.config.root else "."
                rendered_path = render_template(file_spec.path, context)
                output_path = os.path.normpath(os.path.join(rendered_root, rendered_path))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Log file info (debug) before writing
                self.logger.debug(f"WriteFilesStep: Preparing to write file: {output_path}")
                self.logger.debug(f"WriteFilesStep: File content for {output_path}: {repr(file_spec.content)}")
                # Write content as utf-8 (or dump content as-is if not string)
                with open(output_path, "w", encoding="utf-8") as f:
                    if isinstance(file_spec.content, str):
                        f.write(file_spec.content)
                    else:
                        import json

                        f.write(json.dumps(file_spec.content, indent=2))

                size = len(file_spec.content) if isinstance(file_spec.content, str) else len(str(file_spec.content))
                self.logger.info(f"WriteFilesStep: Wrote file '{output_path}' ({size} bytes)")
            except Exception as ex:
                self.logger.error(f"WriteFilesStep: Failed to write file '{file_spec.path}': {str(ex)}")
                raise

    def _resolve_files_from_config(self, files_config: List[Dict[str, Any]], context) -> List[FileSpec]:
        files: List[FileSpec] = []
        for idx, file_dict in enumerate(files_config):
            # Determine the path
            path: Optional[str] = None
            if "path" in file_dict:
                path = file_dict["path"]
                if path is None:
                    raise ValueError(f"WriteFilesStep: 'path' cannot be None (file index {idx})")
                path = render_template(path, context)
            elif "path_key" in file_dict:
                key = file_dict["path_key"]
                if key not in context:
                    raise ValueError(f"WriteFilesStep: path_key '{key}' not in context (file index {idx})")
                path = str(context[key])
                path = render_template(path, context)
            else:
                raise ValueError(f"WriteFilesStep: File at index {idx} missing 'path' or 'path_key'.")
            # Determine the content
            content: Any = None
            if "content" in file_dict:
                content = file_dict["content"]
            elif "content_key" in file_dict:
                key = file_dict["content_key"]
                if key not in context:
                    raise ValueError(f"WriteFilesStep: content_key '{key}' not in context (file index {idx})")
                content = context[key]
            else:
                raise ValueError(f"WriteFilesStep: File at index {idx} missing 'content' or 'content_key'.")
            files.append(FileSpec(path=path, content=content))
        return files

    def _normalize_files_from_context(self, artifact: Any) -> List[FileSpec]:
        if isinstance(artifact, FileSpec):
            return [artifact]
        elif isinstance(artifact, list):
            files: List[FileSpec] = []
            for idx, item in enumerate(artifact):
                if isinstance(item, FileSpec):
                    files.append(item)
                elif isinstance(item, dict):
                    try:
                        files.append(FileSpec.model_validate(item))
                    except Exception as ex:
                        raise ValueError(f"WriteFilesStep: Invalid file dict at index {idx}: {ex}")
                else:
                    raise ValueError(f"WriteFilesStep: Invalid file type at index {idx}")
            return files
        elif isinstance(artifact, dict):
            # Try to coerce to FileSpec
            try:
                return [FileSpec.model_validate(artifact)]
            except Exception as ex:
                raise ValueError(f"WriteFilesStep: Invalid file dict in context: {ex}")
        else:
            raise ValueError("WriteFilesStep: Provided artifact is not a FileSpec, list, or dict.")


=== File: recipe_executor/utils.py ===
from typing import Any

from liquid import Template
from liquid.exceptions import LiquidError

from recipe_executor.protocols import ContextProtocol


def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    data: dict[str, Any] = context.dict()
    string_context: dict[str, str] = {k: str(v) if v is not None else "" for k, v in data.items()}
    try:
        template = Template(text)
        return template.render(**string_context)
    except LiquidError as exc:
        raise ValueError(
            f"Liquid template rendering error: {exc}\nTemplate: {text}\nContext: {string_context}"
        ) from exc
    except Exception as exc:
        raise ValueError(f"Template rendering error: {exc}\nTemplate: {text}\nContext: {string_context}") from exc


