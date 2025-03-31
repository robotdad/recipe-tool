=== File: recipes/recipe_executor/build_component.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/specs{{component_path}}/{{component_id}}.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs{{component_path}}/{{component_id}}.md",
      "artifact": "usage_doc",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "openai:o3-mini",
        "output_root": "output",
        "output_path": "recipe_executor{{component_path}}",
        "language": "python",
        "spec": "{{spec}}",
        "usage_doc": "{{usage_doc}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "{{additional_content}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/context_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/logger_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/models_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/utils_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/llm_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/executor_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/main_create.json"
    }
  ]
}


=== File: recipes/recipe_executor/docs/context.md ===
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
```

## Initialization

The Context can be initialized with optional artifacts and configuration:

```python
# Method signature
def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the Context with optional artifacts and configuration.

    Args:
        artifacts: Initial artifacts to store
        config: Configuration values
    """
```

Examples:

```python
# Empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"spec": "specification content"})

# With configuration
context = Context(config={"output_dir": "./output"})

# With both
context = Context(
    artifacts={"spec": "specification content"},
    config={"output_dir": "./output"}
)
```

## Core API

### Storing Values

```python
def __setitem__(self, key: str, value: Any) -> None:
    """Dictionary-like setting of artifacts."""
    self._artifacts[key] = value

# Usage example
context["key"] = value
```

### Retrieving Values

```python
def __getitem__(self, key: str) -> Any:
    """Dictionary-like access to artifacts."""
    if key not in self._artifacts:
        raise KeyError(f"Artifact with key '{key}' does not exist.")
    return self._artifacts[key]

def get(self, key: str, default: Optional[Any] = None) -> Any:
    """Get an artifact with an optional default value."""
    return self._artifacts.get(key, default)

# Usage examples
value = context["key"]  # Raises KeyError if not found
value = context.get("key", default=None)  # Returns default if not found
```

### Checking Keys

```python
def __contains__(self, key: str) -> bool:
    """Check if a key exists in artifacts."""
    return key in self._artifacts

# Usage example
if "key" in context:
    # Key exists
    pass
```

### Iteration

```python
def __iter__(self) -> Iterator[str]:
    """Iterate over artifact keys."""
    return iter(self._artifacts)

def keys(self) -> Iterator[str]:
    """Return an iterator over the keys of artifacts."""
    return iter(self._artifacts.keys())

def __len__(self) -> int:
    """Return the number of artifacts."""
    return len(self._artifacts)

# Usage examples
for key in context:
    value = context[key]
    print(f"{key}: {value}")

# Get number of artifacts
num_artifacts = len(context)
```

### Getting All Values

```python
def as_dict(self) -> Dict[str, Any]:
    """Return a copy of the artifacts as a dictionary to ensure immutability."""
    return self._artifacts.copy()

# Usage example
all_artifacts = context.as_dict()
```

### Accessing Configuration

```python
# Configuration is accessed via the config attribute
# Type: Dict[str, Any]

# Usage example
output_dir = context.config.get("output_dir", "./default")
```

## Integration with Steps

Steps receive the context in their `execute` method:

```python
def execute(self, context: Context) -> None:
    # Read from context
    input_value = context.get("input", "default")

    # Process...
    result = process(input_value)

    # Store in context
    context["output"] = result
```

## Important Notes

1. Context is mutable and shared between steps
2. Values can be of any type
3. Configuration is read-only in typical usage (but not enforced)
4. Step authors should document keys they read/write
5. Context provides no thread safety - it's designed for sequential execution


=== File: recipes/recipe_executor/docs/executor.md ===
# Executor Component Usage

## Importing

```python
from recipe_executor.executor import RecipeExecutor
```

## Basic Usage

The RecipeExecutor has a single primary method: `execute()`. This method loads and runs a recipe with a given context:

```python
# Method signature
def execute(
    self,
    recipe: Union[str, Dict[str, Any], List[Dict[str, Any]]],
    context: Context,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Execute a recipe with the given context.

    Args:
        recipe: Recipe to execute, can be a file path, JSON string, or dict
        context: Context instance to use for execution
        logger: Optional logger to use, creates a default one if not provided

    Raises:
        ValueError: If recipe format is invalid or step execution fails
        TypeError: If recipe type is not supported
    """
```

Examples:

```python
# Create context and executor
context = Context()
executor = RecipeExecutor()

# Execute a recipe from a file
executor.execute("path/to/recipe.json", context)

# Or from a JSON string
json_string = '{"steps": [{"type": "read_file", "path": "example.txt", "artifact": "content"}]}'
executor.execute(json_string, context)

# Or from a dictionary
recipe_dict: Dict[str, List[Dict[str, Any]]] = {
    "steps": [
        {"type": "read_file", "path": "example.txt", "artifact": "content"}
    ]
}
executor.execute(recipe_dict, context)
```

## Recipe Formats

The executor supports three recipe input formats:

### 1. File Path

```python
# JSON file
executor.execute("recipes/my_recipe.json", context)

# Markdown file with JSON code block
executor.execute("recipes/my_recipe.md", context)
```

### 2. JSON String

```python
json_string = '''
{
  "steps": [
    {
      "type": "read_file",
      "path": "input.txt",
      "artifact": "input_content"
    },
    {
      "type": "generate",
      "prompt": "Generate based on: {{input_content}}",
      "model": "openai:o3-mini",
      "artifact": "generation_result"
    }
  ]
}
'''
executor.execute(json_string, context)
```

### 3. Dictionary

```python
recipe: Dict[str, List[Dict[str, Any]]] = {
    "steps": [
        {
            "type": "read_file",
            "path": "input.txt",
            "artifact": "input_content"
        }
    ]
}
executor.execute(recipe, context)
```

## Custom Logging

You can provide a custom logger to the executor:

```python
import logging

logger = logging.getLogger("my_custom_logger")
logger.setLevel(logging.DEBUG)

executor.execute(recipe, context, logger=logger)
```

## Error Handling

The executor provides detailed error messages:

```python
try:
    executor.execute(recipe, context)
except ValueError as e:
    print(f"Recipe execution failed: {e}")
except TypeError as e:
    print(f"Unsupported recipe type: {e}")
```

## Integration with Steps

The executor uses the Step Registry to instantiate steps based on their type:

```python
# Each step in a recipe must have a "type" field:
step: Dict[str, Any] = {
    "type": "read_file",  # Must match a key in STEP_REGISTRY
    "path": "input.txt",
    "artifact": "content"
}
```

Steps are looked up in the STEP_REGISTRY by their type name:

```python
# Simplified example of what happens inside the executor
from recipe_executor.steps.registry import STEP_REGISTRY

step_type = step["type"]
step_class = STEP_REGISTRY[step_type]
step_instance = step_class(step, logger)
step_instance.execute(context)
```

## Important Notes

1. Recipes must contain valid steps with "type" fields
2. All step types must be registered in the STEP_REGISTRY before use
3. Each step receives the same context object
4. Execution is sequential by default


=== File: recipes/recipe_executor/docs/llm.md ===
# LLM Component Usage

## Importing

```python
from recipe_executor.llm import get_model, get_agent, call_llm
```

## Basic Usage

The LLM component provides three main functions:

### 1. Getting a Model

```python
def get_model(model_id: str) -> Any:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider:model_name'.

    Args:
        model_id (str): Model identifier in format 'provider:model_name'.
                        Example: 'openai:o3-mini', 'anthropic:claude-3.7-sonnet-latest'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai:o3-mini")

