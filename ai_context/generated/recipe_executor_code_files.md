=== File: .env.example ===
# Optional for the project
#LOG_LEVEL=DEBUG

# Required for the project
OPENAI_API_KEY=

# Additional APIs
#ANTHROPIC_API_KEY=
#GEMINI_API_KEY=

# Azure OpenAI
#AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_USE_MANAGED_IDENTITY=false
#AZURE_OPENAI_API_KEY=

#(Optional) The client ID of the specific managed identity to use.
#  If not provided, DefaultAzureCredential will be used.
#AZURE_MANAGED_IDENTITY_CLIENT_ID=


=== File: README.md ===
# Recipe Executor

A tool for executing recipe-like natural language instructions to generate and manipulate code and other files.

## Overview

The Recipe Executor is a flexible orchestration system that executes "recipes" - JSON-based definitions of sequential steps to perform tasks such as file reading, LLM-based content generation, and file writing. This project allows you to define complex workflows through simple recipe files.

## Key Components

- **Recipe Format**: JSON-based recipe definitions with steps
- **Step Types**: Various operations including file reading/writing, LLM generation, and sub-recipe execution
- **Context System**: Shared state for passing data between steps
- **Template Rendering**: Liquid templates for dynamic content generation

## Setup and Installation

### Prerequisites

Recommended installers:

