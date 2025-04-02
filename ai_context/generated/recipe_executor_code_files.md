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
dev = ["pyright>=1.1.389"]

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
from typing import Any, Dict, Optional, Iterator
import copy


class Context:
    """
    The Context class provides a shared state container for the Recipe Executor system.
    It allows steps to store and retrieve artifacts and configuration options within
    a recipe execution. This implementation follows a minimalist design as specified.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store
            config: Configuration values
        """
        # Use deep copy to prevent external modifications
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        """
        Dictionary-like access to artifacts.

        Args:
            key: The key of the artifact to retrieve

        Returns:
            The value associated with the key

        Raises:
            KeyError: If the key does not exist
        """
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in context artifacts.")

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Dictionary-like setting of artifacts.

        Args:
            key: The key to be set
            value: The value to associate with the key
        """
        self._artifacts[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get an artifact with an optional default value if the key is missing.

        Args:
            key: The key to retrieve
            default: The value to return if key is not found

        Returns:
            The value associated with the key or the default value
        """
        return self._artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in artifacts.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over the artifact keys. Converts keys to a list for safe iteration.

        Returns:
            An iterator over the keys of the artifacts
        """
        # Convert keys to a list to prevent issues if artifacts are modified during iteration
        return iter(list(self._artifacts.keys()))

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the keys of artifacts.

        Returns:
            An iterator over artifact keys
        """
        return self.__iter__()

    def __len__(self) -> int:
        """
        Return the number of artifacts stored in the context.

        Returns:
            The number of artifacts
        """
        return len(self._artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a copy of the artifacts as a dictionary to ensure immutability.

        Returns:
            A copy of the artifacts dictionary
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> 'Context':
        """
        Return a deep copy of the current context, including artifacts and configuration.

        Returns:
            A new Context object with a deep copy of the current state
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))


=== File: recipe_executor/executor.py ===
import os
import json
import logging
from typing import Any, Dict, Union, Optional

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY

class RecipeExecutor:
    """
    The RecipeExecutor is responsible for orchestrating the execution of a recipe.
    It supports loading recipes from file paths, JSON strings, or dictionaries, validates
    the recipe structure, and executes each step sequentially using the provided context.
    """

    def execute(
        self,
        recipe: Union[str, Dict[str, Any]],
        context: Context,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Execute a recipe with the given context.

        Args:
            recipe: Recipe to execute, can be a file path, JSON string, or dictionary
            context: Context instance to use for execution
            logger: Optional logger to use, creates a default one if not provided

        Raises:
            ValueError: If recipe format is invalid or step execution fails
            TypeError: If recipe type is not supported
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                # Create a basic configuration if none exists
                logging.basicConfig(level=logging.DEBUG)

        logger.debug("Starting recipe execution.")

        # Load and parse recipe into a dictionary
        recipe_payload: Dict[str, Any]
        if isinstance(recipe, dict):
            recipe_payload = recipe
            logger.debug("Recipe provided as dictionary.")
        elif isinstance(recipe, str):
            # Check if it's a file path
            if os.path.exists(recipe):
                logger.debug(f"Loading recipe from file: {recipe}")
                try:
                    with open(recipe, 'r', encoding='utf-8') as file:
                        recipe_payload = json.load(file)
                except Exception as e:
                    raise ValueError(f"Failed to load recipe from file '{recipe}': {e}")
            else:
                # Assume it's a JSON string
                logger.debug("Loading recipe from JSON string.")
                try:
                    recipe_payload = json.loads(recipe)
                except Exception as e:
                    raise ValueError(f"Failed to parse recipe JSON string: {e}")
        else:
            raise TypeError("Unsupported recipe type. Must be a file path, JSON string, or dictionary.")

        logger.debug(f"Parsed recipe payload: {recipe_payload}")

        # Validate that the recipe contains a 'steps' key
        if 'steps' not in recipe_payload or not isinstance(recipe_payload['steps'], list):
            raise ValueError("Invalid recipe format: Missing 'steps' list.")

        steps = recipe_payload['steps']

        # Execute steps sequentially
        for index, step in enumerate(steps):
            logger.debug(f"Processing step {index + 1}: {step}")

            if not isinstance(step, dict):
                raise ValueError(f"Invalid step format at index {index}: Step must be a dictionary.")

            if 'type' not in step:
                raise ValueError(f"Missing 'type' in step at index {index}.")

            step_type = step['type']
            if step_type not in STEP_REGISTRY:
                raise ValueError(f"Unknown step type '{step_type}' at index {index}.")

            step_class = STEP_REGISTRY[step_type]

            try:
                # Instantiate the step with its definition and logger
                step_instance = step_class(step, logger)
                logger.debug(f"Executing step {index + 1} of type '{step_type}'.")
                step_instance.execute(context)
                logger.debug(f"Completed step {index + 1}.")
            except Exception as e:
                # Wrap and re-raise with step index for clarity
                raise ValueError(f"Error executing step {index + 1} (type: '{step_type}'): {e}") from e

        logger.debug("Recipe execution completed successfully.")


=== File: recipe_executor/llm.py ===
import logging
import time
from typing import Optional, Union

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel

# Import our structured result models
from recipe_executor.models import FileGenerationResult


# The function get_model initializes the appropriate LLM model based on a standardized model id
# Format: 'provider:model_name' or 'provider:model_name:deployment_name' (for Azure OpenAI)

def get_model(model_id: str) -> Union[OpenAIModel, AnthropicModel, GeminiModel]:
    """
    Initialize an LLM model based on a standardized model_id string.

    Expected format:
      - For OpenAI:      "openai:model_name"
      - For Anthropic:   "anthropic:model_name"
      - For Gemini:      "gemini:model_name"
      - For Azure OpenAI: "azure:model_name" or "azure:model_name:deployment_name"

    Args:
        model_id (str): The model identifier in the format specified.

    Returns:
        An instance of the appropriate model class.

    Raises:
        ValueError: If the model_id format is invalid or provider unsupported.
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError("Invalid model_id format. Expected 'provider:model_name' at minimum.")

    provider = parts[0].lower()
    model_name = parts[1]

    if provider == "azure":
        # For Azure OpenAI, deployment_name may be provided; if not, default deployment equals model_name
        deployment_name = model_name if len(parts) == 2 else parts[2]
        try:
            # Dynamically import the azure openai model initializer
            from recipe_executor.llm_utils.azure_openai import get_openai_model as get_azure_openai_model
        except ImportError as e:
            raise ImportError("Azure OpenAI support is not available. Ensure llm_utils/azure_openai.py exists and is accessible.") from e
        return get_azure_openai_model(model_name, deployment_name)
    elif provider == "openai":
        return OpenAIModel(model_name)
    elif provider == "anthropic":
        return AnthropicModel(model_name)
    elif provider == "gemini":
        return GeminiModel(model_name)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")



def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model using structured output.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
                                    If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests.
    """
    if not model_id:
        model_id = "openai:gpt-4o"
    model_instance = get_model(model_id)
    agent = Agent(model_instance, result_type=FileGenerationResult)
    return agent



def call_llm(prompt: str, model: Optional[str] = None, logger: Optional[logging.Logger] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name' (or with deployment for Azure).
                               If None, defaults to 'openai:gpt-4o'.
        logger (Optional[logging.Logger]): Logger instance; if None, a default logger named "RecipeExecutor" is used.

    Returns:
        FileGenerationResult: The structured result containing files and commentary.

    Raises:
        Exception: If model configuration is invalid or the LLM call fails.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    if not model:
        model = "openai:gpt-4o"

    agent = get_agent(model)

    logger.debug(f"LLM Request Payload: prompt={prompt}, model={model}")
    start_time = time.time()
    try:
        result = agent.run_sync(prompt)
    except Exception as e:
        logger.exception(f"LLM call failed for model {model} with prompt: {prompt}")
        raise e
    elapsed = time.time() - start_time
    logger.info(f"Model '{model}' executed in {elapsed:.2f} seconds")
    logger.debug(f"LLM Response Payload: {result.all_messages()}")

    # Return the result data (structured FileGenerationResult)
    return result.data


=== File: recipe_executor/llm_utils/azure_openai.py ===
import os
import logging
from typing import Optional

import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Import PydanticAI models for OpenAI
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_openai_model(
    model_name: str,
    deployment_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance for Azure OpenAI, configured from environment variables.

    Environment Variables:
      - AZURE_OPENAI_ENDPOINT: Required. The endpoint for the Azure OpenAI resource.
      - AZURE_OPENAI_API_VERSION: Optional. Defaults to '2024-07-01-preview'.
      - AZURE_USE_MANAGED_IDENTITY: Set to 'true' to use Managed Identity authentication.
      - AZURE_MANAGED_IDENTITY_CLIENT_ID: Optional. Client ID for a user-assigned managed identity.
      - AZURE_OPENAI_API_KEY: Required if not using managed identity.

    Args:
      model_name: The name of the model to use (e.g. "gpt-4o").
      deployment_name: Optional deployment name; defaults to model_name if not provided.
      logger: An optional logger to log creation info.

    Returns:
      An instance of OpenAIModel configured for Azure OpenAI.

    Raises:
      ValueError: If critical environment variables are missing.
    """
    if logger is None:
        logger = logging.getLogger("RecipeExecutor")

    # Read required configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        raise ValueError("Environment variable AZURE_OPENAI_ENDPOINT is required.")

    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
    deployment = deployment_name if deployment_name else model_name

    use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"

    if use_managed_identity:
        # Use Azure Identity via DefaultAzureCredential
        client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
        # If a client id is provided, pass it to DefaultAzureCredential
        if client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
        else:
            credential = DefaultAzureCredential()

        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        try:
            azure_client = openai.AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                azure_ad_token_provider=token_provider,
                azure_deployment=deployment
            )
        except Exception as e:
            logger.error("Error creating AzureOpenAI client with managed identity: %s", str(e))
            raise
    else:
        # Use API Key authentication
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY must be provided if not using managed identity.")
        try:
            azure_client = openai.AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                azure_deployment=deployment
            )
        except Exception as e:
            logger.error("Error creating AzureOpenAI client with API key: %s", str(e))
            raise

    # Create a PydanticAI OpenAIModel instance using the OpenAIProvider
    try:
        provider = OpenAIProvider(openai_client=azure_client)
        openai_model = OpenAIModel(
            model_name=model_name,
            provider=provider
        )
    except Exception as e:
        logger.error("Error creating PydanticAI OpenAIModel: %s", str(e))
        raise

    logger.info("Azure OpenAI model created with endpoint %s and deployment %s", azure_endpoint, deployment)
    return openai_model