# Get an Anthropic model
anthropic_model = get_model("anthropic:claude-3.7-sonnet-latest")

# Get a Gemini model
gemini_model = get_model("gemini:gemini-pro")
```

### 2. Creating an Agent

```python
def get_agent(model_id: Optional[str] = None) -> Agent[None, FileGenerationResult]:
    """
    Initialize an LLM agent with the specified model.

    Args:
        model_id (Optional[str]): Model identifier in format 'provider:model_name'.
                                 If None, defaults to 'openai:gpt-4o'.

    Returns:
        Agent[None, FileGenerationResult]: A configured Agent ready to process LLM requests.
    """
```

Usage example:

```python
# Get default agent (openai:gpt-4o)
default_agent = get_agent()

# Get agent with specific model
custom_agent = get_agent(model_id="anthropic:claude-3-sonnet")
```

### 3. Calling an LLM

```python
def call_llm(prompt: str, model: Optional[str] = None) -> FileGenerationResult:
    """
    Call the LLM with the given prompt and return a structured FileGenerationResult.

    Args:
        prompt (str): The prompt string to be sent to the LLM.
        model (Optional[str]): The model identifier in the format 'provider:model_name'.
        If None, defaults to 'openai:gpt-4o'.

    Returns:
        FileGenerationResult: The structured result containing generated files and commentary.

    Raises:
        Exception: If LLM call fails or result validation fails.
    """
```

Usage example:

```python
# Call LLM with default model
result = call_llm("Generate a Python utility module for handling dates.")

# Call with specific model
result = call_llm(
    prompt="Create a React component for a user profile page.",
    model="openai:o3-mini"
)

# Access generated files
for file in result.files:
    print(f"File: {file.path}")
    print(file.content)

# Access commentary
if result.commentary:
    print(f"Commentary: {result.commentary}")
```

## Model ID Format

The component uses a standardized model identifier format:

```
provider:model_name
```

Supported providers:

- `openai`: OpenAI models (e.g., `openai:gpt-4o`, `openai:o3-mini`)
- `anthropic`: Anthropic models (e.g., `anthropic:claude-3.7-sonnet-latest`)
- `gemini`: Google Gemini models (e.g., `gemini:gemini-pro`)

## System Prompt

The agent is configured with a system prompt that instructs the LLM to generate a JSON object with:

1. A `files` array containing file objects with `path` and `content` properties
2. An optional `commentary` field with additional information

This ensures consistent output structure regardless of the model used.

## Error Handling

Example of error handling:

```python
try:
    result = call_llm(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Integration with Steps

The LLM component is primarily used by the GenerateWithLLMStep:

```python
# Example from GenerateWithLLMStep.execute()
def execute(self, context: Context) -> None:
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    response = call_llm(rendered_prompt, rendered_model)

    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = response
```

## Important Notes

1. Calling a model incurs API costs with the respective provider
2. OpenAI is the default provider if none is specified
3. The component logs request details at debug level
4. Responses are validated against the FileGenerationResult model
5. The agent is configured with 3 retries by default


=== File: recipes/recipe_executor/docs/logger.md ===
# Logger Component Usage

## Importing

```python
from recipe_executor.logger import init_logger
```

## Initialization

The Logger component provides a single function to initialize a configured logger:

```python
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
```

Examples:

```python
# Default usage
logger = init_logger()

# With custom log directory
logger = init_logger(log_dir="custom/log/path")
```

## Log Levels

The configured logger supports standard Python logging levels:

```python
# Debug level (to debug.log file and higher level logs)
logger.debug("Detailed information for diagnosing problems")

# Info level (to console, info.log, and error.log)
logger.info("Confirmation that things are working as expected")

# Warning level (to console, info.log, and error.log)
logger.warning("An indication that something unexpected happened")

# Error level (to console, info.log, and error.log)
logger.error("Due to a more serious problem, the software could not perform a function")

# Critical level (to all logs)
logger.critical("A serious error indicating the program itself may be unable to continue running")
```

## Log Files

The logger creates three log files:

1. `debug.log` - All messages (DEBUG and above)
2. `info.log` - INFO messages and above
3. `error.log` - ERROR messages and above

Example:

```
2025-03-30 15:42:38,927 [INFO] Starting Recipe Executor Tool
2025-03-30 15:42:38,928 [DEBUG] Initializing executor
2025-03-30 15:42:38,930 [INFO] Executing recipe: recipes/my_recipe.json
2025-03-30 15:42:38,935 [ERROR] Recipe execution failed: Invalid step type
```

## Console Output

The logger also writes INFO level and above messages to stdout:

```python
# This appears in both console and log files
logger.info("Executing step 1 of 5")

# This appears in log files only
logger.debug("Step config: {'path': 'input.txt', 'artifact': 'content'}")
```

## Integration with Other Components

The logger is typically initialized in the main component and passed to the executor:

```python
from recipe_executor.logger import init_logger
from recipe_executor.executor import RecipeExecutor

logger = init_logger(log_dir="logs")
executor = RecipeExecutor()
executor.execute(recipe_path, context, logger=logger)
```

Steps receive the logger in their constructor:

```python
class ReadFileStep(BaseStep):
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RecipeExecutor")
        # ...
```

## Important Notes

1. Logs are cleared (truncated) on each run
2. Debug logs can get large with detailed information
3. The log directory is created if it doesn't exist
4. The logger name "RecipeExecutor" is consistent across the system


=== File: recipes/recipe_executor/docs/main.md ===
# Main Component Usage

## Command-Line Interface

The Recipe Executor is used from the command line like this:

```bash
# Basic usage
python -m recipe_executor.main recipes/my_recipe.json

# With custom log directory
python -m recipe_executor.main recipes/my_recipe.json --log-dir custom_logs

# With context values
python -m recipe_executor.main recipes/my_recipe.json --context key1=value1 --context key2=value2
```

## Command-Line Arguments

The Main component supports these arguments:

1. `recipe_path` (required positional): Path to the recipe file to execute
2. `--log-dir` (optional): Directory for log files (default: "logs")
3. `--context` (optional, multiple): Context values as key=value pairs

## Context Parsing

The Main component parses context values from the command line:

```python
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
```

For example:

```bash
# These arguments:
--context name=John --context age=30 --context active=true

# Will create this context:
{
    "name": "John",
    "age": "30",
    "active": "true"
}
```

## Main Execution Flow

The main function serves as the entry point:

```python
def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    """
```

Implementation details:

```python
def main() -> None:
    """
    CLI entry point for the Recipe Executor Tool.

    Parses command-line arguments, sets up logging, creates the context, and runs the recipe executor.
    """
    # Parse command-line arguments
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
```

## Programmatic Usage

While typically used as a command-line tool, the Main component can be used programmatically:

```python
from recipe_executor.main import parse_context
from recipe_executor.context import Context
from recipe_executor.executor import RecipeExecutor
from recipe_executor.logger import init_logger

# Parse context from strings
context_args = ["name=Project", "version=1.0"]
context_dict = parse_context(context_args)

# Initialize logger
logger = init_logger("logs")

# Create context and execute recipe
context = Context(artifacts=context_dict)
executor = RecipeExecutor()
executor.execute("recipes/my_recipe.json", context, logger=logger)
```

## Exit Codes

The Main component uses these exit codes:

- `0`: Successful execution
- `1`: Error during execution (parsing errors, missing files, execution failures)

## Error Messages

Error messages are written to stderr and the log files:

```python
# Context parsing error
sys.stderr.write(f"Context Error: {str(e)}\n")

# Recipe execution error
logger.error(f"An error occurred during recipe execution: {str(e)}", exc_info=True)
```

## Important Notes

1. The recipe path must point to a valid recipe file
2. Context values from the command line are stored as strings
3. Logs are written to the specified log directory
4. All steps in the recipe share the same context
5. The executable exits with non-zero status on error


=== File: recipes/recipe_executor/docs/models.md ===
# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    FileGenerationResult,
    ReadFileConfig,
    GenerateCodeConfig,
    WriteFileConfig,
    RecipeStep,
    Recipe
)
```

## File Generation Models

### FileSpec

Represents a single file to be generated:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path (str): Relative path where the file should be written.
        content (str): The content of the file.
    """

    path: str
    content: str
```