- Linux: apt or your distribution's package manager
- macOS: [brew](https://brew.sh/)
- Windows: [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

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
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
5. Test the installation by running the example recipe:
   ```bash
   make recipe-executor-create
   ```

## Using the Makefile

The project includes several useful make commands:

- **`make`**: Sets up the virtual environment and installs all dependencies
- **`make recipe-executor-context`**: Builds AI context files for recipe executor development
- **`make recipe-executor-create`**: Generates recipe executor code from scratch using the recipe itself
- **`make recipe-executor-edit`**: Revises existing recipe executor code using recipes

## Running Recipes

Execute a recipe using the command line interface:

```bash
python recipe_executor/main.py path/to/your/recipe.json
```

You can also pass context variables:

```bash
python recipe_executor/main.py path/to/your/recipe.json --context key=value
```

## Project Structure

The project contains:

- **`recipe_executor/`**: Core implementation with modules for execution, context management, and steps
- **`recipes/`**: Recipe definition files that can be executed

## Building from Recipes

One of the most interesting aspects of this project is that it can generate its own code using recipes:

1. To generate the code from scratch:

   ```bash
   make recipe-executor-create
   ```

2. To edit/revise existing code:
   ```bash
   make recipe-executor-edit
   ```

This demonstrates the power of the Recipe Executor for code generation and maintenance tasks.


=== File: pyproject.toml ===
[project]
name = "recipe-executor"
version = "0.1.0"
description = "A tool for executing natural language recipe-like instructions"
authors = [{ name = "Brian Krabach" }]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "azure-identity>=1.21.0",
    "dotenv>=0.9.9",
    "pydantic-ai>=0.0.46",
    "pydantic-settings>=2.8.1",
    "python-dotenv>=1.1.0",
    "python-liquid>=2.0.1",
]

[dependency-groups]
dev = ["pyright>=1.1.389", "ruff>=0.11.2"]

[tool.uv]
package = true

[project.scripts]
recipe-executor = "recipe_executor.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["recipe_executor"]


=== File: recipe_executor/context.py ===
import copy
from typing import Any, Dict, Iterator, Optional


class Context:
    """
    Context is the shared state container for the Recipe Executor system.
    It provides a simple dictionary-like interface for storing and accessing artifacts
    and maintains a separate configuration for use during recipe execution.
    
    Core Responsibilities:
    - Store and provide access to artifacts (data shared between steps).
    - Maintain separate configuration values.
    - Provide dictionary-like operations (get, set, iteration).
    - Support deep cloning to ensure data isolation.
    """
    
    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Optional initial artifacts to store in the context.
            config: Optional configuration values for the context.
        """
        # Use deep copy for true data isolation
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}
    
    def __getitem__(self, key: str) -> Any:
        """
        Retrieve an artifact by key.

        Args:
            key: The key name of the artifact.

        Returns:
            The artifact associated with the key.
        
        Raises:
            KeyError: If the key is not present in the context, with a descriptive error message.
        """
        if key not in self._artifacts:
            raise KeyError(f"Artifact '{key}' not found in context.")
        return self._artifacts[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an artifact in the context.

        Args:
            key: The key under which the artifact is stored.
            value: The value of the artifact to store.
        """
        self._artifacts[key] = value
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get an artifact with an optional default if the key is missing.

        Args:
            key: The key of the artifact to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The artifact associated with the key or the provided default if key is missing.
        """
        return self._artifacts.get(key, default)
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the artifacts.

        Args:
            key: The key to check.

        Returns:
            True if the key exists; False otherwise.
        """
        return key in self._artifacts
    
    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.

        Returns:
            An iterator for the artifact keys.
        """
        # Convert keys to a list to avoid external modifications
        return iter(list(self._artifacts.keys()))
    
    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.

        Returns:
            An iterator over the keys of the artifacts.
        """
        return iter(list(self._artifacts.keys()))
    
    def __len__(self) -> int:
        """
        Return the count of artifacts stored.

        Returns:
            The number of artifacts in the context.
        """
        return len(self._artifacts)
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts dictionary.
        This ensures external code cannot modify the internal state of the context.

        Returns:
            A deep copy of the artifacts dictionary.
        """
        return copy.deepcopy(self._artifacts)
    
    def clone(self) -> "Context":
        """
        Return a deep copy of the current context.

        This method clones both the artifacts and configuration to ensure complete data isolation.
        
        Returns:
            A new Context instance with the current state copied deeply.
        """
        return Context(
            artifacts=copy.deepcopy(self._artifacts),
            config=copy.deepcopy(self.config)
        )


=== File: recipe_executor/executor.py ===
import json
import logging
import os
from typing import Any, Dict, Optional, Union

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class RecipeExecutor:
    """
    Executor component for the Recipe Executor system.

    Loads recipe definitions from various sources and executes their steps sequentially using the provided context.

    Supported recipe formats:
        - File path pointing to a JSON file
        - JSON string
        - Dictionary

    Each recipe must be a dictionary with a 'steps' key containing a list of step definitions.
    Each step must have a 'type' field that corresponds to a registered step in STEP_REGISTRY.
    """

    def __init__(self) -> None:
        # Minimal initialization. Could be expanded later if needed.
        pass

    def execute(
        self, recipe: Union[str, Dict[str, Any]], context: Context, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Execute a recipe with the given context.

        Args:
            recipe: Recipe to execute; can be a file path, JSON string, or dictionary.
            context: Context instance for execution that stores shared artifacts.
            logger: Optional logger; if not provided, a default one will be created.

        Raises:
            ValueError: If the recipe format is invalid or the execution of any step fails.
            TypeError: If the recipe type is not supported.
        """
        # Set up the logger if not provided
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

        # Determine the recipe data source (dictionary, file path, or JSON string)
        recipe_data: Dict[str, Any]
        if isinstance(recipe, dict):
            recipe_data = recipe
            logger.debug("Loaded recipe from dictionary.")
        elif isinstance(recipe, str):
            # Check if the string is a file path
            if os.path.exists(recipe) and os.path.isfile(recipe):
                try:
                    with open(recipe, "r", encoding="utf-8") as f:
                        recipe_data = json.load(f)
                    logger.debug(f"Recipe loaded successfully from file: {recipe}")
                except Exception as e:
                    raise ValueError(f"Failed to read or parse recipe file '{recipe}': {e}") from e
            else:
                # Attempt to parse the string as JSON
                try:
                    recipe_data = json.loads(recipe)
                    logger.debug("Recipe loaded successfully from JSON string.")
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid recipe format. Expected file path or valid JSON string. Error: {e}"
                    ) from e
        else:
            raise TypeError(f"Unsupported recipe type: {type(recipe)}")

        # Validate that the parsed recipe is a dictionary
        if not isinstance(recipe_data, dict):
            raise ValueError("Recipe must be a dictionary after parsing.")

        steps = recipe_data.get("steps")
        if not isinstance(steps, list):
            raise ValueError("Recipe must contain a 'steps' key with a list of steps.")

        logger.debug(f"Starting recipe execution with {len(steps)} step(s). Recipe data: {recipe_data}")

        # Execute each step sequentially
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step at index {idx} is not a valid dictionary.")

            step_type = step.get("type")
            if not step_type:
                raise ValueError(f"Step at index {idx} is missing the 'type' field.")

            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {idx}. Please ensure it is registered.")

            step_class = STEP_REGISTRY[step_type]

            try:
                logger.debug(f"Executing step {idx} of type '{step_type}'. Step details: {step}")
                step_instance = step_class(step, logger)
                step_instance.execute(context)
                logger.debug(f"Step {idx} executed successfully.")
            except Exception as e:
                raise ValueError(f"Error executing step at index {idx} (type '{step_type}'): {e}") from e

        logger.debug("Recipe execution completed successfully.")