=== File: recipe_executor/logger.py ===
import logging
import os
import sys


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
    # Create log directory if it does not exist
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise Exception(f"Failed to create log directory '{log_dir}': {e}")

    # Create a logger with a consistent name
    logger = logging.getLogger("RecipeExecutor")
    logger.setLevel(logging.DEBUG)  # Set lowest level to capture all messages

    # Remove existing handlers, if any, to avoid duplicate logs in re-initializations
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define log format
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Setup file handlers and ensure logs are cleared (mode="w")
    try:
        # Debug file: logs everything (DEBUG and above)
        debug_file = os.path.join(log_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_file, mode="w")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)

        # Info file: logs info and above
        info_file = os.path.join(log_dir, "info.log")
        info_handler = logging.FileHandler(info_file, mode="w")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        # Error file: logs error and above
        error_file = os.path.join(log_dir, "error.log")
        error_handler = logging.FileHandler(error_file, mode="w")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
    except Exception as e:
        raise Exception(f"Failed to set up file handlers: {e}")

    # Console handler: logs info and above to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger


=== File: recipe_executor/main.py ===
import argparse
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from executor import RecipeExecutor

from recipe_executor.context import Context
from recipe_executor.logger import init_logger


def parse_context(context_args: List[str]) -> Dict[str, Any]:
    """
    Parse context key=value pairs from the CLI arguments.

    Args:
        context_args: List of context arguments as key=value strings.

    Returns:
        A dictionary with key-value pairs parsed from the arguments.

    Raises:
        ValueError: If any argument does not follow key=value format.
    """
    context: Dict[str, Any] = {}
    for arg in context_args:
        if "=" not in arg:
            raise ValueError(f"Invalid context argument '{arg}'. Expected format: key=value")
        key, value = arg.split("=", 1)
        if not key:
            raise ValueError(f"Empty key in context argument '{arg}'.")
        context[key] = value
    return context