Usage example:

```python
file = FileSpec(
    path="src/utils.py",
    content="def hello_world():\n    print('Hello, world!')"
)

# Access properties
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
```

### FileGenerationResult

Contains a collection of generated files and optional commentary:

```python
class FileGenerationResult(BaseModel):
    """Result of an LLM file generation request.

    Attributes:
        files (List[FileSpec]): List of files to generate.
        commentary (Optional[str]): Optional commentary from the LLM.
    """

    files: List[FileSpec]
    commentary: Optional[str] = None
```

Usage example:

```python
result = FileGenerationResult(
    files=[
        FileSpec(path="src/utils.py", content="def util_function():\n    pass"),
        FileSpec(path="src/main.py", content="from utils import util_function")
    ],
    commentary="Generated utility module and main script"
)

# Iterate through files
for file in result.files:
    print(f"Writing to {file.path}")
    # ... write file.content to file.path
```

## Step Configuration Models

### ReadFileConfig

Configuration for a ReadFile step:

```python
class ReadFileConfig(BaseModel):
    """Configuration for a ReadFile step.

    Attributes:
        file_path (str): The path of the file to read.
        store_key (str): Key under which to store the file content. Defaults to "spec".
    """

    file_path: str
    store_key: str = "spec"
```

Usage example:

```python
config = ReadFileConfig(
    file_path="specs/component_spec.md",
    store_key="component_spec"
)

# Use in a step definition
step = {
    "type": "read_file",
    "file_path": config.file_path,
    "store_key": config.store_key
}
```

### GenerateCodeConfig

Configuration for a GenerateCode step:

```python
class GenerateCodeConfig(BaseModel):
    """Configuration for a GenerateCode step.

    Attributes:
        input_key (str): Key in context where the specification is stored. Defaults to "spec".
        output_key (str): Key to store the generated code result. Defaults to "codegen_result".
    """

    input_key: str = "spec"
    output_key: str = "codegen_result"
```

### WriteFileConfig

Configuration for a WriteFile step:

```python
class WriteFileConfig(BaseModel):
    """Configuration for a WriteFile step.

    Attributes:
        input_key (str): Key in context where the codegen result is stored. Defaults to "codegen_result".
        output_root (str): Root directory where files will be written.
    """

    input_key: str = "codegen_result"
    output_root: str
```

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type (str): The type of the recipe step.
        config (Dict): Dictionary containing configuration for the step.
    """

    type: str
    config: Dict
```

### Recipe

Represents a complete recipe with multiple steps:

```python
class Recipe(BaseModel):
    """A complete recipe with multiple steps.

    Attributes:
        steps (List[RecipeStep]): A list containing the steps of the recipe.
    """

    steps: List[RecipeStep]
```

Usage example:

```python
from recipe_executor.models import Recipe, RecipeStep

# Create a recipe with steps
recipe = Recipe(
    steps=[
        RecipeStep(
            type="read_file",
            config={"file_path": "specs/component_spec.md", "store_key": "spec"}
        ),
        RecipeStep(
            type="generate",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "openai:o3-mini",
                "artifact": "code_result"
            }
        ),
        RecipeStep(
            type="write_file",
            config={"artifact": "code_result", "root": "./output"}
        )
    ]
)

# Validate recipe structure
recipe_dict = recipe.dict()
```

## Model Validation

All models inherit from Pydantic's BaseModel, providing automatic validation:

```python
# This will raise a validation error because path is required
try:
    FileSpec(content="File content")
except Exception as e:
    print(f"Validation error: {e}")

# This works correctly
valid_file = FileSpec(path="file.txt", content="File content")
```

## Important Notes

1. Models provide runtime validation in addition to static type checking
2. Default values are provided for common configuration options
3. Models can be converted to dictionaries with `.dict()` method
4. Models can be created from dictionaries with `Model(**dict_data)`


=== File: recipes/recipe_executor/docs/steps/base.md ===
# Steps Base Component Usage

## Importing

```python
from recipe_executor.steps.base import BaseStep, StepConfig
```

## Basic Structure

The Steps Base component provides two primary classes:

1. `StepConfig` - Base class for step configuration
2. `BaseStep` - Abstract base class for step implementations

These classes are designed to work together using generics for type safety.

## Step Configuration

All step configurations extend the `StepConfig` base class:

```python
class StepConfig(BaseModel):
    """Base class for all step configs. Extend this in each step."""
    pass

# Type variable for generic configuration types
ConfigType = TypeVar("ConfigType", bound=StepConfig)
```

Example of extending StepConfig:

```python
class ReadFileConfig(StepConfig):
    """Configuration for ReadFileStep"""
    path: str
    artifact: str
    encoding: str = "utf-8"  # With default value
```

## Base Step Class

The BaseStep is an abstract generic class parameterized by the config type:

```python
class BaseStep(Generic[ConfigType]):
    """
    Base class for all steps. Subclasses must implement `execute(context)`.
    Each step receives a config object and a logger.

    Args:
        config (ConfigType): Configuration for the step
        logger (Optional[logging.Logger]): Logger instance, defaults to "RecipeExecutor"
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")

    def execute(self, context: Context) -> None:
        """
        Execute the step with the given context.

        Args:
            context (Context): Context for execution

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Each step must implement the `execute()` method.")
```

## Implementing a Step

To implement a concrete step, create a class that:

1. Extends BaseStep with a specific config type
2. Implements the execute method
3. Takes a dictionary of configuration values in the constructor

Example:

```python
class ExampleStep(BaseStep[ExampleConfig]):
    """Example step implementation."""

    def __init__(self, config: dict, logger=None):
        # Convert dict to the appropriate config type
        super().__init__(ExampleConfig(**config), logger)

    def execute(self, context: Context) -> None:
        # Implementation specific to this step
        self.logger.info("Executing example step")

        # Access configuration values
        value = self.config.some_field

        # Do something with the context
        context["result"] = f"Processed {value}"
```

## Step Registration

All step implementations should be registered in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY

# Register the step type
STEP_REGISTRY["example_step"] = ExampleStep
```

## Handling Configuration

The base step handles configuration conversion automatically:

```python
# Step configuration in a recipe
step_config = {
    "type": "example_step",
    "some_field": "value",
    "another_field": 42
}

# In the executor
step_class = STEP_REGISTRY[step_config["type"]]
step_instance = step_class(step_config, logger)

# Configuration is validated through Pydantic
# Access in the step through self.config
```

## Logging

All steps receive a logger in their constructor:

```python
def __init__(self, config: dict, logger=None):
    # If logger is None, it defaults to logging.getLogger("RecipeExecutor")
    super().__init__(ExampleConfig(**config), logger)

def execute(self, context: Context) -> None:
    # Use the logger for various levels
    self.logger.debug("Detailed debug information")
    self.logger.info("Step execution started")
    self.logger.warning("Potential issue detected")
    self.logger.error("Error occurred during execution")
```

## Important Notes

1. All step implementations must inherit from BaseStep
2. The execute method must be implemented by all subclasses
3. Steps should validate their configuration using Pydantic models
4. Steps receive and modify a shared Context object
5. Steps should use the logger for appropriate messages


=== File: recipes/recipe_executor/docs/steps/execute_recipe.md ===
# ExecuteRecipeStep Component Usage

## Importing

```python
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep, ExecuteRecipeConfig
```

## Configuration

The ExecuteRecipeStep is configured with an ExecuteRecipeConfig:

```python
class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep.

    Fields:
        recipe_path: Path to the recipe to execute.
        context_overrides: Optional values to override in the context.
    """

    recipe_path: str
    context_overrides: Dict[str, str] = {}