=== File: recipe_executor/llm.py ===
import logging
import time
from typing import Optional

from recipe_executor.models import FileGenerationResult

# Import LLM model classes from pydantic_ai package
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel


def get_model(model_id: str):
    """
    Initialize and return an LLM model instance based on a standardized model identifier format.

    Supported model id formats:
      - openai:model_name
      - anthropic:model_name
      - gemini:model_name
      - azure:model_name or azure:model_name:deployment_name

    Raises:
        ValueError: for an improperly formatted model_id or unsupported provider.
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid model identifier: {model_id}")

    provider = parts[0].lower()

    if provider == "openai":
        model_name = parts[1]
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        model_name = parts[1]
        return AnthropicModel(model_name)
    elif provider == "gemini":
        model_name = parts[1]
        return GeminiModel(model_name)
    elif provider == "azure":
        # For Azure, allowed formats are: azure:model_name or azure:model_name:deployment_name
        if len(parts) == 2:
            model_name = parts[1]
            deployment_name = model_name  # Default deployment name is same as model name
        elif len(parts) == 3:
            model_name = parts[1]
            deployment_name = parts[2]
        else:
            raise ValueError(f"Invalid Azure model identifier: {model_id}")
        # Import the azure-specific function to get the model
        from recipe_executor.llm_utils.azure_openai import get_openai_model
        return get_openai_model(model_name=model_name, deployment_name=deployment_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize and return an Agent configured with the specified model identifier.

    If model_id is not specified, it defaults to 'openai:gpt-4o'.

    Returns:
        Agent instance with the result type set to FileGenerationResult.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model_instance = get_model(model_id)
    agent = Agent(model_instance, result_type=FileGenerationResult)
    return agent


def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Send a prompt to the LLM and return the validated FileGenerationResult.

    Args:
        prompt (str): The prompt/query to send to the LLM.
        model (Optional[str]): The LLM model identifier in the format 'provider:model_name' (or for Azure: 'azure:model_name[:deployment_name]').
                                Defaults to 'openai:gpt-4o' if not provided.
        logger (Optional[logging.Logger]): Logger instance to log debug and info messages. If not specified, a default logger named 'RecipeExecutor' is used.

    Returns:
        FileGenerationResult: The structured result produced by the LLM.

    Raises:
        Exception: Propagates any exceptions encountered during the LLM call with appropriate logging.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    if model is None:
        model = "openai:gpt-4o"

    logger.debug(f"LLM Request - Prompt: {prompt}, Model: {model}")

    agent = get_agent(model_id=model)
    start_time = time.time()
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.error(f"LLM call failed with error: {e}")
        raise
    elapsed = time.time() - start_time
    logger.info(f"Model {model} responded in {elapsed:.2f} seconds")
    logger.debug(f"LLM Response: {result}")

    # Return only the structured data from the result
    return result.data


=== File: recipe_executor/llm_utils/azure_openai.py ===
import logging
import os
from typing import Optional

import openai

# Import the PydanticAI model and provider for OpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# For managed identity, attempt to import the Azure Identity packages
try:
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, get_bearer_token_provider
except ImportError as e:
    raise ImportError("azure-identity package is required for managed identity authentication.") from e


def get_openai_model(
    model_name: str, deployment_name: Optional[str] = None, logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create and return a PydanticAI OpenAIModel instance configured for Azure OpenAI Service.

    The function reads configuration values from environment variables and supports both API key and managed identity authentication.

    Environment Variables:
      - AZURE_OPENAI_ENDPOINT: The endpoint of your Azure OpenAI resource (required).
      - AZURE_OPENAI_API_VERSION: The API version to use (optional, defaults to "2023-07-01-preview").
      - AZURE_OPENAI_DEPLOYMENT: The deployment name (optional, defaults to the model name).
      - AZURE_USE_MANAGED_IDENTITY: If set to "true" or "1", managed identity is used instead of API key.
      - AZURE_MANAGED_IDENTITY_CLIENT_ID: (Optional) The client ID for a user-assigned managed identity.
      - AZURE_OPENAI_API_KEY: The API key to use when managed identity is not employed.

    Args:
      model_name: The name of the underlying model (e.g., "gpt-4o").
      deployment_name: Optional override for the deployment name; if not provided, falls back to AZURE_OPENAI_DEPLOYMENT or model_name.
      logger: Optional logger; if not provided, a logger named "RecipeExecutor" is used.

    Returns:
      An instance of OpenAIModel configured with the proper authentication and endpoint settings.

    Raises:
      ValueError: If required environment variables are missing.
      Exception: If there is an error initializing the client or model.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Read required Azure configuration values
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not set in the environment.")

    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")
    azure_deployment = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT", model_name)

    # Determine if managed identity should be used
    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() in ("true", "1")

    if use_managed_identity:
        logger.info("Using managed identity authentication for Azure OpenAI.")
        client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        try:
            if client_id:
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
        except Exception as e:
            logger.error("Error initializing token provider with managed identity: %s", e)
            raise e
        try:
            azure_client = openai.AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=azure_deployment,
                azure_ad_token_provider=token_provider,
            )
        except Exception as e:
            logger.error("Error initializing Azure OpenAI client with managed identity: %s", e)
            raise e
    else:
        logger.info("Using API key authentication for Azure OpenAI.")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not azure_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY must be set when not using managed identity.")
        try:
            azure_client = openai.AsyncAzureOpenAI(
                api_key=azure_api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment=azure_deployment,
            )
        except Exception as e:
            logger.error("Error initializing Azure OpenAI client with API key: %s", e)
            raise e

    try:
        provider = OpenAIProvider(openai_client=azure_client)
        model = OpenAIModel(model_name, provider=provider)
    except Exception as e:
        logger.error("Error creating OpenAIModel: %s", e)
        raise e

    logger.info("Successfully created Azure OpenAI model for model '%s' with deployment '%s'.", model_name, azure_deployment)
    return model


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        model = get_openai_model("gpt-4o")
        print("Model created successfully:", model)
    except Exception as err:
        print("Failed to create model:", err)


=== File: recipe_executor/logger.py ===
import logging
import os
import sys
from typing import Optional


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    This function sets up separate handlers for debug, info, and error log files as well
    as a console handler for stdout. Each file is truncated (using mode='w') on each
    run to prevent unbounded growth of log files.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If the log directory cannot be created or log file handlers cannot be initialized.
    """
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Capture all logs at or above DEBUG

    # Remove any existing handlers to ensure a clean configuration
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define the common log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format)

    # Ensure the log directory exists
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Set up file handlers with mode 'w' to clear previous logs
    try:
        # Debug file handler: logs all messages (DEBUG and above)
        debug_file = os.path.join(log_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_file, mode="w")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)

        # Info file handler: logs INFO and above
        info_file = os.path.join(log_dir, "info.log")
        info_handler = logging.FileHandler(info_file, mode="w")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)

        # Error file handler: logs ERROR and above
        error_file = os.path.join(log_dir, "error.log")
        error_handler = logging.FileHandler(error_file, mode="w")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    except Exception as e:
        raise Exception(f"Failed to initialize file handlers: {e}")

    # Console Handler: logs INFO and above to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    # Example usage of the logger component
    try:
        logger = init_logger()
        logger.debug("Debug message: Detailed info for diagnosing problems")
        logger.info("Info message: Confirmation that things are working as expected")
        logger.warning("Warning message: Something unexpected happened")
        logger.error("Error message: A function could not be performed")
        logger.critical("Critical message: The program may be unable to continue running")
    except Exception as e:
        print(f"Logger initialization failed: {e}")