def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    This function parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    It also handles errors and provides appropriate exit codes.
    """
    # Load environment variables from .env file
    load_dotenv()

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

    # Initialize logging
    logger = init_logger(args.log_dir)
    logger.info("Starting Recipe Executor Tool")

    # Create the Context object with CLI-supplied artifacts
    context = Context(artifacts=cli_context)

    try:
        # Execute the recipe
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
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """
    path: str
    content: str


class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """
    files: List[FileSpec]
    commentary: Optional[str] = None


class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict[str, Any]): Dictionary containing configuration for the step.
    """
    type: str
    config: Dict[str, Any]


class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep]


=== File: recipe_executor/steps/__init__.py ===
# __init__.py

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

# Explicitly populate the registry
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
    Base class for all step configurations. Extend this class to add custom configuration fields.
    """

    pass


# Type variable for generic configuration types, bound to StepConfig
ConfigType = TypeVar("ConfigType", bound=StepConfig)


class BaseStep(ABC, Generic[ConfigType]):
    """
    Abstract base class for all steps. Subclasses should implement the execute method.

    Attributes:
        config (ConfigType): The configuration for the step, validated via Pydantic.
        logger (logging.Logger): Logger instance for logging messages during execution.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.logger = logger or logging.getLogger("RecipeExecutor")
        if not self.logger.handlers:
            # Basic handler setup if no handlers are present, ensuring logging output
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @abstractmethod
    def execute(self, context: Context) -> None:
        """
        Execute the step using a provided context.

        Args:
            context (Context): Shared context object carrying data between steps.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")


=== File: recipe_executor/steps/execute_recipe.py ===
import logging
import os
from typing import Any, Dict, Optional

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
    """Step for executing a sub-recipe with dynamic path rendering and context overrides.

    This step applies template rendering to both the recipe path and context overrides,
    verifies the existence of the sub-recipe file, and then uses the RecipeExecutor to execute it.
    Detailed logging is performed to track execution start and completion.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
        # Convert dict config to an instance of ExecuteRecipeConfig
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute a sub-recipe by applying context overrides, rendering the recipe path,
        and delegating execution to RecipeExecutor.

        Args:
            context (Context): Shared context between parent and sub-recipe.

        Raises:
            FileNotFoundError: If the sub-recipe file does not exist.
            Exception: Propagates exceptions from sub-recipe execution.
        """
        # Apply context overrides if specified
        if self.config.context_overrides:
            for key, value in self.config.context_overrides.items():
                rendered_value = render_template(value, context)
                context[key] = rendered_value

        # Render the sub-recipe path
        recipe_path = render_template(self.config.recipe_path, context)

        # Verify that the sub-recipe file exists
        if not os.path.exists(recipe_path):
            error_message = f"Sub-recipe file not found: {recipe_path}"
            self.logger.error(error_message)
            raise FileNotFoundError(error_message)

        # Log the start of sub-recipe execution
        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        # Execute the sub-recipe using the RecipeExecutor
        try:
            executor = RecipeExecutor()
            executor.execute(recipe=recipe_path, context=context, logger=self.logger)
        except Exception as e:
            self.logger.error(f"Error executing sub-recipe '{recipe_path}': {e}")
            raise

        # Log the completion of sub-recipe execution
        self.logger.info(f"Completed sub-recipe: {recipe_path}")


=== File: recipe_executor/steps/generate_llm.py ===
import logging
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.llm import call_llm
from recipe_executor.steps.base import BaseStep, StepConfig
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
    """Component that generates content using a Large Language Model (LLM)."""

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the configuration dictionary to the GenerateLLMConfig type
        super().__init__(GenerateLLMConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the generate step:
          - Render the artifact key if templated
          - Render the prompt and model using the context
          - Call the LLM with the rendered prompt and model
          - Store the generation result in the context under the resolved artifact key

        Args:
            context (Context): The execution context containing artifacts and variables.

        Raises:
            ValueError: If template rendering fails.
            RuntimeError: If LLM call fails.
        """
        # Process artifact key rendering
        artifact_key = self.config.artifact
        try:
            if "{{" in artifact_key and "}}" in artifact_key:
                artifact_key = render_template(artifact_key, context)
        except Exception as e:
            self.logger.error("Error rendering artifact key '%s': %s", self.config.artifact, e)
            raise ValueError(f"Error rendering artifact key: {e}")

        # Render prompt and model using the current context
        try:
            rendered_prompt = render_template(self.config.prompt, context)
            rendered_model = render_template(self.config.model, context)
        except Exception as e:
            self.logger.error("Error rendering prompt or model: %s", e)
            raise ValueError(f"Error rendering templates: {e}")

        # Log LLM call initiation
        self.logger.info("Calling LLM with prompt for artifact: %s", artifact_key)

        # Call the LLM and handle potential failures
        try:
            response = call_llm(rendered_prompt, rendered_model)
        except Exception as e:
            self.logger.error("LLM call failed for model '%s' with prompt '%s': %s", rendered_model, rendered_prompt, e)
            raise RuntimeError(f"LLM call failed: {e}")

        # Store the result in context under the resolved artifact key
        context[artifact_key] = response
        self.logger.debug("LLM response stored in context under '%s'", artifact_key)