```

## Step Registration

The ExecuteRecipeStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep

STEP_REGISTRY["execute_recipe"] = ExecuteRecipeStep
```

## Basic Usage in Recipes

The ExecuteRecipeStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/sub_recipe.json"
    }
  ]
}
```

## Context Overrides

You can override specific context values for the sub-recipe execution:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/generate_component.json",
      "context_overrides": {
        "component_name": "Utils",
        "output_dir": "output/components/utils"
      }
    }
  ]
}
```

## Template-Based Values

Both the recipe path and context overrides can include template variables:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/{{recipe_type}}/{{component_id}}.json",
      "context_overrides": {
        "component_name": "{{component_display_name}}",
        "output_dir": "output/components/{{component_id}}"
      }
    }
  ]
}
```

## Recipe Composition

Sub-recipes can be composed to create more complex workflows:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/project_spec.md",
      "artifact": "project_spec"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/parse_project.json",
      "context_overrides": {
        "spec": "{{project_spec}}"
      }
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/generate_components.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/assemble_project.json"
    }
  ]
}
```

## Implementation Details

The ExecuteRecipeStep works by:

1. Rendering the recipe path with the current context
2. Applying context overrides (also rendered with the current context)
3. Creating a RecipeExecutor instance
4. Executing the sub-recipe with the modified context

```python
def execute(self, context: Context) -> None:
    # Merge any context overrides into the current context
    if hasattr(self.config, "context_overrides") and self.config.context_overrides:
        for key, value in self.config.context_overrides.items():
            context[key] = render_template(value, context)

    # Render the recipe path
    recipe_path = render_template(self.config.recipe_path, context)

    # Verify recipe exists
    if not os.path.exists(recipe_path):
        raise FileNotFoundError(f"Sub-recipe file not found: {recipe_path}")

    # Log sub-recipe execution
    self.logger.info(f"Executing sub-recipe: {recipe_path}")

    # Execute the sub-recipe
    executor = RecipeExecutor()
    executor.execute(recipe=recipe_path, context=context, logger=self.logger)

    # Log completion
    self.logger.info(f"Completed sub-recipe: {recipe_path}")
```

## Error Handling

The ExecuteRecipeStep can raise several types of errors:

```python
try:
    execute_recipe_step.execute(context)
except FileNotFoundError as e:
    # Sub-recipe file not found
    print(f"File error: {e}")
except ValueError as e:
    # Recipe format or execution errors
    print(f"Recipe error: {e}")
```

## Common Use Cases

1. **Component Generation**:

   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/generate_component.json",
     "context_overrides": {
       "component_id": "utils",
       "component_name": "Utils Component"
     }
   }
   ```

2. **Template-Based Recipes**:

   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/component_template.json",
     "context_overrides": {
       "template_type": "create",
       "component_id": "{{component_id}}"
     }
   }
   ```

3. **Multi-Step Workflows**:
   ```json
   {
     "type": "execute_recipe",
     "recipe_path": "recipes/workflow/{{workflow_name}}.json"
   }
   ```

## Important Notes

1. The sub-recipe receives the same context object as the parent recipe
2. Context overrides are applied before sub-recipe execution
3. Changes made to the context by the sub-recipe persist after it completes
4. Template variables in both recipe_path and context_overrides are resolved before execution
5. Sub-recipes can execute their own sub-recipes (nested execution)


=== File: recipes/recipe_executor/docs/steps/generate_llm.md ===
# GenerateWithLLMStep Component Usage

## Importing

```python
from recipe_executor.steps.generate_llm import GenerateWithLLMStep, GenerateLLMConfig
```

## Configuration

The GenerateWithLLMStep is configured with a GenerateLLMConfig:

```python
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
```

## Step Registration

The GenerateWithLLMStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.generate_llm import GenerateWithLLMStep

STEP_REGISTRY["generate"] = GenerateWithLLMStep
```

## Basic Usage in Recipes

The GenerateWithLLMStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate Python code for a utility that: {{requirements}}",
      "model": "openai:o3-mini",
      "artifact": "generation_result"
    }
  ]
}
```

## Template-Based Prompts

The prompt can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/component_spec.md",
      "artifact": "spec"
    },
    {
      "type": "generate",
      "prompt": "You are an expert Python developer. Based on the following specification, generate code for a component:\n\n{{spec}}",
      "model": "openai:o3-mini",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Model Selection

The model identifier can also use template variables:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code based on: {{spec}}",
      "model": "{{model_provider|default:'openai'}}:{{model_name|default:'o3-mini'}}",
      "artifact": "codegen_result"
    }
  ]
}
```

## Dynamic Artifact Keys

The artifact key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "generate",
      "prompt": "Generate code for: {{component_name}}",
      "model": "openai:o3-mini",
      "artifact": "{{component_name}}_result"
    }
  ]
}
```

## Implementation Details

The GenerateWithLLMStep works by:

1. Rendering the prompt with the current context
2. Rendering the model identifier
3. Rendering the artifact key (if it contains templates)
4. Calling the LLM with the rendered prompt and model
5. Storing the result in the context under the artifact key

```python
def execute(self, context: Context) -> None:
    # Process the artifact key using templating if needed
    artifact_key = self.config.artifact
    if "{{" in artifact_key and "}}" in artifact_key:
        artifact_key = render_template(artifact_key, context)

    # Render the prompt and model with the current context
    rendered_prompt = render_template(self.config.prompt, context)
    rendered_model = render_template(self.config.model, context)

    # Call the LLM
    self.logger.info(f"Calling LLM with prompt for artifact: {artifact_key}")
    response = call_llm(rendered_prompt, rendered_model)

    # Store the LLM response in context
    context[artifact_key] = response
    self.logger.debug(f"LLM response stored in context under '{artifact_key}'")
```