=== File: recipe_executor/main.py ===
import argparse
import sys
from typing import Dict, List

from dotenv import load_dotenv

from executor import RecipeExecutor
from recipe_executor.context import Context
from recipe_executor.logger import init_logger


def parse_context(context_list: List[str]) -> Dict[str, str]:
    """
    Parse a list of key=value strings into a dictionary.

    Args:
        context_list (List[str]): List of context strings in key=value format.

    Returns:
        Dict[str, str]: Dictionary containing parsed context values.

    Raises:
        ValueError: If any context string is malformed or key is empty.
    """
    context: Dict[str, str] = {}
    for item in context_list:
        if "=" not in item:
            raise ValueError(f"Malformed context item: {item}. Expected format key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty key in context pair: {item}.")
        context[key] = value
    return context


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    This function parses command-line arguments, loads environment variables, sets up logging,
    creates a Context from CLI inputs, and executes the specified recipe.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Define command-line argument parser
    parser = argparse.ArgumentParser(
        description="Recipe Executor Tool - Executes a recipe with additional context information."
    )
    parser.add_argument("recipe_path", help="Path to the recipe file to execute.")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files (default: logs)")
    parser.add_argument("--context", action="append", default=[], help="Additional context values as key=value pairs")
    args = parser.parse_args()

    # Parse context key=value pairs
    try:
        cli_context = parse_context(args.context) if args.context else {}
    except ValueError as e:
        sys.stderr.write(f"Context Error: {str(e)}\n")
        sys.exit(1)

    # Initialize logging system
    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Create the execution context with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        # Execute the specified recipe
        executor = RecipeExecutor()
        executor.execute(args.recipe_path, context, logger=logger)
    except Exception as e:
        logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


