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
#AZURE_OPENAI_API_KEY=
#AZURE_USE_MANAGED_IDENTITY=false

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

## Quick Start

Get started with Recipe Executor in minutes:

### Simple Example

Run a basic code generation recipe:

```bash
python recipe_executor/main.py recipes/example_simple/test_recipe.md
```

This generates a simple Python script based on a specification. See [Simple Example README](/recipes/example_simple/README.md) for details.

### Complex Example

Try a more advanced multi-step workflow:

```bash
python recipe_executor/main.py recipes/example_complex/complex_recipe.md
```

This demonstrates multiple specifications and sub-recipes. See [Complex Example README](/recipes/example_complex/README.md) for details.

### Creating Your Own Project

For real projects, use the blueprint generator to create a complete component structure:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=your_spec.md \
  --context component_id=your_component \
  --context target_project=your_project
```

### Running Any Recipe

Execute a recipe using the command line interface:

```bash
python recipe_executor/main.py path/to/your/recipe.json
```

You can also pass context variables:

```bash
python recipe_executor/main.py path/to/your/recipe.json --context key=value
```

For comprehensive documentation, see the [User Guide](/docs/user_guide.md).

## Project Structure

The project contains:

- **`recipe_executor/`**: Core implementation with modules for execution, context management, and steps
- **`recipes/`**: Recipe definition files that can be executed
- **Implementation Philosophy**: Code follows a minimalist, functionally-focused approach with clear error handling

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
from typing import Any, Dict, Iterator, Optional


class Context:
    """
    The Context component is a shared state container for the Recipe Executor system.
    It provides a dictionary-like interface for storing and retrieving artifacts during recipe execution.

    Attributes:
        config (Dict[str, Any]): Configuration values.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store.
            config: Configuration values.
        """
        # Copy input dictionaries to avoid external modifications
        self._artifacts: Dict[str, Any] = artifacts.copy() if artifacts is not None else {}
        self.config: Dict[str, Any] = config.copy() if config is not None else {}

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-like setting of artifacts."""
        self._artifacts[key] = value

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to artifacts. Raises KeyError if the key does not exist."""
        if key not in self._artifacts:
            raise KeyError(f"Artifact with key '{key}' does not exist.")
        return self._artifacts[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get an artifact with an optional default value."""
        return self._artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in artifacts."""
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """Iterate over artifact keys."""
        return iter(self._artifacts)

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of artifacts."""
        return iter(self._artifacts.keys())

    def __len__(self) -> int:
        """Return the number of artifacts stored in the context."""
        return len(self._artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """Return a copy of the artifacts as a dictionary to ensure immutability."""
        return self._artifacts.copy()


=== File: recipe_executor/executor.py ===
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY


class RecipeExecutor:
    """
    RecipeExecutor is the central orchestration mechanism for the Recipe Executor system.
    It loads and executes recipes from various input formats sequentially using a provided context.
    """

    def __init__(self) -> None:
        # Stateless design; no initialization required
        pass

    def execute(
        self,
        recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        context: Context,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Execute a recipe with the provided context.

        Args:
            recipe: Recipe to execute. It can be a file path, a JSON string, a dict, or a list of step dicts.
            context: Context instance to use for execution.
            logger: Optional logger to use, defaults to a simple console logger if not provided.

        Raises:
            ValueError: If the recipe format is invalid or a step execution fails.
            TypeError: If the recipe type is not supported.
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                # Set up a basic console handler if no handlers exist
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        try:
            # Parse the recipe based on its type
            recipe_data = self._load_recipe(recipe, logger)
        except Exception as e:
            msg = f"Failed to load recipe: {str(e)}"
            logger.error(msg)
            raise ValueError(msg) from e

        # Validate recipe structure - expecting either a dict with a 'steps' key or a list of steps
        steps = []
        if isinstance(recipe_data, dict):
            if "steps" not in recipe_data:
                msg = "Recipe dictionary must have a 'steps' key."
                logger.error(msg)
                raise ValueError(msg)
            steps = recipe_data["steps"]
        elif isinstance(recipe_data, list):
            steps = recipe_data
        else:
            msg = f"Unsupported recipe format: {type(recipe_data)}."
            logger.error(msg)
            raise TypeError(msg)

        if not isinstance(steps, list):
            msg = "'steps' should be a list of step definitions."
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"Executing recipe with {len(steps)} steps.")

        # Execute each step sequentially
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                msg = f"Step at index {index} is not a dictionary."
                logger.error(msg)
                raise ValueError(msg)

            if "type" not in step:
                msg = f"Step at index {index} is missing the 'type' field."
                logger.error(msg)
                raise ValueError(msg)

            step_type = step["type"]
            if step_type not in STEP_REGISTRY:
                msg = f"Unknown step type '{step_type}' at index {index}."
                logger.error(msg)
                raise ValueError(msg)

            step_class = STEP_REGISTRY[step_type]
            try:
                logger.info(f"Executing step {index + 1}/{len(steps)}: {step_type}")
                step_instance = step_class(step, logger)
                step_instance.execute(context)
            except Exception as e:
                msg = f"Error executing step {index} (type: {step_type}): {str(e)}"
                logger.error(msg)
                raise ValueError(msg) from e

        logger.info("Recipe execution completed successfully.")

    def _load_recipe(
        self, recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]], logger: logging.Logger
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load and parse the recipe from various formats:

        - If recipe is a path to a file, load its content.
        - If the file is markdown, extract JSON from fenced code blocks.
        - If recipe is a JSON string, parse it.
        - If recipe is already a dict or list, return it directly.
        """
        logger.info(f"Loading recipe from: {recipe}")

        # If recipe is a dict or list, return it directly
        if isinstance(recipe, (dict, list)):
            return recipe

        if isinstance(recipe, str):
            # If the string is a path to an existing file, load file content
            if os.path.exists(recipe) and os.path.isfile(recipe):
                try:
                    with open(recipe, "r", encoding="utf-8") as file:
                        content = file.read()
                        logger.info(f"Loaded recipe from file: {recipe}")
                except Exception as e:
                    raise ValueError(f"Failed to read recipe file '{recipe}': {str(e)}") from e

                # Check if it's a markdown file by extension
                if recipe.lower().endswith(".md"):
                    # Extract JSON from markdown fenced code blocks
                    json_content = self._extract_json_from_markdown(content)
                    if json_content is None:
                        raise ValueError("No JSON code block found in markdown recipe.")
                    content = json_content

                # Parse the content as JSON
                try:
                    return json.loads(content)
                except Exception as e:
                    raise ValueError(f"Invalid JSON in recipe file '{recipe}': {str(e)}") from e
            else:
                # Try to parse the string directly as JSON
                try:
                    return json.loads(recipe)
                except Exception as e:
                    raise ValueError(f"Invalid recipe format string: {str(e)}") from e

        # Unsupported recipe type
        raise TypeError(f"Recipe type {type(recipe)} is not supported.")

    def _extract_json_from_markdown(self, content: str) -> Optional[str]:
        """
        Extract the first JSON fenced code block from a markdown string.

        Returns:
            The JSON string if found, otherwise None.
        """
        # Regex to match fenced code block with json language indicator
        pattern = r"```json\s*(.*?)\s*```"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None


=== File: recipe_executor/llm.py ===
import logging
import os
import time
from typing import Optional

# Import Azure identity and AsyncAzureOpenAI if available
try:
    from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
except ImportError:
    DefaultAzureCredential = None
    ManagedIdentityCredential = None

try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None

# Import Agent from Pydantic AI and the FileGenerationResult for structured output
from pydantic_ai import Agent
from recipe_executor.models import FileGenerationResult


def get_model(model_id: str):
    """
    Initialize and return an LLM model based on a colon-separated identifier.
    Supported formats:
      - openai:model_name
      - anthropic:model_name
      - gemini:model_name
      - azure:model_name or azure:model_name:deployment_name
    """
    parts = model_id.split(":")
    if len(parts) < 2:
        raise ValueError("Invalid model identifier. Expected format 'provider:model_name[:deployment_name]'")
    
    provider = parts[0].lower()

    if provider == "openai":
        if len(parts) != 2:
            raise ValueError("Invalid format for OpenAI model. Expected 'openai:model_name'")
        from pydantic_ai.models.openai import OpenAIModel
        return OpenAIModel(parts[1])

    elif provider == "anthropic":
        if len(parts) != 2:
            raise ValueError("Invalid format for Anthropic model. Expected 'anthropic:model_name'")
        from pydantic_ai.models.anthropic import AnthropicModel
        return AnthropicModel(parts[1])

    elif provider == "gemini":
        if len(parts) != 2:
            raise ValueError("Invalid format for Gemini model. Expected 'gemini:model_name'")
        from pydantic_ai.models.gemini import GeminiModel
        return GeminiModel(parts[1])

    elif provider == "azure":
        # Azure supports either azure:model_name or azure:model_name:deployment_name, but deployment is handled via model parameter
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.azure import AzureProvider

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("OPENAI_API_VERSION")
        if not azure_endpoint or not api_version:
            raise ValueError("Missing required environment variables: AZURE_OPENAI_ENDPOINT and OPENAI_API_VERSION")

        if len(parts) == 2:
            model_name = parts[1]
        elif len(parts) == 3:
            model_name = parts[1]  # deployment name provided as parts[2] is ignored because AzureProvider does not accept deployment_name
        else:
            raise ValueError("Invalid format for Azure model. Expected 'azure:model_name' or 'azure:model_name:deployment_name'")

        use_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
        if use_managed_identity:
            if DefaultAzureCredential is None:
                raise ImportError("azure-identity package is required for managed identity authentication")
            client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
            if client_id:
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                credential = DefaultAzureCredential()

            if AsyncAzureOpenAI is None:
                raise ImportError("openai package with AsyncAzureOpenAI is required for Azure managed identity support")

            # Mandatory token scope for managed identity
            def get_bearer_token_provider():
                scope = "https://cognitiveservices.azure.com/.default"
                token = credential.get_token(scope)
                return token.token

            custom_client = AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                azure_ad_token_provider=get_bearer_token_provider
            )
            provider_instance = AzureProvider(openai_client=custom_client)
        else:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Missing environment variable AZURE_OPENAI_API_KEY for Azure authentication")
            provider_instance = AzureProvider(
                azure_endpoint=azure_endpoint,
                api_version=api_version,
                api_key=api_key
            )
        
        return OpenAIModel(model_name, provider=provider_instance)

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initializes and returns an Agent configured with a standardized system prompt for file generation.
    Defaults to 'openai:gpt-4o' if no model_id is provided.
    """
    if model_id is None:
        model_id = "openai:gpt-4o"
    model = get_model(model_id)
    system_prompt = (
        "Generate a JSON object with exactly two keys: 'files' and 'commentary'. "
        "The 'files' key should be an array of objects, each with 'path' and 'content' properties. "
        "The 'commentary' field is optional. "
        "Return your output strictly in JSON format."
    )

    return Agent(
        model=model,
        result_type=FileGenerationResult,
        system_prompt=system_prompt,
        retries=3
    )


def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Calls the LLM with the given prompt and optional model identifier, logging the execution time,
    and returns a FileGenerationResult. Basic error handling and retry logic is implemented.
    """
    logger = logging.getLogger("RecipeExecutor.LLM")
    logger.debug(f"LLM call started with prompt: {prompt}")
    start_time = time.time()
    try:
        agent_instance = get_agent(model)
        result = agent_instance.run_sync(prompt)
    except Exception as e:
        logger.error("Error during LLM call", exc_info=True)
        raise e
    elapsed = time.time() - start_time
    logger.debug(f"LLM call finished in {elapsed:.2f} seconds")
    logger.debug(f"LLM response: {result.data}")
    return result.data


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
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


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


class ReadFileConfig(BaseModel):
    """
    Configuration for a ReadFile step.

    Attributes:
        file_path (str): The path of the file to read.
        store_key (str): Key under which to store the file content. Defaults to "spec".
    """
    file_path: str
    store_key: str = "spec"


class GenerateCodeConfig(BaseModel):
    """
    Configuration for a GenerateCode step.

    Attributes:
        input_key (str): Key in context where the specification is stored. Defaults to "spec".
        output_key (str): Key to store the generated code result. Defaults to "codegen_result".
    """
    input_key: str = "spec"
    output_key: str = "codegen_result"


class WriteFileConfig(BaseModel):
    """
    Configuration for a WriteFile step.

    Attributes:
        input_key (str): Key in context where the codegen result is stored. Defaults to "codegen_result".
        output_root (str): Root directory where files will be written.
    """
    input_key: str = "codegen_result"
    output_root: str


class RecipeStep(BaseModel):
    """
    A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """
    type: str
    config: Dict


class Recipe(BaseModel):
    """
    A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """
    steps: List[RecipeStep]


class AzureOpenAISettings(BaseSettings):
    """
    Configuration model for Azure OpenAI services.

    This model supports configuring Azure OpenAI using either an API key or managed identity.

    Attributes:
        endpoint (str): The Azure OpenAI endpoint URL, mapped from environment variable AZURE_OPENAI_ENDPOINT.
        openai_api_version (str): API version to use, mapped from environment variable OPENAI_API_VERSION.
        api_key (Optional[str]): API key for authentication when not using managed identity, mapped from AZURE_OPENAI_API_KEY.
        use_managed_identity (bool): Flag for managed identity auth, defaults to False, mapped from AZURE_USE_MANAGED_IDENTITY.
        managed_identity_client_id (Optional[str]): Specific managed identity client ID, mapped from AZURE_MANAGED_IDENTITY_CLIENT_ID.
    """
    endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    openai_api_version: str = Field(..., env="OPENAI_API_VERSION")
    api_key: Optional[str] = Field(None, env="AZURE_OPENAI_API_KEY")
    use_managed_identity: bool = Field(False, env="AZURE_USE_MANAGED_IDENTITY")
    managed_identity_client_id: Optional[str] = Field(None, env="AZURE_MANAGED_IDENTITY_CLIENT_ID")

    @validator('api_key', always=True)
    def validate_authentication(cls, v, values):
        """
        Validates that either an API key is provided or managed identity is enabled.

        Raises:
            ValueError: If API key is not provided when managed identity is not used.
        """
        use_managed_identity = values.get('use_managed_identity', False)
        if not use_managed_identity and not v:
            raise ValueError("Authentication configuration error: API key must be provided when managed identity is not used.")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


=== File: recipe_executor/steps/__init__.py ===
# __init__.py

from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFileStep

# Explicitly populate the registry
STEP_REGISTRY.update({
    "read_file": ReadFileStep,
    "write_file": WriteFileStep,
    "generate": GenerateWithLLMStep,
    "execute_recipe": ExecuteRecipeStep,
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


class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Attributes:
        artifact (str): Name of the context key holding a FileGenerationResult or List[FileSpec].
        root (str): Optional base path to prepend to all output file paths. Defaults to '.'
    """

    artifact: str
    root: str = "."


class WriteFileStep(BaseStep[WriteFilesConfig]):
    """
    Step that writes files to disk based on the provided artifact in the context.
    The artifact can be either a FileGenerationResult or a list of FileSpec objects.
    """

    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Initialize configuration using WriteFilesConfig
        super().__init__(WriteFilesConfig(**config), logger)

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