=== File: recipe_executor/steps/parallel.py ===
import time
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Any, Dict, List

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.context import Context

from pydantic import BaseModel


class ParallelConfig(StepConfig, BaseModel):
    """Config for ParallelStep.

    Fields:
        substeps: List of sub-step configurations to execute in parallel. Each substep must be defined as an execute_recipe step.
        max_concurrency: Maximum number of substeps to run concurrently. Default of 0 means no explicit limit.
        delay: Optional delay (in seconds) between launching each substep. Default is 0.
    """
    substeps: List[Dict[str, Any]]
    max_concurrency: int = 0
    delay: float = 0.0


class ParallelStep(BaseStep[ParallelConfig]):
    """ParallelStep executes multiple sub-recipes concurrently in isolated contexts.

    It clones the current context for each substep, launches them in a ThreadPoolExecutor, and enforces fail-fast behavior.
    """
    def __init__(self, config: dict, logger: Any = None) -> None:
        # Initialize configuration via Pydantic validation
        super().__init__(ParallelConfig(**config), logger)

    def execute(self, context: Context) -> None:
        self.logger.info("Starting ParallelStep execution with {} substeps.".format(len(self.config.substeps)))

        substeps = self.config.substeps
        total_substeps = len(substeps)

        # Determine max_workers: if max_concurrency is set (>0), use it, otherwise allow all substeps concurrently.
        max_workers = self.config.max_concurrency if self.config.max_concurrency > 0 else total_substeps
        futures: Dict[Future, int] = {}
        exception_occurred = False
        first_exception = None
        failed_index = None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit substeps one by one, obeying delay and fail-fast policy
            for index, substep_config in enumerate(substeps):
                if exception_occurred:
                    self.logger.info(f"Aborting submission of substep {index} due to a previous error.")
                    break

                # Clone the context for isolation
                cloned_context = context.clone()

                # Resolve and instantiate the sub-step from the registry
                step_type = substep_config.get("type")
                if step_type not in STEP_REGISTRY:
                    raise ValueError(f"Substep at index {index} has unregistered type: {step_type}")

                step_cls = STEP_REGISTRY[step_type]
                try:
                    step_instance = step_cls(substep_config, self.logger)
                except Exception as e:
                    self.logger.error(f"Failed to instantiate substep at index {index}: {e}")
                    raise

                self.logger.info(f"Submitting substep {index} of type '{step_type}'.")
                future = executor.submit(step_instance.execute, cloned_context)
                futures[future] = index

                # If a delay is configured, wait before launching the next one
                if self.config.delay > 0 and index < total_substeps - 1:
                    time.sleep(self.config.delay)

            # Process futures as they complete
            try:
                for future in as_completed(futures):
                    index = futures[future]
                    try:
                        future.result()
                        self.logger.info(f"Substep {index} completed successfully.")
                    except Exception as e:
                        self.logger.error(f"Substep {index} failed with error: {e}")
                        exception_occurred = True
                        first_exception = e
                        failed_index = index
                        # Fail fast: attempt to cancel any futures that haven't started
                        for pending_future in futures:
                            if not pending_future.done():
                                pending_future.cancel()
                        # Break out of the loop as soon as one error is encountered
                        break
            except Exception as overall_exception:
                # If there was an exception while collecting results
                self.logger.error(f"Exception during parallel execution: {overall_exception}")
                raise overall_exception

        if exception_occurred:
            raise RuntimeError(f"ParallelStep aborted because substep {failed_index} failed: {first_exception}")

        self.logger.info("All parallel substeps completed successfully.")