=== File: recipe_executor/models.py ===
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class FileSpec(BaseModel):
    """
    Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """
    path: str
    content: str


class FileGenerationResult(BaseModel):
    """
    Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """
    files: List[FileSpec]
    commentary: Optional[str] = None


class RecipeStep(BaseModel):
    """
    A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict[str, Any]): Dictionary containing configuration for the step.
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


=== File: recipe_executor/steps/__init__.py ===
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps by updating the registry
STEP_REGISTRY.update({
    "execute_recipe": ExecuteRecipeStep,
    "generate": GenerateWithLLMStep,
    "parallel": ParallelStep,
    "read_file": ReadFileStep,
    "write_files": WriteFilesStep,
})


=== File: recipe_executor/steps/base.py ===
import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from recipe_executor.context import Context


class StepConfig(BaseModel):
    """
    Base class for step configurations.

    Extend this class to create custom configuration models for steps.
    """
    pass


# Type variable for generic configuration type
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(Generic[ConfigType], ABC):
    """
    Base abstract class for all steps in the Recipe Executor system.

    Each concrete step must inherit from this class and implement the execute method.

    Args:
        config (ConfigType): The step configuration object validated via Pydantic.
        logger (Optional[logging.Logger]): Logger instance, defaults to 'RecipeExecutor' if not provided.
    """
    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger: logging.Logger = logger or logging.getLogger("RecipeExecutor")
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config.dict()}" if hasattr(self.config, 'dict') else f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using the provided context.

        Args:
            context (Context): The execution context for the recipe, enabling data sharing between steps.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        # Subclasses must override this method.
        raise NotImplementedError(f"Each step must implement the execute method. {self.__class__.__name__} did not.")


=== File: recipe_executor/steps/execute_recipe.py ===
import os
import logging
from typing import Dict, Optional

from recipe_executor.context import Context
from recipe_executor.executor import RecipeExecutor
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
    """Step to execute a sub-recipe using a provided recipe file path and context overrides.

    This step:
      - Applies template rendering on the recipe path and on context overrides.
      - Shares the current context with the sub-recipe, modifying it as needed with overrides.
      - Validates that the sub-recipe file exists before executing it.
      - Logs the start and completion details of sub-recipe execution.
      - Uses the existing RecipeExecutor to run the sub-recipe.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize with config converted by ExecuteRecipeConfig
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """Execute the sub-recipe with context overrides and template rendering.

        Args:
            context (Context): The execution context received from the parent recipe.

        Raises:
            FileNotFoundError: If the sub-recipe file does not exist.
            Exception: Propagates any error encountered during sub-recipe execution.
        """
        # Apply context overrides using template rendering
        if hasattr(self.config, 'context_overrides') and self.config.context_overrides:
            for key, value in self.config.context_overrides.items():
                try:
                    rendered_value = render_template(value, context)
                    context[key] = rendered_value
                except Exception as e:
                    self.logger.error(f"Error rendering context override for key '{key}': {str(e)}")
                    raise

        # Render the recipe path using the current context
        try:
            recipe_path = render_template(self.config.recipe_path, context)
        except Exception as e:
            self.logger.error(f"Error rendering recipe path '{self.config.recipe_path}': {str(e)}")
            raise

        # Validate that the sub-recipe file exists
        if not os.path.exists(recipe_path):
            error_msg = f"Sub-recipe file not found: {recipe_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Log sub-recipe execution start
        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        try:
            # Execute the sub-recipe using the same executor
            executor = RecipeExecutor()
            executor.execute(recipe=recipe_path, context=context, logger=self.logger)
        except Exception as e:
            # Log error with sub-recipe path and propagate
            self.logger.error(f"Error during sub-recipe execution ({recipe_path}): {str(e)}")
            raise

        # Log sub-recipe execution completion
        self.logger.info(f"Completed sub-recipe: {recipe_path}")