## LLM Response Format

The response from call_llm is a FileGenerationResult object:

```python
# FileGenerationResult structure
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)
```

## Error Handling

The GenerateWithLLMStep can raise several types of errors:

```python
try:
    generate_step.execute(context)
except ValueError as e:
    # Template rendering or model format errors
    print(f"Value error: {e}")
except RuntimeError as e:
    # LLM call failures
    print(f"Runtime error: {e}")
```

## Common Use Cases

1. **Code Generation**:

   ```json
   {
     "type": "generate",
     "prompt": "Generate Python code for: {{specification}}",
     "model": "openai:o3-mini",
     "artifact": "code_result"
   }
   ```

2. **Content Creation**:

   ```json
   {
     "type": "generate",
     "prompt": "Write a blog post about: {{topic}}",
     "model": "anthropic:claude-3-haiku",
     "artifact": "blog_post"
   }
   ```

3. **Analysis and Transformation**:
   ```json
   {
     "type": "generate",
     "prompt": "Analyze this code and suggest improvements:\n\n{{code}}",
     "model": "openai:gpt-4o",
     "artifact": "code_analysis"
   }
   ```

## Important Notes

1. The artifact key can be dynamic using template variables
2. The prompt is rendered using the current context before sending to the LLM
3. The model identifier follows the format "provider:model_name"
4. The LLM response is a FileGenerationResult object with files and commentary
5. LLM calls may incur costs with the respective provider


=== File: recipes/recipe_executor/docs/steps/read_file.md ===
# ReadFileStep Component Usage

## Importing

```python
from recipe_executor.steps.read_file import ReadFileStep, ReadFileConfig
```

## Configuration

The ReadFileStep is configured with a ReadFileConfig:

```python
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
```

## Step Registration

The ReadFileStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_file import ReadFileStep

STEP_REGISTRY["read_file"] = ReadFileStep
```

## Basic Usage in Recipes

The ReadFileStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/component_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

## Template-Based Paths

The path can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    }
  ]
}
```

## Optional Files

You can specify that a file is optional, and execution will continue even if the file doesn't exist:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/optional_file.md",
      "artifact": "optional_content",
      "optional": true
    }
  ]
}
```

If an optional file is not found, an empty string is stored in the context.

## Implementation Details

The ReadFileStep works by:

1. Resolving the path using template rendering
2. Checking if the file exists
3. Reading the file content
4. Storing the content in the context

```python
def execute(self, context: Context) -> None:
    # Render the path using the current context
    path = render_template(self.config.path, context)

    # Check if file exists
    if not os.path.exists(path):
        if self.config.optional:
            self.logger.warning(f"Optional file not found at path: {path}, continuing anyway")
            context[self.config.artifact] = ""  # Set empty string for missing optional file
            return
        else:
            raise FileNotFoundError(f"ReadFileStep: file not found at path: {path}")

    # Read the file
    self.logger.info(f"Reading file from: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Store in context
    context[self.config.artifact] = content
    self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
```

## Error Handling

If a file doesn't exist and is not marked as optional, the step will raise a FileNotFoundError:

```python
try:
    read_file_step.execute(context)
except FileNotFoundError as e:
    print(f"File error: {e}")
    # Handle the error
```

## Common Use Cases

1. **Loading Specifications**:

   ```json
   {
     "type": "read_file",
     "path": "specs/component_spec.md",
     "artifact": "spec"
   }
   ```

2. **Loading Templates**:

   ```json
   {
     "type": "read_file",
     "path": "templates/email_template.txt",
     "artifact": "email_template"
   }
   ```

3. **Dynamic Path Resolution**:
   ```json
   {
     "type": "read_file",
     "path": "docs/{{project}}/{{component}}.md",
     "artifact": "documentation"
   }
   ```

## Important Notes

1. The step uses UTF-8 encoding by default
2. The file content is stored as a string in the context
3. Template variables in the path are resolved before reading the file
4. When a file is optional and missing, an empty string is stored


=== File: recipes/recipe_executor/docs/steps/registry.md ===
# Step Registry Component Usage

## Importing

```python
from recipe_executor.steps.registry import STEP_REGISTRY
```

## Registry Structure

The registry is a simple dictionary that maps step type names to their implementation classes:

```python
# Type definition
from typing import Dict, Type
from recipe_executor.steps.base import BaseStep

# Structure of STEP_REGISTRY
STEP_REGISTRY: Dict[str, Type[BaseStep]] = {
    "read_file": ReadFileStep,
    "write_file": WriteFileStep,
    "generate": GenerateWithLLMStep,
    "execute_recipe": ExecuteRecipeStep
}
```

## Registering Steps

Steps are typically registered in the steps package `__init__.py`:

```python
# In recipe_executor/steps/__init__.py
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_file import ReadFileStep
from recipe_executor.steps.write_files import WriteFileStep
from recipe_executor.steps.generate_llm import GenerateWithLLMStep
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep

# Register steps by updating the registry
STEP_REGISTRY.update({
    "read_file": ReadFileStep,
    "write_file": WriteFileStep,
    "generate": GenerateWithLLMStep,
    "execute_recipe": ExecuteRecipeStep
})
```

Custom steps can be registered in the same way:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.base import BaseStep
from my_custom_steps import CustomStep

# Register a custom step implementation
STEP_REGISTRY["custom_step"] = CustomStep
```

## Looking Up Steps

The executor uses the registry to look up step classes by type:

```python
# Example of registry usage in executor
from typing import Dict, Any
import logging
from recipe_executor.context import Context
from recipe_executor.steps.registry import STEP_REGISTRY

def execute_step(step: Dict[str, Any], context: Context, logger: logging.Logger) -> None:
    step_type = step["type"]
    if step_type not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type '{step_type}'")

    step_class = STEP_REGISTRY[step_type]
    step_instance = step_class(step, logger)
    step_instance.execute(context)
```

## Important Notes

1. Step type names must be unique across the entire system
2. Steps must be registered before the executor tries to use them
3. Standard steps are automatically registered when the package is imported
4. Custom steps need to be explicitly registered by the user


=== File: recipes/recipe_executor/docs/steps/write_files.md ===
# WriteFileStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFileStep, WriteFilesConfig
```

## Configuration

The WriteFileStep is configured with a WriteFilesConfig:

```python
class WriteFilesConfig(StepConfig):
    """
    Config for WriteFileStep.

    Fields:
        artifact: Name of the context key holding a FileGenerationResult or List[FileSpec].
        root: Optional base path to prepend to all output file paths.
    """

    artifact: str
    root: str = "."
```

## Step Registration

The WriteFileStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFileStep

STEP_REGISTRY["write_file"] = WriteFileStep
```

## Basic Usage in Recipes

The WriteFileStep can be used in recipes like this:

```json
{
  "steps": [
    {
      "type": "write_file",
      "artifact": "generated_code",
      "root": "output/project"
    }
  ]
}
```

## Supported Context Values

The WriteFileStep can work with two types of artifacts in the context:

### 1. FileGenerationResult

```python
from recipe_executor.models import FileGenerationResult, FileSpec

# Example of generating a FileGenerationResult
result = FileGenerationResult(
    files=[
        FileSpec(path="src/main.py", content="print('Hello, world!')"),
        FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
    ],
    commentary="Generated a simple Python project"
)

# Store in context
context["generated_code"] = result
```

### 2. List of FileSpec objects

```python
from recipe_executor.models import FileSpec

# Example of generating a list of FileSpec objects
files = [
    FileSpec(path="src/main.py", content="print('Hello, world!')"),
    FileSpec(path="src/utils.py", content="def add(a, b):\n    return a + b")
]

# Store in context
context["generated_files"] = files
```

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_file",
      "artifact": "generated_code",
      "root": "output/{{project_name}}"
    }
  ]
}
```

File paths within the FileSpec objects can also contain templates:

```python
FileSpec(
    path="{{component_name}}/{{filename}}.py",
    content="# Generated code for {{component_name}}"
)
```

## Implementation Details

The WriteFileStep works by:

1. Retrieving the artifact from the context
2. Validating it's a FileGenerationResult or list of FileSpec objects
3. Rendering the root path using template rendering
4. For each file:
   - Rendering the file path
   - Creating the necessary directories
   - Writing the file content

```python
def execute(self, context: Context) -> None:
    # Get data from context
    data = context.get(self.config.artifact)

    if data is None:
        raise ValueError(f"No artifact found at key: {self.config.artifact}")

    # Determine file list
    if isinstance(data, FileGenerationResult):
        files = data.files
    elif isinstance(data, list) and all(isinstance(f, FileSpec) for f in data):
        files = data
    else:
        raise TypeError("Expected FileGenerationResult or list of FileSpec objects")

    # Render output root
    output_root = render_template(self.config.root, context)

    # Write each file
    for file in files:
        rel_path = render_template(file.path, context)
        full_path = os.path.join(output_root, rel_path)

        # Create directories
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(file.content)

        self.logger.info(f"Wrote file: {full_path}")