=== File: recipe_executor/steps/read_file.py ===
import logging
import os
from typing import Optional

from recipe_executor.context import Context
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Attributes:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found. Defaults to False.
    """

    path: str
    artifact: str
    optional: bool = False


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    Step that reads a file from the filesystem using a template-resolved path and stores its contents in the execution context.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert dict to ReadFileConfig using Pydantic validation
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the file reading step.

        This method resolves the file path from the provided template, reads its content if file exists,
        and stores the content into the given execution context under the specified artifact key.
        If the file is marked as optional and not found, it logs a warning and stores an empty string.

        Args:
            context (Context): The shared execution context.

        Raises:
            FileNotFoundError: If the file is not found and the step is not marked as optional.
            Exception: Re-raises any exceptions encountered while reading the file.
        """
        # Render the file path using the current context
        rendered_path: str = render_template(self.config.path, context)

        # Check file existence
        if not os.path.exists(rendered_path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {rendered_path}, continuing with empty content")
                context[self.config.artifact] = ""
                return
            else:
                raise FileNotFoundError(f"ReadFileStep: file not found at path: {rendered_path}")

        self.logger.info(f"Reading file from: {rendered_path}")
        try:
            with open(rendered_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as exc:
            self.logger.error(f"Error reading file at path: {rendered_path}. Exception: {exc}")
            raise

        # Store the file content in the context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")


=== File: recipe_executor/steps/registry.py ===
from typing import Dict, Type

from recipe_executor.steps.base import BaseStep

# Global dictionary for mapping step type names to their implementation classes
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {}


def register_step(step_type: str, step_class: Type[BaseStep]) -> None:
    """
    Register a new step implementation.

    Args:
        step_type (str): The unique name for the step type.
        step_class (Type[BaseStep]): The class implementing the step.

    Raises:
        ValueError: If the step type is already registered.
    """
    if step_type in STEP_REGISTRY:
        raise ValueError(f"Step type '{step_type}' is already registered.")
    STEP_REGISTRY[step_type] = step_class


def get_registered_step(step_type: str) -> Type[BaseStep]:
    """
    Retrieve a registered step class by its type name.

    Args:
        step_type (str): The unique name for the step type.

    Returns:
        Type[BaseStep]: The class implementing the step.

    Raises:
        ValueError: If the step type is not registered.
    """
    try:
        return STEP_REGISTRY[step_type]
    except KeyError:
        raise ValueError(f"Unknown step type '{step_type}'.")


=== File: recipe_executor/steps/write_files.py ===
import logging
import os
from typing import List, Optional

from recipe_executor.context import Context
from recipe_executor.models import FileGenerationResult, FileSpec
from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.utils import render_template


class WriteFilessConfig(StepConfig):
    """
    Config for WriteFilesStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to '.'
    """

    artifact: str
    root: str = "."


class WriteFilesStep(BaseStep[WriteFilessConfig]):
    """
    Step that writes files to disk based on the provided artifact in the context.
    The artifact can be either a FileGenerationResult or a list of FileSpec objects.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize configuration using WriteFilessConfig
        super().__init__(WriteFilessConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the step: write files to disk by resolving paths using template rendering and
        creating directories as needed.

        Args:
            context (Context): Execution context containing artifacts and configuration.

        Raises:
            ValueError: If no artifact is found in the context.
            TypeError: If the artifact is not of an expected type.
            IOError: If file writing fails.
        """
        # Retrieve artifact from context
        data = context.get(self.config.artifact)

        if data is None:
            raise ValueError(f"No artifact found at key: {self.config.artifact}")

        # Determine file list based on artifact type
        if isinstance(data, FileGenerationResult):
            files: List[FileSpec] = data.files
        elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
            files = data
        else:
            raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

        # Render output root using the context to resolve any template variables
        output_root = render_template(self.config.root, context)

        # Process each file in the file list
        for file in files:
            # Render the relative file path from template variables
            rel_path = render_template(file.path, context)
            full_path = os.path.join(output_root, rel_path)

            # Create parent directories if they do not exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Failed to create directory {parent_dir}: {e}")
                    raise IOError(f"Error creating directory {parent_dir}: {e}")

            # Write file content to disk
            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file.content)
                self.logger.info(f"Wrote file: {full_path}")
            except Exception as e:
                self.logger.error(f"Failed to write file {full_path}: {e}")
                raise IOError(f"Error writing file {full_path}: {e}")


=== File: recipe_executor/utils.py ===
from typing import Any

from liquid import Template

from recipe_executor.context import Context


def _convert_values_to_str(value: Any) -> Any:
    """
    Recursively convert all values in the provided data structure to strings.

    Args:
        value: The input value, which may be a dict, list, or primitive.

    Returns:
        The data structure with all values converted to strings.
    """
    if isinstance(value, dict):
        return {k: _convert_values_to_str(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_convert_values_to_str(item) for item in value]
    else:
        return str(value)


def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
    try:
        # Get artifacts from the context and convert all values to strings
        raw_context = context.as_dict()
        str_context = _convert_values_to_str(raw_context)

        # Create and render the Liquid template with the provided context
        template = Template(text)
        rendered_text = template.render(**str_context)
        return rendered_text
    except Exception as e:
        raise ValueError(f"Template rendering failed: {e}") from e