=== File: recipe_executor/steps/generate_llm.py ===
import logging
from typing import Any

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.utils import render_template


class GenerateLLMConfig(StepConfig):
    """
    Config for GenerateWithLLMStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider:model_name format).
        artifact: The name under which to store the LLM response in context.
    """
    prompt: str
    model: str
    artifact: str


class GenerateWithLLMStep(BaseStep[GenerateLLMConfig]):
    """
    GenerateWithLLMStep is responsible for generating content using a large language model (LLM).
    It renders the prompt, model identifier, and artifact key from the provided context, calls the LLM,
    and stores the returned FileGenerationResult in the context under the rendered artifact key.
    
    The step follows a minimalistic design:
      - It uses template rendering for dynamic prompt and model resolution.
      - It allows the artifact key to be templated for dynamic context storage.
      - It logs details before and after calling the LLM.
    """

    def __init__(self, config: dict, logger: Any = None) -> None:
        """
        Initialize the GenerateWithLLMStep with its configuration and an optional logger.

        Args:
            config (dict): A dictionary containing the configuration for the step.
            logger (Optional[Any]): Logger instance to use for logging. Defaults to a logger with name "RecipeExecutor".
        """
        super().__init__(GenerateLLMConfig(**config), logger or logging.getLogger("RecipeExecutor"))

    def execute(self, context: Context) -> None:
        """
        Execute the LLM generation step using the provided context.
        
        This method performs the following:
          1. Dynamically render artifact key, prompt, and model values from the context.
          2. Log debug and info messages with details of the rendered parameters.
          3. Call the LLM using the rendered prompt and model.
          4. Store the resulting FileGenerationResult in the context under the rendered artifact key.
          5. Handle and log any errors encountered during generation.
        
        Args:
            context (Context): The shared context for execution containing input data and used for storing results.
        
        Raises:
            Exception: Propagates any exception encountered during processing, after logging the error.
        """
        try:
            # Process the artifact key using templating if needed
            artifact_key = self.config.artifact
            if "{{" in artifact_key and "}}" in artifact_key:
                artifact_key = render_template(artifact_key, context)

            # Render the prompt and model values using the current context
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)

            # Log the LLM call details
            self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
            self.logger.debug(f"Rendered prompt: {rendered_prompt}")
            self.logger.debug(f"Rendered model: {rendered_model}")

            # Call the LLM to generate content
            response = call_llm(rendered_prompt, rendered_model, logger=self.logger)

            # Store the LLM response in the context
            context[artifact_key] = response
            self.logger.debug(f"LLM response stored in context under '{artifact_key}'")

        except Exception as e:
            # Log detailed error information for debugging
            self.logger.error(f"Failed to generate content using LLM. Error: {e}")
            raise