```

## Error Handling

The WriteFileStep can raise several types of errors:

```python
try:
    write_step.execute(context)
except ValueError as e:
    # Missing or invalid artifact
    print(f"Value error: {e}")
except TypeError as e:
    # Unexpected artifact type
    print(f"Type error: {e}")
except IOError as e:
    # File writing errors
    print(f"I/O error: {e}")
```

## Common Use Cases

1. **Writing Generated Code**:

   ```json
   {
     "type": "write_file",
     "artifact": "generated_code",
     "root": "output/src"
   }
   ```

2. **Project-Specific Output**:

   ```json
   {
     "type": "write_file",
     "artifact": "project_files",
     "root": "output/{{project_name}}"
   }
   ```

3. **Component Generation**:
   ```json
   {
     "type": "write_file",
     "artifact": "component_result",
     "root": "output/components"
   }
   ```

## Important Notes

1. Directories are created automatically if they don't exist
2. Files are overwritten without confirmation if they already exist
3. All paths are rendered using template variables from the context
4. File content is written using UTF-8 encoding
5. Both FileGenerationResult and List[FileSpec] formats are supported


=== File: recipes/recipe_executor/docs/utils.md ===
# Utils Component Usage

## Importing

```python
from recipe_executor.utils import render_template
```

## Template Rendering

The Utils component provides a `render_template` function that renders Liquid templates using values from the Context:

```python
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
```

Basic usage example:

```python
from recipe_executor.context import Context
from recipe_executor.utils import render_template

# Create a context with values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Liquid syntax:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains dictionaries)
template = "Author: {{book.author}}"
```

### Conditionals

```python
template = "{% if user_count > 0 %}Users: {{user_count}}{% else %}No users{% endif %}"
```

### Loops

```python
template = "{% for item in items %}Item: {{item}}{% endfor %}"
```

## Type Handling

All values from the context are converted to strings before rendering:

```python
# Context with mixed types
context = Context(artifacts={
    "number": 42,
    "boolean": True,
    "list": [1, 2, 3],
    "dict": {"key": "value"}
})

# All values become strings in templates
template = "Number: {{number}}, Boolean: {{boolean}}, List: {{list}}, Dict: {{dict}}"
# Renders as: "Number: 42, Boolean: True, List: [1, 2, 3], Dict: {'key': 'value'}"
```

## Error Handling

Template rendering errors are wrapped in a ValueError:

```python
try:
    result = render_template("{% invalid syntax %}", context)
except ValueError as e:
    print(f"Template error: {e}")
    # Handle the error
```

## Common Usage Patterns

### In Step Classes

The primary use of template rendering is in step execution:

```python
# Example from ReadFileStep.execute()
def execute(self, context: Context) -> None:
    # Render the path using the current context
    path = render_template(self.config.path, context)

    # Read the file at the rendered path
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Store in context (with rendered artifact key if needed)
    artifact_key = render_template(self.config.artifact, context)
    context[artifact_key] = content
```

### In Recipe Steps

Templates are typically used in recipe step configurations:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "specs/{{component_id}}_spec.md",
      "artifact": "component_spec"
    },
    {
      "type": "generate",
      "prompt": "Generate code based on: {{component_spec}}",
      "model": "{{model_id|default:'openai:o3-mini'}}",
      "artifact": "generated_code"
    }
  ]
}
```

## Important Notes

1. All context values are converted to strings, which may affect formatting
2. Template rendering is synchronous and blocking
3. The Context's `as_dict()` method is used to access all artifacts
4. Empty or missing variables will be replaced with an empty string


=== File: recipes/recipe_executor/edit.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/context_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/logger_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/models_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/utils_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/llm_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/executor_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/main_edit.json"
    }
  ]
}