=== File: recipe_executor/steps/parallel.py ===
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class ParallelConfig(StepConfig):
    """
    Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel.
                  Each substep must be an execute_recipe step definition (with its own recipe_path, overrides, etc).
        max_concurrency: Maximum number of substeps to run concurrently.
                         Default = 0 means no explicit limit (all substeps may run at once, limited only by system resources).
        delay: Optional delay (in seconds) between launching each substep.
               Default = 0 means no delay (all allowed substeps start immediately).
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """
    ParallelStep executes multiple sub-recipes concurrently in isolated contexts.

    It uses a ThreadPoolExecutor to run substeps in parallel with optional concurrency limits
    and launch delays. Implements fail-fast behavior: if any substep fails, execution aborts
    and propagates the first encountered exception.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize the base step with ParallelConfig
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the parallel step: launch substeps concurrently and wait for completion.

        Args:
            context (Context): The execution context.

        Raises:
            Exception: Propagates the first encountered exception from any substep.
        """
        total_substeps: int = len(self.config.substeps)
        self.logger.info(f"ParallelStep starting with {total_substeps} substep(s).")

        # Determine max_workers: if max_concurrency is 0 or greater than total, use total_substeps
        max_workers: int = self.config.max_concurrency if self.config.max_concurrency > 0 else total_substeps

        futures = []
        first_exception: Optional[Exception] = None
        executor = ThreadPoolExecutor(max_workers=max_workers)

        try:
            # Submit tasks sequentially and respect delay between launches
            for index, sub_config in enumerate(self.config.substeps):
                # Fail-fast: if an error was encountered, stop launching new substeps
                if first_exception is not None:
                    self.logger.error("Aborting submission of further substeps due to previous error.")
                    break

                # Clone context for isolation
                sub_context = context.clone()

                # Validate step type
                step_type = sub_config.get("type")
                if step_type not in STEP_REGISTRY:
                    err_msg = f"Unrecognized step type '{step_type}' in substep at index {index}."
                    self.logger.error(err_msg)
                    raise ValueError(err_msg)

                # Instantiate the substep using the registry
                step_class = STEP_REGISTRY[step_type]
                substep_instance = step_class(sub_config, logger=self.logger)

                self.logger.info(f"Launching substep {index} (type: {step_type}).")

                # Submit the substep execution as a separate task using the cloned context
                future = executor.submit(self._execute_substep, substep_instance, sub_context, index)
                futures.append(future)

                # If a launch delay is configured and this is not the last substep, sleep
                if self.config.delay > 0 and index < total_substeps - 1:
                    time.sleep(self.config.delay)

            # Wait for all submitted tasks to complete
            for future in as_completed(futures):
                try:
                    # This will re-raise any exception from the substep
                    future.result()
                except Exception as exc:
                    self.logger.error(f"A substep failed with error: {exc}", exc_info=True)
                    first_exception = exc
                    # Fail-fast: stop waiting on additional substeps
                    break

            # If an exception was encountered, cancel any pending substeps
            if first_exception is not None:
                self.logger.error("Fail-fast activated. Cancelling pending substeps.")
                for fut in futures:
                    fut.cancel()
                raise first_exception

            self.logger.info("ParallelStep completed all substeps successfully.")

        finally:
            executor.shutdown(wait=True)

    def _execute_substep(self, step_instance: BaseStep, context: Context, index: int) -> None:
        """
        Execute an individual substep with its cloned context.

        Args:
            step_instance (BaseStep): The substep instance to execute.
            context (Context): The cloned context for this substep.
            index (int): Index of the substep, for logging purposes.

        Raises:
            Exception: Propagates any exception encountered during execution of the substep.
        """
        self.logger.info(f"Substep {index} started.")
        try:
            step_instance.execute(context)
            self.logger.info(f"Substep {index} completed successfully.")
        except Exception as e:
            self.logger.error(f"Substep {index} failed with error: {e}", exc_info=True)
            raise e


=== File: recipe_executor/steps/read_file.py ===
import os
import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Fields:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found.
    """
    path: str
    artifact: str
    optional: bool = False


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    ReadFileStep component reads a file from the filesystem and stores its contents into the execution context.

    This step renders the file path using the given context, reads the contents of the file, and assigns it to a specified key.
    It handles missing files based on the 'optional' configuration flag. If the file is optional and not found,
    an empty string is stored in the context, otherwise a FileNotFoundError is raised.
    """
    
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the provided config dictionary into a ReadFileConfig instance and initialize the base step
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the ReadFileStep:
          - Render the file path using template rendering
          - Check for file existence
          - Read file content using UTF-8 encoding
          - Store the content into the context under the specified artifact key
          - Handle missing files based on the 'optional' flag

        Args:
            context (Context): The shared execution context.

        Raises:
            FileNotFoundError: If the file is not found and the step is not marked as optional.
        """
        # Render the file path using values from the execution context
        path: str = render_template(self.config.path, context)
        self.logger.debug(f"Rendered file path: {path}")

        # Check if the file exists at the rendered path
        if not os.path.exists(path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {path}, continuing without file.")
                context[self.config.artifact] = ""
                return
            else:
                error_msg: str = f"ReadFileStep: file not found at path: {path}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        # File exists, attempt to read its contents with UTF-8 encoding
        self.logger.info(f"Reading file from path: {path}")
        try:
            with open(path, "r", encoding="utf-8") as file:
                content: str = file.read()
        except Exception as e:
            self.logger.error(f"Error reading file at {path}: {e}")
            raise

        # Store the file content into the context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global step registry mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


=== File: recipe_executor/steps/write_files.py ===
import logging
import os
from typing import List, Optional

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to ".".
    """

    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilesConfig]):
    """
    WriteFilesStep writes generated files to disk based on content from the execution context.
    It handles template rendering, directory creation, and logging of file operations.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict config to WriteFilesConfig via Pydantic
        super().__init__(WriteFilesConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the write files step.

        Retrieves an artifact from the context, validates its type, and writes the corresponding files to disk.
        It supports both FileGenerationResult and a list of FileSpec objects.

        Args:
            context (Context): The execution context containing artifacts and configuration.

        Raises:
            ValueError: If the artifact is missing or if the root path rendering fails.
            TypeError: If the artifact is not a FileGenerationResult or a list of FileSpec objects.
            IOError: If an error occurs during file writing.
        """
        # Retrieve the artifact from the context
        data = context.get(self.config.artifact)
        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine the list of files to write
        if isinstance(data, FileGenerationResult):
            files: List[FileSpec] = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        # Render the root output path using template rendering
        try:
            output_root = render_template(self.config.root, context)
        except Exception as e:
            raise ValueError(f"Error rendering root path '{self.config.root}': {str(e)}")

        # Process each file: resolve file path, create directories, and write the file
        for file in files:
            try:
                # Render the file path; file.path may contain template variables
                rel_path = render_template(file.path, context)
                full_path = os.path.join(output_root, rel_path)

                # Ensure that the parent directory exists
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

                # Write the file content using UTF-8 encoding
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)

                self.logger.info(f"Wrote file: {full_path}")
            except Exception as e:
                self.logger.error(f"Error writing file '{file.path}': {str(e)}")
                raise IOError(f"Error writing file '{file.path}': {str(e)}")


=== File: recipe_executor/utils.py ===
from typing import Any

from liquid import Template

from recipe_executor.context import Context


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The Liquid template text to be rendered.
        context (Context): The context containing values for substitution.

    Returns:
        str: The rendered template string.

    Raises:
        ValueError: When there is an error during template rendering.
    """
    try:
        # Retrieve all artifacts from the context as a dictionary.
        # Convert each value to a string to ensure compatibility with the Liquid engine.
        context_dict = context.as_dict()
        safe_context = {key: str(value) for key, value in context_dict.items()}
        
        # Create the Liquid template and render it using the prepared safe context.
        template = Template(text)
        rendered = template.render(**safe_context)
        return rendered
    except Exception as e:
        # Raise a ValueError wrapping the original error with a clear error message.
        raise ValueError(f"Error rendering template: {e}") from e