=== File: recipes/recipe_executor/recipes/context_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "context",
        "component_path": "",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/context_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/context.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/context_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/executor_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/steps/registry.md",
      "artifact": "registry_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "executor",
        "component_path": "",
        "existing_code": "{{existing_code}}",
        "additional_content": "<REGISTRY_DOCS>\n{{registry_docs}}\n</REGISTRY_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/executor_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/executor.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/executor_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/llm_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/models.md",
      "artifact": "models_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/includes/PYDANTIC_AI_DOCS.md",
      "artifact": "pydantic_ai_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "llm",
        "component_path": "",
        "existing_code": "{{existing_code}}",
        "additional_content": "<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<PYDANTIC_AI_DOCUMENTATION>\n{{pydantic_ai_docs}}\n</PYDANTIC_AI_DOCUMENTATION>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/llm_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/llm.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/llm_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/logger_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "logger",
        "component_path": "",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/logger_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/logger.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/logger_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/main_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/executor.md",
      "artifact": "executor_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/logger.md",
      "artifact": "logger_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "main",
        "component_path": "",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<EXECUTOR_DOCS>\n{{executor_docs}}\n</EXECUTOR_DOCS>\n<LOGGER_DOCS>\n{{logger_docs}}\n</LOGGER_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/main_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/main.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/main_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/models_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "models",
        "component_path": "",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/models_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/models.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/models_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/base_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/models.md",
      "artifact": "models_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "base",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/base_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/steps/base.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/base_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/registry_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/base_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/read_file_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/write_files_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/generate_llm_create.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/execute_recipe_create.json"
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/edit.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/registry_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/base_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/read_file_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/write_files_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/generate_llm_edit.json"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/execute_recipe_edit.json"
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/execute_recipe_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/steps/base.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/executor.md",
      "artifact": "executor_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/utils.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "execute_recipe",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<EXECUTOR_DOCS>\n{{executor_docs}}\n</EXECUTOR_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/execute_recipe_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/steps/execute_recipe.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/execute_recipe_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/generate_llm_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/steps/base.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/llm.md",
      "artifact": "llm_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/utils.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "generate_llm",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<LLM_DOCS>\n{{llm_docs}}\n</LLM_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/generate_llm_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/steps/generate_llm.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/generate_llm_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/read_file_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/steps/base.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/utils.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "read_file",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/read_file_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/steps/read_file.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/read_file_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/registry_create.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "registry",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/registry_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/steps/registry.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/registry_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/write_files_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/steps/base.md",
      "artifact": "steps_base_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/models.md",
      "artifact": "models_docs"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/utils.md",
      "artifact": "utils_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "write_files",
        "component_path": "/steps",
        "existing_code": "{{existing_code}}",
        "additional_content": "<STEPS_BASE_DOCS>\n{{steps_base_docs}}\n</STEPS_BASE_DOCS>\n<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>\n<MODELS_DOCS>\n{{models_docs}}\n</MODELS_DOCS>\n<UTILS_DOCS>\n{{utils_docs}}\n</UTILS_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/steps/write_files_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/steps/write_files.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/steps/write_files_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/utils_create.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs/context.md",
      "artifact": "context_docs"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/build_component.json",
      "context_overrides": {
        "component_id": "utils",
        "component_path": "",
        "existing_code": "{{existing_code}}",
        "additional_content": "<CONTEXT_DOCS>\n{{context_docs}}\n</CONTEXT_DOCS>"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/utils_edit.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipe_executor/utils.py",
      "artifact": "existing_code"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/recipe_executor/recipes/utils_create.json",
      "context_overrides": {
        "existing_code": "{{existing_code}}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/specs/context.md ===
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.

## Core Requirements

- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Ensure data isolation between different executions
- Follow minimalist design principles

## Implementation Considerations

- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
- Maintain minimal state with clear separation of concerns

## Component Dependencies

The Context component has no external dependencies on other Recipe Executor components.

## Error Handling

- Raise KeyError with descriptive message when accessing non-existent keys
- No special handling for setting values (all types allowed)

## Future Considerations

- Namespacing of artifacts


=== File: recipes/recipe_executor/specs/executor.md ===
# Executor Component Specification

## Purpose

The Executor component is the central orchestration mechanism for the Recipe Executor system. It loads recipe definitions from various sources and executes their steps sequentially using the provided context.

## Core Requirements

- Load and parse recipes from multiple input formats
- Validate recipe structure and step definitions
- Execute steps sequentially using registered step implementations
- Provide clear error messages for troubleshooting
- Support minimal logging for execution status

## Implementation Considerations

- Parse recipes from file paths, JSON strings, or dictionaries
- Extract JSON from markdown fenced code blocks when present
- Use direct instantiation of step classes from the registry
- Handle errors at both recipe and step levels
- Maintain a simple, stateless design

## Component Dependencies

The Executor component depends on:

- **Context** - Uses Context for data sharing between steps
- **Step Registry** - Uses STEP_REGISTRY to look up step classes by type

## Error Handling

- Validate recipe format before execution begins
- Check that step types exist in the registry before instantiation
- Verify each step is properly structured before execution
- Provide specific error messages identifying problematic steps
- Include original exceptions for debugging

## Future Considerations

- Parallel step execution
- Conditional branching between steps
- Step retry policies
- Progress tracking and reporting


=== File: recipes/recipe_executor/specs/llm.md ===
# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers. It handles model initialization, request formatting, and response processing, enabling the Recipe Executor to generate content with different LLM providers through a consistent API.

## Core Requirements

- Support multiple LLM providers (OpenAI, Anthropic, Gemini)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use Pydantic AI for consistent handling and validation of LLM responses
- Implement basic error handling and retry logic
- Support structured output format for file generation

## Implementation Considerations

- Use a clear provider:model_name identifier format
- Direct usage of provider SDKs through pydantic-ai
- Minimal wrapper functions with clear responsibilities
- Consistent error handling with informative messages
- Logging of request details and timing information

## Component Dependencies

The LLM component depends on:

- **Models** - Uses FileGenerationResult and FileSpec for structured output
- **External Libraries** - Relies on pydantic-ai for model interactions

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging
- Include timing information for performance monitoring

## Future Considerations

- Additional LLM providers
- Enhanced parameter control for model fine-tuning


=== File: recipes/recipe_executor/specs/logger.md ===
# Logger Component Specification

## Purpose

The Logger component provides a consistent logging interface for the Recipe Executor system. It initializes and configures logging, writes logs to appropriate files, and ensures that all components can log messages at different severity levels.

## Core Requirements

- Initialize a logger that writes to both stdout and log files
- Support different log levels (DEBUG, INFO, ERROR)
- Create separate log files for each level
- Clear existing logs on each run to prevent unbounded growth
- Provide a consistent log format with timestamps and log levels
- Create log directories if they don't exist

## Implementation Considerations

- Use Python's standard logging module directly
- Reset existing handlers to ensure consistent configuration
- Set up separate handlers for console and different log files
- Create the log directory if it doesn't exist
- Use mode="w" for file handlers to clear previous logs

## Component Dependencies

The Logger component has no external dependencies on other Recipe Executor components.

## Error Handling

- Catch and report directory creation failures
- Handle file access permission issues
- Provide clear error messages for logging setup failures

## Future Considerations

- Customizable log formats


=== File: recipes/recipe_executor/specs/main.md ===
# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, executes the specified recipe, and handles top-level error reporting.

## Core Requirements

- Provide a command-line interface for executing recipes
- Load environment variables from .env files using python-dotenv
  - python-dotenv is already installed as a dependency of the project
- Parse arguments for recipe path and context values
- Initialize the logging system
- Create the context with command-line supplied values
- Execute the specified recipe with proper error handling
- Follow minimal design with clear user-facing error messages

## Implementation Considerations

- Call load_dotenv() early in the main function before any other initialization
- Use argparse for command-line argument parsing
- Initialize logging early in execution flow
- Parse context values from key=value pairs
- Create a clean context for recipe execution
- Keep the main function focused on orchestration
- Provide meaningful exit codes and error messages

## Component Dependencies

The Main component depends on:

- **python-dotenv** - Uses load_dotenv to load environment variables from .env files
- **Context** - Creates the Context object with CLI-supplied values
- **Executor** - Uses RecipeExecutor to run the specified recipe
- **Logger** - Uses init_logger to set up the logging system

## Error Handling

- Validate command-line arguments
- Provide clear error messages for missing or invalid recipe files
- Handle context parsing errors gracefully
- Log all errors before exiting
- Use appropriate exit codes for different error conditions

## Future Considerations

- Support for environment variable configuration
- Support for directory-based recipes


=== File: recipes/recipe_executor/specs/models.md ===
# Models Component Specification

## Purpose

The Models component defines the core data structures used throughout the Recipe Executor system. It provides Pydantic models for validating and structuring data, including recipe steps, file generation results, and step configurations.

## Core Requirements

- Define consistent data structures for file generation results
- Provide configuration models for various step types
- Support recipe structure validation
- Leverage Pydantic for schema validation and documentation
- Include clear type hints and docstrings

## Implementation Considerations

- Use Pydantic models for all data structures
- Keep models focused and minimal
- Provide sensible defaults where appropriate
- Use descriptive field names and docstrings
- Focus on essential fields without over-engineering

## Component Dependencies

The Models component has no external dependencies on other Recipe Executor components.

## Future Considerations

- Extended validation for complex fields


=== File: recipes/recipe_executor/specs/steps/base.md ===
# Steps Base Component Specification

## Purpose

The Steps Base component defines the foundational abstract classes and interfaces for all step implementations in the Recipe Executor system. It provides a common structure for steps, ensuring consistent behavior and integration with the rest of the system.

## Core Requirements

- Define an abstract base class for all step implementations
- Provide a base configuration class for step configuration validation
- Establish a consistent interface for step execution
- Support proper type hinting using generics
- Include logging capabilities in all steps

## Implementation Considerations

- Use Python's abstract base classes for proper interface definition
- Leverage generic typing for configuration type safety
- Keep the base step functionality minimal but complete
- Use Pydantic for configuration validation
- Provide sensible defaults where appropriate

## Component Dependencies

The Steps Base component depends on:

- **Context** - Steps operate on a context object for data sharing
- **Models** - Uses Pydantic's BaseModel for configuration validation

## Error Handling

- Define clear error handling responsibilities for steps
- Propagate errors with appropriate context
- Use logger for tracking execution progress and errors

## Future Considerations

- Lifecycle hooks for pre/post execution
- Asynchronous execution support
- Step validation and dependency checking
- Composition of steps into more complex steps


=== File: recipes/recipe_executor/specs/steps/execute_recipe.md ===
# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Component Dependencies

The ExecuteRecipeStep component depends on:

- **Steps Base** - Extends BaseStep with a specific config type
- **Context** - Shares context between main recipe and sub-recipes
- **Executor** - Uses RecipeExecutor to run the sub-recipe
- **Utils** - Uses render_template for dynamic content resolution

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include sub-recipe path in error messages for debugging

## Future Considerations

- Support for recipe content passed directly in configuration
- Context isolation options for sub-recipes
- Result mapping from sub-recipes back to parent recipes
- Conditional sub-recipe execution


=== File: recipes/recipe_executor/specs/steps/generate_llm.md ===
# GenerateWithLLMStep Component Specification

## Purpose

The GenerateWithLLMStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, and storing generation results in the context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Call LLMs to generate content
- Store generated results in the context
- Support dynamic artifact key resolution
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use template rendering for dynamic prompt generation
- Support template rendering in model selection
- Allow dynamic artifact key through template rendering
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about LLM requests

## Component Dependencies

The GenerateWithLLMStep component depends on:

- **Steps Base** - Extends BaseStep with a specific config type
- **Context** - Retrieves input values and stores generation results
- **LLM** - Uses call_llm function to interact with language models
- **Utils** - Uses render_template for dynamic content resolution

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Future Considerations

- Additional LLM parameters (temperature, max tokens, etc.)


=== File: recipes/recipe_executor/specs/steps/read_file.md ===
# ReadFileStep Component Specification

## Purpose

The ReadFileStep component reads a file from the filesystem and stores its contents in the execution context. It serves as a foundational step for loading data into recipes, such as specifications, templates, and other input files.

## Core Requirements

- Read a file from a specified path
- Support template-based path resolution
- Store file contents in the context under a specified key
- Provide optional file handling for cases when files might not exist
- Include appropriate logging and error messages
- Follow minimal design with clear error handling

## Implementation Considerations

- Use template rendering to support dynamic paths
- Handle missing files explicitly with meaningful error messages
- Use consistent UTF-8 encoding for text files
- Implement optional flag to continue execution if files are missing
- Keep the implementation simple and focused on a single responsibility

## Component Dependencies

The ReadFileStep component depends on:

- **Steps Base** - Extends BaseStep with a specific config type
- **Context** - Stores file contents in the context
- **Utils** - Uses render_template for path resolution

## Error Handling

- Raise FileNotFoundError with clear message when files don't exist
- Support optional flag to continue execution with empty content
- Log appropriate warnings and information during execution

## Future Considerations

- Directory reading and file globbing


=== File: recipes/recipe_executor/specs/steps/registry.md ===
# Step Registry Component Specification

## Purpose

The Step Registry component provides a central mechanism for registering and looking up step implementations by their type names. It enables the dynamic discovery of step classes during recipe execution.

## Core Requirements

- Provide a simple mapping between step type names and their implementation classes
- Support registration of step implementations from anywhere in the codebase
- Enable the executor to look up step classes by their type name
- Follow a minimal, dictionary-based approach with no unnecessary complexity

## Implementation Considerations

- Use a single, global dictionary to store all step registrations
- Allow steps to register themselves upon import
- Keep the registry structure simple and stateless
- Avoid unnecessary abstractions or wrapper functions

## Component Dependencies

The Step Registry component has no external dependencies on other Recipe Executor components.

## Future Considerations

- Dynamic loading of external step implementations
- Step metadata and documentation


=== File: recipes/recipe_executor/specs/steps/write_files.md ===
# WriteFileStep Component Specification

## Purpose

The WriteFileStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both FileGenerationResult and list of FileSpec formats
- Create directories as needed for file paths
- Apply template rendering to file paths
- Provide appropriate logging for file operations
- Follow minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (FileGenerationResult or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Component Dependencies

The WriteFileStep component depends on:

- **Steps Base** - Extends BaseStep with a specific config type
- **Context** - Retrieves file content from the context
- **Models** - Uses FileGenerationResult and FileSpec models
- **Utils** - Uses render_template for path resolution

## Error Handling

- Validate that the artifact exists in context
- Ensure artifact contains a valid FileGenerationResult or list of FileSpec objects
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Future Considerations

- Dry-run mode that logs without writing


=== File: recipes/recipe_executor/specs/utils.md ===
# Utils Component Specification

## Purpose

The Utils component provides utility functions for the Recipe Executor system, primarily focusing on template rendering. It enables steps to use dynamic values from the context in their configuration through a simple templating mechanism.

## Core Requirements

- Provide a template rendering function using the Liquid templating engine
- Support substituting values from the Context into templates
- Handle all context values by converting them to strings
- Provide clear error handling for template rendering failures
- Follow minimal design with focused functionality

## Implementation Considerations

- Use the Liquid library directly without unnecessary abstraction
- Convert context values to strings before rendering to prevent type errors
- Handle rendering errors gracefully with clear error messages
- Keep the implementation stateless and focused

## Component Dependencies

The Utils component depends on:

- **Context** - Uses the Context class for accessing artifacts during template rendering

## Error Handling

- Wrap template rendering in try/except blocks
- Provide specific error messages that indicate the source of template failures
- Propagate rendering errors with useful context

## Future Considerations

- Support for custom template filters or tags
- Support for template partials or includes
- Template validation before rendering


