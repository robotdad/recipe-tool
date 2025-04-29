# AI Context Files
Date: 4/29/2025, 5:13:34 PM
Files: 51

=== File: recipes/recipe_executor/README.md ===
# Recipe Executor Recipes

This directory contains the recipes used for generating the Recipe Executor components. These recipes demonstrate the self-generating capability of the Recipe Executor system.

## Diagram

![Recipe Executor Build Process](./docs/recipe-executor-build-flow.svg)

## Main Recipes

### `build.json`

The main entry point recipe that orchestrates the entire component generation process. It:

1. Reads the component definitions from `components.json`
2. Iterates through each component (optionally filtering by a specific component ID)
3. Processes each component by calling the `process_component.json` recipe

```bash
# Process all components
recipe-tool --execute recipes/recipe_executor/build.json

# Process a single component
recipe-tool --execute recipes/recipe_executor/build.json component_id=context
```

### `components.json`

Contains the definitions of all components in the system, including:

- Component ID
- Dependencies on other components
- References to external documentation

## Sub-Recipes

### `recipes/process_component.json`

Handles the processing of a single component:

1. If in edit mode, reads existing code for the component
2. Calls `recipes/read_component_resources.json` to gather all resources
3. Calls `recipes/generate_component_code.json` to generate code using an LLM

```bash
# Process a specific component with edit mode enabled
recipe-tool --execute recipes/recipe_executor/recipes/process_component.json component_id=context edit=true
```

### `recipes/read_component_resources.json`

Gathers all resources required for generating a component:

1. Reads the component specification
2. Reads the component documentation (if available)
3. Gathers dependency specifications
4. Collects reference documentation
5. Loads implementation philosophy and dev guide

### `recipes/generate_component_code.json`

Uses an LLM to generate code based on the gathered resources:

1. Constructs a prompt with specifications, docs, and guidance
2. Calls the LLM to generate code files
3. Writes the generated files to disk

```bash
# Generate code for a specific component
recipe-tool --execute recipes/recipe_executor/recipes/generate_component_code.json spec=path/to/spec.md docs=path/to/docs.md
```

## Configuration Options

| Option               | Description                                                           |
| -------------------- | --------------------------------------------------------------------- |
| `component_id`       | ID of the specific component to process (e.g., "context", "executor") |
| `edit`               | Set to `true` to read and update existing code (default: `false`)     |
| `model`              | LLM model to use (default: "openai/o4-mini")                          |
| `output_root`        | Root directory for output files (default: "output")                   |
| `existing_code_root` | Root directory for existing code (used in edit mode)                  |

## Example Usage

```bash
# Process all components and output to a custom directory
recipe-tool --execute recipes/recipe_executor/build.json output_root=custom_output

# Edit an existing component with a specific model
recipe-tool --execute recipes/recipe_executor/build.json component_id=executor edit=true model=openai/gpt-4o existing_code_root=src
```

## How It Works

The recipe system follows these steps:

1. **Component Selection**: The system reads component definitions and selects which ones to process.
2. **Resource Gathering**: For each component, it collects specifications, documentation, and dependencies.
3. **Code Generation**: It uses an LLM to generate code based on the gathered resources.
4. **Output**: The generated code is written to disk in the specified directory structure.

This workflow demonstrates the power of the Recipe Executor to generate its own code, serving as both an example and a practical tool for development.


=== File: recipes/recipe_executor/build.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/recipes/read_components.json",
        "context_overrides": {}
      }
    },
    {
      "type": "loop",
      "config": {
        "items": "components",
        "item_key": "component",
        "max_concurrency": 0,
        "delay": 0.1,
        "result_key": "built_components",
        "substeps": [
          {
            "type": "conditional",
            "config": {
              "condition": "{% unless component_id %}true{% else %}{% if component_id == component.id %}true{% else %}false{% endif %}{% endunless %}",
              "if_true": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/recipes/process_component.json",
                      "context_overrides": {}
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  ]
}


=== File: recipes/recipe_executor/components.json ===
[
  {
    "id": "context",
    "deps": ["protocols"],
    "refs": []
  },
  {
    "id": "executor",
    "deps": ["protocols", "logger", "models", "steps.registry"],
    "refs": []
  },
  {
    "id": "logger",
    "deps": ["protocols"],
    "refs": []
  },
  {
    "id": "main",
    "deps": ["context", "executor", "logger", "protocols"],
    "refs": []
  },
  {
    "id": "models",
    "deps": ["protocols"],
    "refs": []
  },
  {
    "id": "protocols",
    "deps": ["models"],
    "refs": []
  },
  {
    "id": "llm_utils.azure_openai",
    "deps": ["logger"],
    "refs": [
      "AZURE_IDENTITY_CLIENT_DOCS.md",
      "git_collector/PYDANTIC_AI_DOCS.md"
    ]
  },
  {
    "id": "llm_utils.llm",
    "deps": ["logger", "llm_utils.azure_openai", "llm_utils.mcp"],
    "refs": ["git_collector/PYDANTIC_AI_DOCS.md"]
  },
  {
    "id": "llm_utils.mcp",
    "deps": ["logger"],
    "refs": ["git_collector/PYDANTIC_AI_DOCS.md"]
  },
  {
    "id": "steps.base",
    "deps": ["logger", "protocols"],
    "refs": []
  },
  {
    "id": "steps.conditional",
    "deps": ["context", "steps.base", "utils.templates"],
    "refs": []
  },
  {
    "id": "steps.execute_recipe",
    "deps": [
      "context",
      "executor",
      "protocols",
      "steps.base",
      "utils.templates"
    ],
    "refs": []
  },
  {
    "id": "steps.llm_generate",
    "deps": [
      "context",
      "models",
      "llm_utils.llm",
      "llm_utils.mcp",
      "steps.base",
      "utils.models",
      "utils.templates"
    ],
    "refs": []
  },
  {
    "id": "steps.loop",
    "deps": [
      "context",
      "executor",
      "steps.base",
      "steps.registry",
      "utils.templates"
    ],
    "refs": []
  },
  {
    "id": "steps.mcp",
    "deps": ["protocols", "llm_utils.mcp", "steps.base", "utils.templates"],
    "refs": ["git_collector/MCP_PYTHON_SDK_DOCS.md"]
  },
  {
    "id": "steps.parallel",
    "deps": ["protocols", "steps.base", "steps.registry"],
    "refs": []
  },
  {
    "id": "steps.read_files",
    "deps": ["steps.base", "context", "utils.templates"],
    "refs": []
  },
  {
    "id": "steps.registry",
    "deps": [],
    "refs": []
  },
  {
    "id": "steps.write_files",
    "deps": ["context", "models", "steps.base", "utils/.templates"],
    "refs": []
  },
  {
    "id": "utils.models",
    "deps": [],
    "refs": []
  },
  {
    "id": "utils.templates",
    "deps": ["protocols"],
    "refs": ["git_collector/LIQUID_PYTHON_DOCS.md"]
  }
]


=== File: recipes/recipe_executor/components/context/context_docs.md ===
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
from recipe_executor.protocols import ContextProtocol
```

_(The `ContextProtocol` interface is imported for typing or interface reference, while `Context` is the concrete class you instantiate.)_

## Initialization

You can create a Context with or without initial data:

```python
# Create an empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"input": "example data"})

# With configuration values
context = Context(config={"run_mode": "test"})

# With both artifacts and configuration
context = Context(
    artifacts={"input": "example data"},
    config={"run_mode": "test"}
)
```

When providing initial artifacts or config, Context will deep-copy them. Changes to the original dictionaries after creation won’t affect the Context.

## Core API

Once you have a Context, you use it like a dictionary for artifacts:

### Storing Values

```python
context["result"] = 42
```

Stores the value `42` under the key `"result"` in the context’s artifacts.

### Retrieving Values

```python
value = context["result"]          # Retrieves the value for "result" (KeyError if missing)
value_or_default = context.get("missing", default_value)
```

Use `context[key]` for direct access (which will throw an error if the key is not present), or `context.get(key, default)` to safely retrieve a value with a fallback.

### Checking for Keys

```python
if "result" in context:
    # Key exists in context
    print(context["result"])
```

The `in` operator checks if a given artifact key exists in the context.

### Iterating over Keys

```python
for key in context:
    print(key, context[key])

# Or equivalently:
for key in context.keys():
    print(key, context[key])
```

Context supports iteration, yielding each artifact key (internally, it iterates over a snapshot list of keys to avoid issues if you modify the context during iteration). You can also call `keys()` to get an iterator of keys explicitly. The `len(context)` function returns the number of artifacts currently stored.

### Getting All Values

```python
snapshot = context.dict()
```

`dict()` returns a deep copy of all artifacts in the context as a regular Python dictionary. This is useful if you need to inspect or serialize the entire state without risk of modifying the Context itself.

```python
snapshot_json = context.json()
```

`json()` returns a JSON string representation of the context’s artifacts. This is useful for logging or sending the context over a network.

### Cloning the Context

```python
new_context = context.clone()
```

The `clone()` method creates a deep copy of the Context, including all artifacts and configuration. The returned object is a new `Context` instance that can be modified independently of the original. This is often used when running sub-recipes or parallel steps to ensure each execution has an isolated context state.

## Important Notes

- **Shared State**: The Context is shared across all steps in a recipe execution. Any step that writes to the context (e.g., `context["x"] = value`) is making that data available to subsequent steps. This is how data flows through a recipe.
- **No Thread Safety**: The Context class does not implement any locking or thread-safety mechanisms. It assumes sequential access. If you need to use it in parallel, each parallel thread or process should work on a cloned copy of the Context to avoid race conditions (as done in the Parallel step implementation).
- **Protocols Interface**: The `Context` class implements the `ContextProtocol` interface defined in the Protocols component. When writing code that interacts with contexts, you can use `ContextProtocol` in type hints to allow any context implementation. In practice, you will typically use the provided `Context` class unless you extend the system.
- **Configuration vs Artifacts**: Remember that context configuration is only available via `context.get_config()` and `context.set_config()`. It is not manipulated via the dictionary interface (`__getitem__`/`__setitem__`). This separation is by convention; Context does not prevent you from modifying the configuration, so it is up to developers to decide how to manage configuration values.


=== File: recipes/recipe_executor/components/context/context_spec.md ===
# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple, dictionary-like interface that steps and other components use to store and retrieve data (artifacts) during recipe execution, along with a separate space for configuration values.

## Core Requirements

- Maintain a store for **artifacts** (dynamic data produced and consumed by steps) and a separate store for **configuration** (static or initial settings).
- Support dictionary-like operations for artifacts:
  - Setting values by key (e.g., `context["x"] = value`).
  - Retrieving values by key (e.g., `value = context["x"]` or `context.get("x")`).
  - Checking for keys (`"x" in context`).
  - Iterating over keys (for example, `for k in context: ...`).
- Ensure that modifying the context in one step affects subsequent steps (shared mutability), while also allowing safe copying when needed.
- Provide a `clone()` method to create a deep copy of the entire context (both artifacts and configuration) for use cases like parallel execution where isolation is required.
- Remain lightweight and straightforward, following minimalist design principles (it should essentially behave like a `dict` with a config attached, without extra complexity).
- Provide a `dict()` and `json()` method to return a deep copy of the artifacts as a standard Python dictionary and a JSON string, respectively. This is useful for serialization or logging purposes.

## Implementation Considerations

- Use a Python dictionary internally to store artifacts. The keys are strings and values can be of any type (no restriction on artifact data types).
- Store configuration in a separate, internal dictionary (`_config` attribute) to distinguish it from runtime artifacts. Configuration might be populated at context creation and typically remains constant, but it's not enforced as immutable by the class.
- On initialization (`__init__`), deep copy any provided artifacts or config dictionaries. This prevents unintentional side effects if the caller modifies the dictionaries after passing them in.
- Implement the magic methods `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, and `__len__` to mimic standard dict behavior for artifacts. Also provide a `keys()` method for convenience.
- The `get` method should allow a default value, similar to `dict.get`, to avoid raising exceptions on missing keys.
- When iterating (`__iter__` or using `keys()`), return a static list or iterator that won’t be affected by concurrent modifications (for example, by copying the key list).
- The `clone()` method should deep copy both artifacts and configuration to produce a completely independent Context. This is important for features like running sub-recipes in parallel or reusing a context as a template.
- Raise a `KeyError` with a clear message in `__getitem__` if a key is not found, to help with debugging missing artifact issues.
- Do not implement any locking or thread-safety measures; the context is intended for sequential use within the executor (concurrent modifications are handled by using `clone` for parallelism instead).
- The Context class should implement the `ContextProtocol` interface defined in the Protocols component. That means any changes to the interface (methods or behavior) should be reflected in both the class and the protocol definition. In practice, the Context class already provides all methods required by `ContextProtocol`.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- **Protocols** - (Required) The Context component conforms to the `ContextProtocol` interface, which is defined in the Protocols component. This ensures other components interact with Context through a well-defined contract.

### External Libraries

- **copy** (Python stdlib) - (Required) Uses `copy.deepcopy` for cloning internal state safely.
- **typing** - (Required) Used for type hints (e.g., `Dict[str, Any]`, `Iterator[str]`) to clarify usage.

### Configuration Dependencies

- **None.** The Context component does not rely on external configuration. It is typically configured via its constructor arguments (artifacts and config dicts) provided at runtime by Main or a calling component.

## Error Handling

- Attempts to access a missing artifact key via `context["missing_key"]` result in a `KeyError`. The error message explicitly names the missing key for clarity (e.g., `"Key 'foo' not found in Context."`).
- The `get` method returns a default (or `None` if not provided) instead of raising an error for missing keys, offering a safe way to query the context.
- Setting a key (`context["x"] = value`) has no special error cases; it will overwrite existing values if the key already exists.
- Cloning always succeeds barring extreme cases (like objects in the context that are not copyable); such cases would raise exceptions from `copy.deepcopy` which propagate up (this is acceptable, as it would be a misusage of context content types).

## Output Files

- `recipe_executor/context.py`

## Future Considerations

- **Namespacing or Hierarchies**: In larger workflows, there might be a need to namespace context data (e.g., per step or per sub-recipe) to avoid key collisions. Future versions might introduce optional namespacing schemes or structured keys.
- **Immutable Context Option**: Possibly provide a mode or subclass for an immutable context (read-only once created) for scenarios where you want to ensure no step modifies the data.


=== File: recipes/recipe_executor/components/executor/executor_docs.md ===
# Executor Component Usage

## Importing

```python
from recipe_executor.executor import Executor
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol
```

_(Import the concrete `Executor` to create an instance, and import `ExecutorProtocol`/`ContextProtocol` if you want to use interfaces in type hints.)_

## Basic Usage

The Executor has a single primary method: `execute()`. This async method loads and runs a recipe with a given context. Typically, you will create a `Context` (for artifacts) and an `Executor`, then call and await `execute` with the recipe you want to run.

```python
from recipe_executor import Context

# Create context and executor (with protocol typing for clarity)
context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor(logger)

# Execute a recipe from a JSON file path
await executor.execute("path/to/recipe.json", context)

# Execute a recipe from a JSON string
json_string = '{"steps": [{"type": "read_files", "path": "example.txt", "content_key": "file_content"}]}'
await executor.execute(json_string, context)

# Execute a recipe from a JSON object (dict)
import json
recipe_dict = json.loads(json_string)
await executor.execute(recipe_dict, context)

# Execute a recipe from a Path object (if using pathlib)
from pathlib import Path
recipe_path = Path("path/to/recipe.json")
await executor.execute(recipe_path, context)

# Execute a recipe from a pre-defined dictionary
recipe_dict = {
    "steps": [
        {
            "type": "llm_generate",
            "prompt": "Write a poem about the sea",
            "model": "openai/gpt-4o",
            "output_format": "files",
            "output_key": "poem"
        }
    ]
}
await executor.execute(recipe_dict, context)
```

In each case, the Executor will parse the input (if needed) and sequentially execute each step in the recipe using the same `context`. After execution, the `context` may contain new artifacts produced by the steps (for example, in the above cases, the `file_content` and `poem` artifacts would be available in the context).

## Behavior Details

- The context passed into `execute` is mutated in-place by the steps. You should create a fresh Context (or clone an existing one) if you plan to reuse it for multiple recipe executions to avoid cross-contamination of data.
- If the recipe path is invalid or the JSON is malformed, `execute` will raise an error (ValueError or TypeError). Ensure you handle exceptions when calling `execute` if there's a possibility of bad input.
- The Executor uses the step registry to find the implementation for each step type. All default steps (like `"read_files"`, `"write_files"`, `"execute_recipe"`, etc.) are registered when you import the `recipe_executor.steps` modules. Custom steps need to be registered in the registry before Executor can use them.

## Important Notes

- **Interface Compliance**: The `Executor` class implements the `ExecutorProtocol` interface. Its `execute` method is designed to accept any object implementing `ContextProtocol`. In practice, you will pass a `Context` instance (which fulfills that protocol). This means the Executor is flexible — if the context were some subclass or alternative implementation, Executor would still work as long as it follows the interface.
- **One Executor, One Execution**: An `Executor` instance can be reused to run multiple recipes (simply call `execute` again with a different recipe and context), but it does not retain any state between runs. You can also create a new `Executor` for each execution. Both approaches are acceptable; there's typically little overhead in creating a new Executor.
- **Step Instantiation**: When the Executor runs a step, it creates a new instance of the step class for each step execution (even if the same step type appears multiple times, each occurrence is a fresh instance). The step class’s `__init__` usually takes the step configuration (from the recipe) and an optional logger.
- **Error Handling**: If any step fails (raises an exception), Executor will halt the execution of the remaining steps. The exception will bubble up as a `ValueError` with context about which step failed. You should be prepared to catch exceptions around `await executor.execute(...)` in contexts where a failure is possible or should not crash the entire program.
- **Context After Execution**: After `execute` completes (successfully), the context contains all the artifacts that steps have placed into it. You can inspect `context` to get results (for example, if a step writes an output, it might be found in `context["output_key"]`). The context is your way to retrieve outcomes from the recipe.


=== File: recipes/recipe_executor/components/executor/executor_spec.md ===
# Executor Component Specification

## Purpose

The Executor component is responsible for executing recipes defined in JSON format. It loads the recipe, validates its structure, and sequentially executes each step using a shared context object. The Executor is designed to be stateless, meaning it does not maintain any internal state between executions. It also handles logging and error propagation to ensure that any issues encountered during execution are reported clearly.

## Core Requirements

- Accept recipe definitions in multiple formats:
  - File path to a JSON recipe file on disk.
  - Raw JSON string containing the recipe.
  - A Python dictionary already representing the recipe.
- Parse or load the recipe into the `Recipe` type.
- Validate the recipe structure.
- Iterate through the list of steps and execute them sequentially:
  - For each step, retrieve the step class from the Step Registry using the step's `"type"`.
  - Instantiate the step with its configuration.
  - Call and await the step's `execute(context)` method, passing in the shared context object.
- Handle errors gracefully:
  - If a step raises an exception, stop execution and wrap the exception in a clear message indicating which step failed.
  - Propagate errors up to the caller (Main or a supervising component) with context so that it can be logged or handled.
- Remain stateless aside from the execution flow; the Executor should not hold state between runs (each call to `execute` is independent).

## Implementation Considerations

- **Recipe Loading**:
  - If the recipe is a string, check if it is a file path (using `os.path.isfile()`). If so, read the file content and parse it as JSON. If not, treat it as a raw JSON string.
  - If the recipe is a dictionary, use it directly.
  - Use `json.loads()` to parse JSON strings into Python dictionaries.
  - If the recipe is a file path, use `json.load()` to read and parse the file content.
- **Format Validation**: Use `Recipe.model_validate(value)` or `Recipe.model_validate_json(value)` to validate the loaded recipe against the `Recipe` model. This ensures that the recipe adheres to the expected structure and types.
- **Step Execution**: Retrieve step implementations via `STEP_REGISTRY` (a global registry mapping step type names to their classes).
- **Context Interface**: Use the `ContextProtocol` interface for the `context` parameter to prevent coupling to a specific context implementation.
- **Protocols Compliance**: Document that Executor implements the `ExecutorProtocol`. The async `execute` method signature should match exactly what `ExecutorProtocol` defines.
- **Sequential Execution**: Execute each defined step in the order they appear in the recipe. The context object is passed to each step's `execute` method, allowing steps to read from and write to the context.
- **Error Propagation**: Wrap exceptions from steps in a `ValueError` with a message indicating the step index and type that failed, then raise it.

## Component Dependencies

### Internal Components

- **Protocols**: Uses the `ContextProtocol` definition for interacting with the context, and in concept provides the implementation for the `ExecutorProtocol`.
- **Models**: Uses the `Recipe` and `RecipeStep` models to represent the loaded recipe.
- **Step Registry**: Uses `STEP_REGISTRY` to look up and instantiate step classes by their type names.
  - _Note_: The dependency on specific step classes is indirect via the registry, preventing the Executor from needing to import each step module.
- **Logger**: The Executor will use the logger passed in by the caller

### External Libraries

- **json** - (Required) Used to parse JSON strings and files into Python dictionaries.
- **os** - (Required) Used to check file path existence and determine if a string is a file path.
- **logging** - (Required) Uses Python's logging library to report on execution progress and issues.
- **typing** - (Required) Utilizes typing for type hints (e.g., `Union[str, Dict]` for recipe input, and `ContextProtocol` for context type).

### Configuration Dependencies

- None

## Logging

- Debug:
  - Log when a recipe is loaded (including whether it came from a dict, file, or JSON string).
  - Log the entire recipe content (or a summary) and the number of steps at the start of execution.
  - Log before executing each step (index and type, plus step details for traceability).
  - Log after a step executes successfully.
  - Log a message when all steps complete.
- Info:
  - The Executor itself does not log at info level by default. (High-level info logging, like start and end of execution, is usually handled by Main or the logger setup.)
- Warning/Error:
  - If a step type is not found in the registry, log or include a message about the unknown step type (this triggers a ValueError as well).
  - No direct error logging inside Executor (it raises exceptions up, and the caller (Main) will log the error).

## Error Handling

- **Unsupported Recipe Type**: If the `recipe` argument is neither `dict` nor `str`, a `TypeError` is raised immediately.
- **File Read Errors**: If a file path is provided but reading or JSON parsing fails, a `ValueError` is raised with details (e.g., file not found or JSON decode error).
- **Invalid Recipe Structure**: If after loading, the structure isn't a dict or missing a proper steps list, a `ValueError` is raised explaining the expectation.
- **Unknown Step Type**: If a step's `"type"` is not in `STEP_REGISTRY`, raise `ValueError` indicating an unknown step type at that index.
- **Step Execution Error**: If `step_instance.execute(context)` raises an Exception, catch it. Raise a new `ValueError` that wraps the original exception, with a message specifying which step index and type failed.
- Stop execution upon the first error encountered (fail-fast behavior).

## Output Files

- `recipe_executor/executor.py`


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_docs.md ===
# Azure OpenAI Component Usage

## Importing

```python
from recipe_executor.llm_utils.azure_openai import get_azure_openai_model
```

## Basic Usage

```python
def get_azure_openai_model(
    logger: logging.Logger,
    model_name: str,
    deployment_name: Optional[str] = None,
) -> pydantic_ia.models.openai.OpenAIModel:
    """
    Create a PydanticAI OpenAIModel instance, configured from environment variables for Azure OpenAI.

    Args:
        logger (logging.Logger): Logger for logging messages.
        model_name (str): Model name, such as "gpt-4o" or "o4-mini".
        deployment_name (Optional[str]): Deployment name for Azure OpenAI, defaults to model_name.

    Returns:
        OpenAIModel: A PydanticAI OpenAIModel instance created from AsyncAzureOpenAI client.

    Raises:
        Exception: If the model cannot be created or if the model name is invalid.
    """
```

Usage example:

```python
# Get an OpenAI model using Azure OpenAI
openai_model = get_azure_openai_model(
    model_name="o4-mini",
    logger=logger
)
```

# Get an OpenAI model using Azure OpenAI with a specific deployment name

```python
openai_model = get_azure_openai_model(
    model_name="o4-mini",
    deployment_name="my_deployment_name",
    logger=logger
)
```

## Environment Variables

The component uses environment variables for authentication and configuration. Depending upon the authentication method, set the following environment variables:

### Option 1: Managed Identity with Default Managed Identity

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_OPENAI_BASE_URL= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 2: Managed Identity with Custom Client ID

```bash
AZURE_USE_MANAGED_IDENTITY=true # Set to true to use managed identity
AZURE_MANAGED_IDENTITY_CLIENT_ID= # Required
AZURE_OPENAI_BASE_URL= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```

### Option 3: API Key Authentication

```bash
AZURE_OPENAI_API_KEY= # Required
AZURE_OPENAI_BASE_URL= # Required
AZURE_OPENAI_API_VERSION= # Optional, defaults to 2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME= # Optional, defaults to model_name
```


=== File: recipes/recipe_executor/components/llm_utils/azure_openai/azure_openai_spec.md ===
# Azure OpenAI Component Specification

## Purpose

The Azure OpenAI component provides a PydanticAI wrapper for Azure OpenAI models for use with PydanticAI Agents. It handles model initialization and authentication.

## Core Requirements

- Provide a PydanticAI-compatible OpenAIModel instance
- Support choice of api key or Azure Identity for authentication
- Use the `openai` library for Azure OpenAI client
- Implement basic error handling

## Implementation Considerations

- Load api keys and endpoints from environment variables, validating their presence
- If using Azure Identity:
  - AsyncAzureOpenAI client must be created with a token provider function
  - If using a custom client ID, use `ManagedIdentityCredential` with the specified client ID
- Provide the function `get_azure_openai_model` to create the OpenAIModel instance
- Create the async client using `openai.AsyncAzureOpenAI` with the provided token provider or API key
- Create a `pydantic_ai.providers.openai.OpenAIProvider` with the Azure OpenAI client
- Return a `pydantic_ai.models.openai.OpenAIModel` with the model name and provider

## Implementation Hints

```python
# Option 1: Create AsyncAzureOpenAI client with API key
azure_client = AsyncAzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_BASE_URL,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Option 2: Create AsyncAzureOpenAI client with Azure Identity
azure_client = AsyncAzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=AZURE_OPENAI_BASE_URL,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)

# Use the client to create the OpenAIProvider
openai_model = OpenAIModel(
    model_name,
    provider=OpenAIProvider(openai_client=azure_client),
)
```

## Logging

- Debug: Log the loaded environment variables (masking all but first/last character of api keys)
- Info: Log the model name and auth method (api key or Azure Identity)

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic-ai**: Uses PydanticAI's `OpenAIModel` and `OpenAIProvider` for model management
- **openai**: Uses `AsyncAzureOpenAI` client for API communication
- **azure-identity**: Uses `DefaultAzureCredential`, `ManagedIdentityCredential`, and `get_bearer_token_provider` for token provision

### Configuration Dependencies

- **AZURE_USE_MANAGED_IDENTITY**: (Optional) Boolean flag to use Azure Identity for authentication
- **AZURE_OPENAI_API_KEY**: (Required for API key auth) API key for Azure OpenAI authentication
- **AZURE_OPENAI_BASE_URL**: (Required) Endpoint URL for Azure OpenAI service
- **AZURE_OPENAI_DEPLOYMENT_NAME**: (Required) Deployment name in Azure OpenAI
- **AZURE_OPENAI_API_VERSION**: (Required) API version to use with Azure OpenAI, defaults to "2025-03-01-preview"
- **AZURE_CLIENT_ID**: (Optional) Client ID for managed identity authentication

## Error Handling

- Debug: Log detailed error messages for failed authentication or model creation
- Info: Log successful authentication and model creation

## Output Files

- `recipe_executor/llm_utils/azure_openai.py`


=== File: recipes/recipe_executor/components/llm_utils/llm/llm_docs.md ===
# LLM Component Usage

## Importing

```python
from recipe_executor.llm_utils.llm import LLM
from recipe_executor.llm_utils.mcp import create_mcp_server_config
```

## Basic Usage

The LLM component provides one main function:

```python
class LLM:
    def __init__(
            self,
            logger: logging.Logger,
            model: str = "openai/gpt-4o",
            max_tokens: Optional[int] = None,
            mcp_servers: Optional[List[MCPServer]] = None,
        ):
        """
        Initialize the LLM component.
        Args:
            logger (logging.Logger): Logger for logging messages.
            model (str): Model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
            max_tokens (int): Maximum number of tokens for the LLM response.
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
        """

    async def generate(
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        output_type: Type[Union[str, BaseModel]] = str,
        mcp_servers: Optional[List[MCPServer]] = None
    ) -> Union[str, BaseModel]:
        """
        Generate an output from the LLM based on the provided prompt.

        Args:
            prompt (str): The prompt string to be sent to the LLM.
            model (Optional[str]): The model identifier in the format 'provider/model_name' (or 'provider/model_name/deployment_name').
                If not provided, the default set during initialization will be used.
            max_tokens (Optional[int]): Maximum number of tokens for the LLM response.
                If not provided, the default set during initialization will be used.
            output_type (Type[Union[str, BaseModel]]): The requested type for the LLM output.
                - str: Plain text output (default).
                - BaseModel: Structured output based on the provided JSON schema.
            mcp_servers Optional[List[MCPServer]]: List of MCP servers for access to tools.
                If not provided, the default set during initialization will be used.

        Returns:
            Union[str, BaseModel]: The output from the LLM, either as plain text or structured data.

        Raises:
            Exception: If any of the following occurs:
                - Invalid model ID or format.
                - Unsupported provider.
                - MCP server errors.
                - Network or API errors.
                - JSON schema validation errors.
        """
```

Usage example:

```python
from recipe_executor.llm_utils.mcp import get_mcp_server

llm = LLM(logger=logger)
# With optional MCP integration:
weather_mcp_server = get_mcp_server(
    logger=logger,
    config={
        "url": "http://localhost:3001/sse",
        "headers": {
            "Authorization": "{{token}}"
        },
    }
)
llm_mcp = LLM(logger=logger, mcp_servers=[weather_mcp_server])

# Call LLM with default model
result = await llm.generate("What is the weather in Redmond, WA today?")

# Call with specific model
result = await llm.generate(
    prompt="What is the capital of France?",
    model="openai/o4-mini"
)

# Call with JSON schema validation
class UserProfile(BaseModel):
    name: str
    age: int
    email: str

result = await llm.generate(
    prompt="Extract the user profile from the following text: {{text}}",
    model="openai/o4-mini",
    max_tokens=100,
    output_type=UserProfile
)
```

## Model ID Format

The component uses a standardized model identifier format:

All models: `provider/model_name`
Example: `openai/o4-mini`

Azure OpenAI models with custom deployment name: `azure/model_name/deployment_name`
Example: `azure/gpt-4o/my_deployment_name`
If no deployment name is provided, the model name is used as the deployment name.

### Supported providers:

- **openai**: OpenAI models (e.g., `gpt-4o`, `o3`, `o4-mini`, etc.)
- **azure**: Azure OpenAI models (e.g., `gpt-4o`, `o3`, `o4-mini`, etc.)
- **azure**: Azure OpenAI models with custom deployment name (e.g., `gpt-4o/my_deployment_name`)
- **anthropic**: Anthropic models (e.g., `claude-3-7-sonnet-latest`)
- **ollama**: Ollama models (e.g., `phi4`, `llama3.2`, `qwen2.5-coder:14b`)

## Error Handling

Example of error handling:

```python
try:
    result = async llm.generate(prompt, model_id)
    # Process result
except ValueError as e:
    # Handle invalid model ID or format
    print(f"Invalid model configuration: {e}")
except Exception as e:
    # Handle other errors (network, API, etc.)
    print(f"LLM call failed: {e}")
```

## Important Notes

- The component logs full request details at debug level


=== File: recipes/recipe_executor/components/llm_utils/llm/llm_spec.md ===
# LLM Component Specification

## Purpose

The LLM component provides a unified interface for interacting with various large language model providers and optional MCP servers. It handles model initialization, request formatting, and result processing, enabling the Recipe Executor to generate content and orchestrate external tools through a single API.

## Core Requirements

- Support multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Ollama)
- Provide model initialization based on a standardized model identifier format
- Encapsulate LLM API details behind a unified interface
- Use PydanticAI's async interface for non-blocking LLM calls
- Use PydanticAI for consistent handling and validation of LLM output
- Implement basic error handling
- Support optional structured output format
- Accept an optional `mcp_servers: Optional[List[MCPServer]]` to enable remote MCP tool integration

## Implementation Considerations

- Use a clear `provider/model_name` identifier format
- Do not need to pass api keys directly to model classes
  - Exception: need to provide to AzureProvider)
- Use PydanticAI's provider-specific model classes, passing only the model name
  - pydantic_ai.models.openai.OpenAIModel (used also for Azure OpenAI and Ollama)
  - pydantic_ai.models.anthropic.AnthropicModel
- Create a PydanticAI Agent with the model, structured output type, and optional MCP servers
- Support: `output_type: Type[Union[str, BaseModel]] = str`
- Pass provided `mcp_servers` (or empty list) to the Agent constructor (e.g. `Agent(model, mcp_servers=mcp_servers, output_type=output_type)`)
- Implement fully asynchronous execution:
  - Make `generate` an async function (`async def generate`)
  - Use `await agent.run(prompt)` method of the Agent to make requests
- CRITICAL: make sure to return the `result.output` in the `generate` method to return only the structured output

## Logging

- Debug: Log full request payload before making call and then full result payload after receiving it
- Info: Log model name and provider before making call (do not include the request payload details) and then include processing times and tokens used upon completion (do not include the result payload details)

## Component Dependencies

### Internal Components

- **Azure OpenAI**: Uses `get_azure_openai_model` for Azure OpenAI model initialization
- **Logger**: Uses the logger for logging LLM calls
- **MCP**: Integrates remote MCP tools when `mcp_servers` are provided (uses `pydantic_ai.mcp`)

### External Libraries

- **pydantic-ai**: Uses PydanticAI for model initialization, Agent-based request handling, and structured-output processing
- **pydantic-ai.mcp**: Provides `MCPServer`, `MCPServerHTTP` and `MCPServerStdio` classes for MCP server transports

### Configuration Dependencies

- **DEFAULT_MODEL**: (Optional) Environment variable specifying the default LLM model in format "provider/model_name"
- **OPENAI_API_KEY**: (Required for OpenAI) API key for OpenAI access
- **ANTHROPIC_API_KEY**: (Required for Anthropic) API key for Anthropic access
- **OLLAMA_BASE_URL**: (Required for Ollama) Endpoint for Ollama models

## Error Handling

- Provide clear error messages for unsupported providers
- Handle network and API errors gracefully
- Log detailed error information for debugging

## Output Files

- `recipe_executor/llm_utils/llm.py`

## Dependency Integration Considerations

### PydanticAI

Create a PydanticAI model for the LLM provider and model name. This will be used to initialize the model and make requests.

```python
def get_model(model_id: str) -> OpenAIModel | AnthropicModel:
    """
    Initialize an LLM model based on a standardized model_id string.
    Expected format: 'provider/model_name' or 'provider/model_name/deployment_name'.

    Supported providers:
    - openai
    - azure (for Azure OpenAI, use 'azure/model_name/deployment_name' or 'azure/model_name')
    - anthropic
    - ollama

    Args:
        model_id (str): Model identifier in format 'provider/model_name'
            or 'provider/model_name/deployment_name'.
            If None, defaults to 'openai/gpt-4o'.

    Returns:
        The model instance for the specified provider and model.

    Raises:
        ValueError: If model_id format is invalid or if the provider is unsupported.
    """

    # If 'azure' is the model provider, use the `get_azure_openai_model` function
```

Usage example:

```python
# Get an OpenAI model
openai_model = get_model("openai/o4-mini")
# Uses OpenAIModel('o4-mini')

# Get an Anthropic model
anthropic_model = get_model("anthropic/claude-3-7-sonnet-latest")
# Uses AnthropicModel('claude-3-7-sonnet-latest')

# Get an Ollama model
ollama_model = get_model("ollama/phi4")
# Uses OllamaModel('phi4')
```

Getting an agent:

```python
from pydantic_ai import Agent

# Create an agent with the model
agent: Agent[None, Union[str, BaseModel]] = Agent(model=ollama_model, output_type=str, mcp_servers=mcp_servers)

# Call the agent with a prompt
async with agent.run_mcp_servers():
  result = await agent.run("What is the capital of France?")

# Process the result
print(result.data)  # This will print the structured output
```

#### Ollama

- The Ollama model requires an endpoint to be specified. This can be done by passing the `endpoint` parameter to the `get_model` function.
- The endpoint should be in the format `http://<host>:<port>`, where `<host>` is the hostname or IP address of the Ollama server and `<port>` is the port number on which the server is running.

Then you can use the `OpenAIModel` class to create an instance of the model and make requests to the Ollama server.

```python
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers import OpenAIProvider
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# inside the get_model function
return OpenAIModel(
    model_name='qwen2.5-coder:7b',
    provider=OpenAIProvider(base_url=f'{OLLAMA_BASE_URL}/v1'),
)
```


=== File: recipes/recipe_executor/components/llm_utils/mcp/mcp_docs.md ===
# MCP Utility Usage

## Importing

```python
from recipe_executor.llm_utils.mcp import get_mcp_server
```

## Basic Usage

You can create an MCP server client using the `get_mcp_server` function. This function takes a logger and a configuration object as arguments.

```python
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
    """
```

Use the provided `MCPServer` client to connect to an MCP server for external tool calls:

```python
from recipe_executor.llm_utils.mcp import get_mcp_server
from recipe_executor.models import MCPServerHttpConfig
mcp_server = get_mcp_server(
    logger=logger,
    config={
        "url": "http://localhost:3001/sse",
        "headers": {
            "Authorization": "{{token}}"
        }
    }
)

# List available tools
tools = await mcp_server.list_tools()
print([t.name for t in tools.tools])

# Call a specific tool
result = await mcp_server.call_tool("get_stock", {"item_id": 123})
print(result)
```

## Error Handling

Tools list and calls will raise exceptions on failures:

```python
try:
    result = await client.call_tool("bad_tool", {})
except RuntimeError as e:
    print(f"Tool call failed: {e}")
```

## Important Notes

- **MCPServer** does not maintain an active connection to the server. Each tool list/call creates a new connection.


=== File: recipes/recipe_executor/components/llm_utils/mcp/mcp_spec.md ===
# MCP Utility Component Specification

## Purpose

The MCP utilities provide minimal, low‑level utilities for interacting with MCP servers.

## Core Requirements

- Provide a utilty method to create a PydanticAI `MCPServer` instance from a configuration object.

## Implementation Considerations

- For the `get_mcp_server` function:
  - Accept a logger and a configuration object.
  - Create an `MCPServer` instance based on the provided configuration, inferring the type of server (HTTP or stdio) from the configuration.
  - Only use the values that are necessary for the MCP server, ignore the rest.
  - Validate the configuration and raise `ValueError` if invalid.
  - Always return a PydanticAI `MCPServer` instance.

## Logging

- Debug: Log the configuration values (masking sensitive information such as keys, secrets, etc.).
- Info: For `get_mcp_server`, log the server type (HTTP or stdio) and relevant identifying information (e.g., URL, command/arg).

## Component Dependencies

### Internal Components

- **Logger**: Uses the logger for logging LLM calls

### External Libraries

- **pydantic_ai.mcp**: Provides `MCPServer`, `MCPServerHTTP`, and `MCPServerStdio` classes for MCP server transports

### Configuration Dependencies

None

## Error Handling

- Wrap low‑level exceptions in `RuntimeError` or `ValueError` with descriptive messages.

## Output Files

- `recipe_executor/llm_utils/mcp.py`


=== File: recipes/recipe_executor/components/logger/logger_docs.md ===
# Logger Component Usage

## Importing

```python
from recipe_executor.logger import init_logger
```

## Initialization

The Logger component provides a single function to initialize the logger. This function sets up the logging configuration, including log levels and file handlers.

```python
def init_logger(
    log_dir: str = "logs",
    stdio_log_level: str = "INFO"
) -> logging.Logger:
    """
    Initializes a logger that writes to stdout and to log files (debug/info/error).
    Clears existing logs on each run.

    Args:
        log_dir (str): Directory to store log files. Default is "logs".
        stdio_log_level (str): Log level for stdout. Default is "INFO".
            Options: "DEBUG", "INFO", "WARN", "ERROR".
            Note: This is not case-sensitive.
            If set to "DEBUG", all logs will be printed to stdout.
            If set to "INFO", only INFO and higher level logs will be printed to stdout.

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        Exception: If log directory cannot be created or log files cannot be opened.
    """
```

Examples:

```python
# Default usage
logger = init_logger(log_dir="custom/log/path")

# Enable debug logging to stdout
logger = init_logger(log_dir="custom/log/path", stdio_log_level="DEBUG")

# Example usage
logger.info("This is an info message")
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
2025-03-30 15:42:38.927 [INFO] (main.py:25) Starting Recipe Executor Tool
2025-03-30 15:42:38.928 [DEBUG](executor.py:42) Initializing executor
2025-03-30 15:42:38.930 [INFO] (executor.py:156) Executing recipe: recipes/my_recipe.json
2025-03-30 15:42:38.935 [ERROR] (executor.py:256) Recipe execution failed: Invalid step type
```

## Important Notes

- Logs are cleared (overwritten) on each run
- Debug logs can get large with detailed information
- The log directory is created if it doesn't exist
- The logger is thread-safe and can be used in multi-threaded applications


=== File: recipes/recipe_executor/components/logger/logger_spec.md ===
# Logger Component Specification

## Purpose

The Logger component provides a consistent logging interface. It initializes and configures logging, writes logs to appropriate files, and ensures that all components can log messages at different severity levels.

## Core Requirements

- Writes to both stdout and log files
- Allow configuration of the log directory and log levels
- Support different log levels (DEBUG, INFO, ERROR)
- Create separate log files for each level
- For stdout, set the log level to INFO
- Clear existing logs on each run to prevent unbounded growth
- Provide a consistent log format with timestamps, log level, source file, line number, and message
- Create log directories if they don't exist

## Implementation Considerations

- Ensure thread safety for concurrent logging
- Use Python's standard logging module directly
- Reset existing handlers to ensure consistent configuration
- Set up separate handlers for console and different log files
- Create the log directory if it doesn't exist
- Use mode="w" for file handlers to clear previous logs
- Use a custom formatter:
  - Log Format: `%(asctime)s.%(msecs)03d [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s`
  - Log Date Format: `%Y-%m-%d %H:%M:%S`

## Logging

- Debug: Log that the logger is being initialized, the log directory being created, and any errors encountered during initialization
- Info: Log that the logger has been initialized successfully

## Component Dependencies

### Internal Components

None

### External Libraries

- **logging**: Uses Python's standard logging module for core functionality

### Configuration Dependencies

None

## Error Handling

- Catch and report directory creation failures
- Handle file access permission issues
- Provide clear error messages for logging setup failures

## Output Files

- `recipe_executor/logger.py`


=== File: recipes/recipe_executor/components/main/main_docs.md ===
# Main Component Usage

## Command-Line Interface

The Recipe Executor is used from the command line. You invoke the `main` module with a recipe file and optional parameters. For example:

```bash
# Basic usage:
python -m recipe_executor.main recipes/my_recipe.json

# With a custom log directory:
python -m recipe_executor.main recipes/my_recipe.json --log-dir custom_logs

# With context values:
python -m recipe_executor.main recipes/my_recipe.json --context key1=value1 --context key2=value2

# With static configuration:
python -m recipe_executor.main recipes/my_recipe.json --config api_key=XYZ --config timeout=30
```

## Command-Line Arguments

The Main component supports these command-line arguments:

1. **`recipe_path`** (positional, required): Path to the recipe file to execute.
2. **`--log-dir`** (optional): Directory for log files (default: `"logs"`). If the directory does not exist, it will be created.
3. **`--context`** (optional, repeatable): Context artifact values as `key=value` pairs. You can specify this option multiple times.
4. **`--config`** (optional, repeatable): Static configuration values as `key=value` pairs, populated into context config. Useful for settings like MCP servers or API credentials.

## Context Parsing

If you provide context values via `--context`, the Main component will parse them into the execution context. For example:

```bash
# Given the arguments:
--context name=John --context age=30 --context active=true

# The resulting context artifacts will be:
{
    "name": "John",
    "age": "30",
    "active": "true"
}
```

_(All values are parsed as strings. It's up to individual steps to interpret types as needed.)_

## Exit Codes

Main uses exit codes to indicate outcome:

- `0` — Successful execution.
- `1` — An error occurred (e.g., invalid arguments, failure during recipe execution).

These codes can be used in shell scripts to handle success or failure of the recipe execution.

## Error Messages

Error messages and exceptions are written to standard error and also logged:

```python
# Example of an error message for a context format issue:
sys.stderr.write("Context Error: Invalid context format 'foo'\n")

# Example of logging an execution error (in logs and stderr):
logger.error("An error occurred during recipe execution: ...")
```

The stack trace for exceptions is output to stderr (via `traceback.format_exc()`) to aid in debugging issues directly from the console.

## Important Notes

- The main entry point is designed to be simple and minimal. It delegates the heavy lifting to the `Context` and `Executor` components.
- All steps in the executed recipe share the same context instance, which is created by Main from the provided context arguments.
- The Main component itself doesn't enforce any type of step ordering beyond what the recipe dictates; it simply invokes the Executor and waits for it to process the steps sequentially.
- Environment variables (for example, API keys for LLM steps) can be set in a `.env` file. Main will load this file at startup via `load_dotenv()`, making those values available to components that need them.
- Logging is configured at runtime when Main calls `init_logger`. The logs (including debug information and errors) are saved in the directory specified by `--log-dir`. Each run may append to these logs, so it's advisable to monitor or clean the log directory if running many recipes.


=== File: recipes/recipe_executor/components/main/main_spec.md ===
# Main Component Specification

## Purpose

The Main component serves as the command-line entry point for the Recipe Executor system. It parses command-line arguments, initializes the logger and context, invokes the executor to run the specified recipe, and handles top-level error reporting (exit codes and exceptions).

## Core Requirements

- Provide a command-line interface for executing recipes (accept recipe path and optional parameters).
- Load environment variables from a `.env` file at startup (using python-dotenv).
- Parse context values supplied via command-line arguments (`--context key=value`) into initial Context artifacts.
- Parse configuration values supplied via command-line arguments (`--config key=value`) into the Context `config` attribute.
- Initialize a logging system and direct log output to a specified directory.
- Create the Context and Executor instances and orchestrate the recipe execution by running an asyncio event loop to call `await Executor.execute` with the provided context.
- Handle successful completion by reporting execution time, and handle errors by logging and exiting with a non-zero status.

## Implementation Considerations

- Use Python's built-in `argparse` for argument parsing.
- Support multiple `--context` arguments by accumulating them into a list and parsing into a dictionary of artifacts.
- Support multiple `--config` arguments by accumulating them into a list and parsing into a dictionary of configuration values.
- Create a `Context` object using the parsed artifacts and configuration dictionaries (e.g., `Context(artifacts=artifacts, config=config)`).
- Use the `Executor` component to run the recipe, passing the context object to it.
- Implement asynchronous execution:
  - Define an async `main_async` function that performs the core execution logic
  - In the `main` entry point, run this async function using `asyncio.run(main_async())`
  - This enables proper async/await usage throughout the execution pipeline
- Keep the main logic linear and straightforward: parse inputs, setup context and logger, run executor, handle errors. Avoid additional complexity or long-running logic in Main; delegate to Executor and other components.
- Ensure that any exception raised during execution is caught and results in a clean error message to `stderr` and an appropriate exit code (`1` for failure).
- Maintain minimal state in Main (it should primarily act as a procedural script). Do not retain references to context or executor after execution beyond what’s needed for logging.
- Follow the project philosophy of simplicity: avoid global state, singletons, or complex initialization in the Main component.

## Component Dependencies

### Internal Components

- **Context**: Creates the Context object to hold initial artifacts parsed from CLI.
- **Executor**: Uses the Executor to run the specified recipe
- **Logger**: Uses the Logger component (via `init_logger`) to initialize logging for the execution.

### External Libraries

- **python-dotenv**: Loads environment variables from a file at startup.
- **argparse**: Parses command-line arguments.
- **asyncio**: Manages the event loop for asynchronous execution.

### Configuration Dependencies

- **Environment File** - The presence of a `.env` file is optional; if present, it's loaded for environment configuration (like API keys for steps, etc., though Main itself mainly cares about logging configuration if any).
- **Logging Directory** - Uses the `--log-dir` argument (default "logs") to determine where log files are written.

## Logging

- Debug: Log the start of execution, the parsed arguments, and the initial context artifact dictionary for traceability.
- Info: Log high-level events such as "Starting Recipe Executor Tool", the recipe being executed, and a success message with execution time.

## Error Handling

- Incorrect context argument format (missing `=`) results in a `ValueError` from `parse_context`; Main catches this and outputs a clear error message to `stderr` before exiting with code 1.
- Failures in logger initialization (e.g., invalid log directory permissions) are caught and cause the program to exit with an error message.
- Any exception during Executor execution is caught in Main; it logs the error and ensures the program exits with a non-zero status.
- Main distinguishes between normal execution termination and error termination by exit codes (0 for success, 1 for any failure case).
- After handling an error, Main uses `sys.exit(1)` to terminate the process, as no further steps should be taken.

## Output Files

- `recipe_executor/main.py`


=== File: recipes/recipe_executor/components/models/models_docs.md ===
# Models Component Usage

## Importing

```python
from recipe_executor.models import (
    FileSpec,
    RecipeStep,
    Recipe
)
```

## File Models

### FileSpec

Represents a single file:

```python
class FileSpec(BaseModel):
    """Represents a single file to be generated.

    Attributes:
        path: Relative path where the file should be written.
        content: The content of the file.
    """

    path: str
    content: Union[str, Dict[str, Any], List[Dict[str, Any]]]
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

## Recipe Models

### RecipeStep

Represents a single step in a recipe:

```python
class RecipeStep(BaseModel):
    """A single step in a recipe.

    Attributes:
        type: The type of the recipe step.
        config: Dictionary containing configuration for the step.
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
            type="read_files",
            config={"path": "specs/component_spec.md", "content_key": "spec"}
        ),
        RecipeStep(
            type="llm_generate",
            config={
                "prompt": "Generate code for: {{spec}}",
                "model": "{{model|default:'openai/o4-mini'}}",
                "output_format": "files",
                "output_key": "code_result"
            }
        ),
        RecipeStep(
            type="write_files",
            config={"files_key": "code_result", "root": "./output"}
        )
    ]
)
```

## Instantiation from JSON

Models can be instantiated from JSON strings or dictionaries:

```python
# From JSON string
json_data = '{"path": "src/utils.py", "content": "def hello_world():\\n    print(\'Hello, world!\')"}'
file = FileSpec.model_validate_json(json_data)
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...

# From dictionary
dict_data = {
    "path": "src/utils.py",
    "content": "def hello_world():\n    print('Hello, world!')"
}
file = FileSpec.model_validate(dict_data)
print(file.path)      # src/utils.py
print(file.content)   # def hello_world():...
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

- Models can be converted to dictionaries with `.model_dump()` method
- Models can be created from dictionaries with `Model.model_validate(dict_data)`
- Models can be converted to JSON with `.model_dump_json()` method
- Models can be created from JSON with `Model.model_validate_json(json_data)`


=== File: recipes/recipe_executor/components/models/models_spec.md ===
# Models Component Specification

## Purpose

The Models component defines the core data structures used throughout the Recipe Executor system. It provides Pydantic models for validating and structuring data, including recipe steps, and files.

## Core Requirements

- Define consistent data structures for files
- Provide configuration models for various step types
- Support recipe structure validation
- Leverage Pydantic for schema validation and documentation
- Include clear type hints and docstrings

## Implementation Considerations

- Use Pydantic `BaseModel` for all data structures
- Keep models focused and minimal
- Provide sensible defaults where appropriate
- Use descriptive field names and docstrings
- Focus on essential fields without over-engineering

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

- **pydantic**: Uses Pydantic for schema validation and model definition

### Configuration Dependencies

None

## Output Files

- `recipe_executor/models.py`


=== File: recipes/recipe_executor/components/protocols/protocols_docs.md ===
# Protocols Component Usage

The Protocols component provides **interface definitions** for key parts of the Recipe Executor system. By defining formal contracts (`Protocol` classes) for the `Executor`, `Context`, and `Step`, this component decouples implementations from each other and serves as the single source of truth for how components interact. All components that implement or use these interfaces should refer to the `Protocols` component to ensure consistency. Where the concrete implementations are needed, consider importing them inside the method or class that requires them, rather than at the top of the file. This helps to prevent circular imports and keeps the code clean.

## Provided Interfaces

### `ContextProtocol`

The `ContextProtocol` defines the interface for the context object used throughout the Recipe Executor system. It specifies methods for accessing, modifying, and managing context data. This includes standard dictionary-like operations (like `__getitem__`, `__setitem__`, etc.) as well as additional methods like `clone`, `dict`, and `json` for deep copying and serialization. In addition, it provides methods for managing configuration data, such as `get_config` and `set_config`.

```python
from typing import Protocol, Dict, Any, Iterator
class ContextProtocol(Protocol):
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
```

### `StepProtocol`

The `StepProtocol` defines the interface for steps within a recipe. Each step must implement an `execute` method that takes a context (any `ContextProtocol` implementation) and performs its designated action. This allows for a consistent way to execute steps, regardless of their specific implementations.

```python
from typing import Protocol
class StepProtocol(Protocol):
    def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
        ...

    def execute(self, context: ContextProtocol) -> None:
        ...
```

### `ExecutorProtocol`

The `ExecutorProtocol` defines the interface for the executor component, which is responsible for executing recipes. It specifies an `execute` method that takes a recipe (which can be a string, path, or a Recipe object) and a context. This allows the executor to run recipes in a consistent manner, regardless of their specific implementations.

```python
from typing import Protocol
from recipe_executor.models import Recipe

class ExecutorProtocol(Protocol):
    def __init__(self, logger: logging.Logger) -> None:
        ...

    async def execute(
        self,
        recipe: Union[str, Path, Recipe],
        context: ContextProtocol,
    ) -> None:
        ...
```

## How to Use These Protocols

Developers should **import the protocol interfaces** when writing type hints or designing new components. For example, to annotate variables or function parameters:

```python
from recipe_executor import Executor, Context
from recipe_executor.protocols import ExecutorProtocol, ContextProtocol

context: ContextProtocol = Context()
executor: ExecutorProtocol = Executor(logger)
executor.execute("path/to/recipe.json", context)
```

In this example, `Context` is the concrete implementation provided by the system (which implements `ContextProtocol`), and `Executor` is the concrete executor implementing `ExecutorProtocol`. By annotating them as `ContextProtocol` and `ExecutorProtocol`, we emphasize that our code relies only on the defined interface, not a specific implementation. This is optional for running the code (the system will work with or without the annotations), but it is useful for clarity and static type checking.

```python
from recipe_executor.protocols import ContextProtocol, ExecutorProtocol

class MyCustomExecutor(ExecutorProtocol):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def execute(self, recipe: str, context: ContextProtocol) -> None:
        # Custom implementation
        pass
```

In this example, `MyCustomExecutor` implements the `ExecutorProtocol`, ensuring it adheres to the expected interface. This allows it to be used interchangeably with any other executor that also implements `ExecutorProtocol`.

## Implementation Notes for Developers

- **For Implementers**: When creating a new Context or Executor implementation (or any new Step), ensure it provides all methods defined in the corresponding protocol. It is recommended to inherit from the protocol class to ensure compliance. This way, you can be sure that your implementation will work seamlessly with any code that relies on the protocol.

- **For Consumers**: If you use the protocols as the type hints in your code, you can be sure that your code will work with any implementation of the protocol. This allows for greater flexibility and easier testing, as you can swap out different implementations without changing the code that uses them.

- **Decoupling and Cycle Prevention**: By using these protocols, components like the Executor and steps do not need to import each other's concrete classes. This breaks import cycles (for example, steps can call executor functionality through `ExecutorProtocol` without a direct import of the Executor class). The Protocols component thus centralizes interface knowledge: it owns the definitions of `execute` methods and context operations that others rely on.

All developers and AI recipes should reference **this protocols documentation** when implementing or using components. This ensures that all components are consistent and adhere to the same interface definitions, enables decoupling, and prevents import cycles. It also allows for easier testing and swapping of implementations, as all components can be treated as interchangeable as long as they adhere to the defined protocols.


=== File: recipes/recipe_executor/components/protocols/protocols_spec.md ===
# Protocols Component Specification

## Purpose

The Protocols component defines the core interfaces for the Recipe Executor system. It provides a set of protocols that standardize the interactions between components, ensuring loose coupling and clear contracts for behavior. This allows for flexible implementations and easy integration of new components without modifying existing code.

## Core Requirements

- Define a `ContextProtocol` that captures the required behaviors of the Context (dictionary-like access, retrieval, iteration, cloning).
- Define a `StepProtocol` that captures the execution interface for any step (the async `execute(context)` method signature).
- Define an `ExecutorProtocol` that captures the interface of the executor (the async `execute(recipe, context)` method signature).
- Support asynchronous execution throughout the system to enable non-blocking I/O operations.
- Ensure these protocols are the single source of truth for their respective contracts, referenced throughout the codebase for type annotations and documentation.
- Eliminate direct references to concrete classes (e.g., `Context` or `Executor`) in other components’ interfaces by using these protocol definitions, thereby avoiding circular dependencies.
- Follow the project's minimalist design philosophy: interfaces should be concise, containing only what is necessary for inter-component communication.

## Implementation Considerations

- Use Python's `typing.Protocol` to define interfaces in a structural subtyping manner. This allows classes to implement the protocols without explicit inheritance, maintaining loose coupling.
- Mark protocol interfaces with `@runtime_checkable` to allow runtime enforcement (e.g., in tests) if needed, without impacting normal execution.
- See the `protocols_docs.md` file for detailed documentation on each protocol, including method signatures, expected behaviors, and examples of usage. This file serves as the authoritative reference for developers implementing or using these protocols.
- No actual business logic or data storage should exist in `protocols.py`; it strictly contains interface definitions with `...` (ellipsis) as method bodies. This keeps it aligned with the "contracts only" role of the component.
- Ensure naming and signatures exactly match those used in concrete classes to avoid confusion. For example, `ContextProtocol.clone()` returns a `ContextProtocol` to allow flexibility in context implementations.
- Keep the protocols in a single file (`protocols.py`) at the root of the package (no sub-package), consistent with single-file component convention. This file becomes a lightweight dependency for any module that needs the interfaces.

## Logging

- None

## Dependency Integration Considerations

### Internal Components

- **Models**: The `Recipe` class is used in the `ExecutorProtocol` to define the type of the recipe parameter in the `execute` method.

### External Libraries

- **typing**: Uses Python's built-in `typing` module (particularly `Protocol` and related features) to define structural interfaces.

### Configuration Dependencies

- None

## Error Handling

- None

## Output Files

- `recipe_executor/protocols.py`


=== File: recipes/recipe_executor/components/steps/base/base_docs.md ===
# Steps Base Component Usage

## Importing

To use the `BaseStep` and `StepConfig` classes in your custom step implementations, you will need to import them from the `recipe_executor.steps.base` module. Here’s how you can do that:

```python
from recipe_executor.steps.base import BaseStep, StepConfig
```

## Defining a New Step (Example)

To illustrate how `BaseStep` is used, let's say you want to create a new step type called `"EchoStep"` that simply logs a message:

1. **Define the Configuration**: Subclass `StepConfig` to define any inputs the step needs. If none are required, you could even use `StepConfig` as is, but we'll define one for example:

   ```python
   class EchoConfig(StepConfig):
       message: str
   ```

   This uses Pydantic to require a `message` field for the step.

2. **Define the Step Class**: Subclass `BaseStep` with the config type and implement `execute`:

   ```python
   class EchoStep(BaseStep[EchoConfig]):
       def __init__(self, logger: logging.Logger, config: Dict[str, Any]) -> None:
           super().__init__(logger, EchoConfig(**config))

       async def execute(self, context: ContextProtocol) -> None:
           # Simply log the message
           self.logger.info(f"Echo: {self.config.message}")
   ```

3. **Register the Step**: Finally, to use `EchoStep` in recipes, add it to the step registry:

   ```python
   from recipe_executor.steps.registry import STEP_REGISTRY
   STEP_REGISTRY["echo"] = EchoStep
   ```

Now, any recipe with a step like `{"type": "echo", "config": {"message": "Hello World"}}` will use `EchoStep`.

## Important Notes

- **Inheriting BaseStep**: All step implementations **must** inherit from `BaseStep` and implement the `execute` method.
- **Configuration Validation**: Using Pydantic `StepConfig` for your step’s configuration is highly recommended. It will automatically validate types and required fields. In the example above, if a recipe is missing the `"message"` field or if it's not a string, the creation of `EchoConfig` would raise an error, preventing execution with bad config.
- **Context Usage**: Steps interact with the execution context via the interface methods defined in `ContextProtocol`. For example, a step can do `value = context.get("some_key")` or `context["result"] = data`.
- **Logging**: Each step gets a logger (`self.logger`). Use it to log important events or data within the step.
- **BaseStep Utility**: Aside from providing the structure, `BaseStep` doesn't interfere with your step logic. You control what happens in `execute`. However, because `BaseStep` takes care of storing config and logger, you should always call its `__init__` in your step’s constructor (as shown with `super().__init__`). This ensures the config is properly parsed and the logger is set up.
- **Step Lifecycle**: There is no explicit "tear down" method for steps. If your step allocates resources (files, network connections, etc.), you should handle those within the step itself (and possibly in the `finally` block or context managers inside `execute`). Each step instance is short-lived (used only for one execution and then discarded).
- **Adhering to StepProtocol**: By following the pattern above, your custom step automatically adheres to `StepProtocol` because it implements `execute(context: ContextProtocol)`.


=== File: recipes/recipe_executor/components/steps/base/base_spec.md ===
# Steps Base Component Specification

## Purpose

The purpose of the Steps Base component is to provide a foundational structure for creating and executing steps in the recipe executor. This component defines the base class for all steps, ensuring that they adhere to a consistent interface and can be easily integrated into the overall execution framework.

## Core Requirements

- Provide a base class (`BaseStep`) that all step classes will inherit from.
- Provide a base configuration model class (`StepConfig`) using Pydantic for validation of step-specific configuration.
- Enforce a consistent interface for step execution (each step must implement an async `execute(context)` method).
- Utilize generics to allow `BaseStep` to be typed with a specific `StepConfig` subclass for that step, enabling type-safe access to configuration attributes within step implementations.
- Integrate logging into steps, so each step has a logger to record its actions.
- Keep the base step minimal—only define structure and common functionality, deferring actual execution logic to subclasses.

## Implementation Considerations

- **StepConfig (Pydantic Model)**: Define a `StepConfig` class as a subclass of `BaseModel`. This serves as a base for all configurations. By default, it has no predefined fields (each step will define its own fields by extending this model). Using Pydantic ensures that step configurations are validated and parsed (e.g., types are enforced, missing fields are caught) when constructing the step.
- **Generic Config Type**: Use a `TypeVar` and generic class definition (`BaseStep[StepConfigType]`) so that each step class can specify what config type it expects. For instance, a `PrintStep` could be `BaseStep[PrintConfig]`. This allows the step implementation to access `self.config` with the correct type.
  - Example: `StepConfigType = TypeVar("StepConfigType", bound=StepConfig)`.
- **BaseStep Class**:
  - Inherit from `Generic[StepConfigType]` to support the generic config typing.
  - Provide an `__init__` that stores the `config` (of type StepConfigType) and a logger. This logger is used by steps to log their internal operations.
  - The `__init__` should log a debug message indicating the class name and config with which the step was initialized. This is useful for tracing execution in logs.
  - Declare a `async execute(context: ContextProtocol) -> None` method. This is the core contract: every step must implement this method as an async method.
  - `BaseStep` should not provide any implementation (aside from possibly a placeholder raise of NotImplementedError, which is a safeguard).
- **Logging in Steps**: Steps can use `self.logger` to log debug or info messages.
- **Step Interface Protocol**: The `BaseStep` (and by extension all steps) fulfill the `StepProtocol` as defined in the Protocols component.

## Logging

- Debug: BaseStep’s `__init__` logs a message when a step is initialized (including the provided configuration).

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for the type of the context parameter in `execute`. Also, by design, `BaseStep` and its subclasses implement `StepProtocol` as defined in the Protocols component.
- **Logger**: Uses the logger for logging messages. The logger is passed to the step during initialization.

### External Libraries

- **typing**: Uses `TypeVar` and `Generic` for typing the BaseStep with its config model.

### Configuration Dependencies

- None

## Error Handling

- BaseStep does not implement run-time error handling. It defines the interface and common setup. Any exceptions that occur within an actual step's `execute` method will propagate up unless handled inside that step.
- In the unlikely case that `BaseStep.execute` is called (e.g., via `super()` call from a subclass that doesn't override it), it will raise `NotImplementedError`, clearly indicating that the subclass should implement it. This is a safeguard and developmental aid.

## Output Files

- `recipe_executor/steps/base.py`


=== File: recipes/recipe_executor/components/steps/conditional/conditional_docs.md ===
# Conditional Step Documentation

## Importing

```python
from recipe_executor.steps.conditional import ConditionalStep
```

## Configuration

The ConditionalStep is configured with a condition expression and step branches to execute based on the evaluation result:

```python
class ConditionalConfig(StepConfig):
    """
    Configuration for ConditionalStep.

    Fields:
        condition: Expression string to evaluate against the context.
        if_true: Optional steps to execute when the condition evaluates to true.
        if_false: Optional steps to execute when the condition evaluates to false.
    """
    condition: str
    if_true: Optional[Dict[str, Any]] = None
    if_false: Optional[Dict[str, Any]] = None
```

## Step Registration

The ConditionalStep is registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.conditional import ConditionalStep

STEP_REGISTRY["conditional"] = ConditionalStep
```

## Basic Usage in Recipes

The ConditionalStep allows you to branch execution paths based on evaluating expressions:

```json
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "{{ analysis_result.needs_splitting }}",
        "if_true": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/blueprint_generator/recipes/split_project.json"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/blueprint_generator/recipes/process_single_component.json"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## Supported Expression Types

### Context Value Checks

```json
"condition": "{{key}} == 'value'"
"condition": "{{nested.key}} != null"
"condition": "{{count}} > 0"
"condition": "{{is_ready}}"
```

### File Operations

```json
"condition": "file_exists('{{output_dir}}/specs/initial_project_spec.md')"
"condition": "all_files_exist(['file1.md', 'file2.md'])"
"condition": "file_is_newer('source.txt', 'output.txt')"
```

### Logical Operations

```json
"condition": "and({{a}}, {{b}})"
"condition": "or(file_exists('file1.md'), file_exists('file2.md'))"
"condition": "not({{skip_processing}})"
```

### Template Variables in Expressions

```json
"condition": "file_exists('{{output_dir}}/components/{{component_id}}_spec.md')"
```

## Common Use Cases

### Conditional Recipe Execution

```json
{
  "type": "conditional",
  "config": {
    "condition": "{{ step_complete }}",
    "if_true": {
      "steps": [
        {
          "type": "execute_recipe",
          "config": {
            "recipe_path": "recipes/next_step.json"
          }
        }
      ]
    }
  }
}
```

### File Existence Checking

```json
{
  "type": "conditional",
  "config": {
    "condition": "file_exists('{{ output_path }}')",
    "if_true": {
      "steps": [
        /* Steps to handle existing file */
      ]
    },
    "if_false": {
      "steps": [
        /* Steps to generate the file */
      ]
    }
  }
}
```

### Complex Condition

```json
{
  "type": "conditional",
  "config": {
    "condition": "and({{ should_process }}, or(file_exists('input1.md'), file_exists('input2.md')))",
    "if_true": {
      "steps": [
        /* Processing steps */
      ]
    }
  }
}
```

## Utility Recipe Example

```json
// check_and_process.json
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "all_files_exist(['{{ input_file }}', '{{ config_file }}'])",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ input_file }}",
                "content_key": "input_content"
              }
            }
            /* More processing steps */
          ]
        },
        "if_false": {
          "steps": [
            /* Steps to handle missing files */
          ]
        }
      }
    }
  ]
}
```

## Important Notes

- Expressions are evaluated in the context of the current recipe execution
- Template variables in the condition string are rendered before evaluation
- Both `if_true` and `if_false` branches are optional and can be omitted for simple checks
- When a branch doesn't exist for the condition result, that path is simply skipped
- Nested conditional steps are supported for complex decision trees
- The conditional step is specifically designed to reduce unnecessary LLM calls in recipes


=== File: recipes/recipe_executor/components/steps/conditional/conditional_spec.md ===
# Conditional Step Type Specification

## Purpose

The Conditional step enables branching execution paths in recipes based on evaluating expressions. It serves as a key building block for creating utility recipes or non-LLM flow control.

## Core Requirements

- Evaluate conditional expressions against the current context state
- Support multiple condition types including:
  - Context value checks
  - File existence checks
  - Comparison operations
- Execute different sets of steps based on the result of the condition evaluation
- Support nested conditions and complex logical operations
- Provide clear error messages when expressions are invalid

## Implementation Considerations

- If expression is already a boolean or a string that can be evaluated to a boolean, use it directly as it may have been rendered by the template engine
- Include conversion of "true" and "false" strings to boolean values in any safe globals list
- Keep expression evaluation lightweight and focused on common needs
- Allow for direct access to context values via expression syntax
- Make error messages helpful for debugging invalid expressions
- Process nested step configurations in a recursive manner
- Ensure consistent logging of condition results and execution paths
- Properly handle function-like logical operations that conflict with Python keywords

## Logging

- Debug: Log the condition being evaluated, its result, and which branch is taken
- Info: None

## Component Dependencies

### Internal Components

- **Context**: Uses context to access values for condition evaluation
- **Utils/Templates**: Uses template rendering for condition strings with variables

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Provide clear error messages for invalid expressions
- Handle missing context values gracefully (typically evaluating to false)
- Properly propagate errors from executed step branches

## Output Files

- `recipe_executor/steps/conditional.py`


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_docs.md ===
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
      "config": {
        "recipe_path": "recipes/sub_recipe.json"
      }
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
      "config": {
        "recipe_path": "recipes/generate_component.json",
        "context_overrides": {
          "component_name": "Utils",
          "output_dir": "output/components/utils"
        }
      }
    }
  ]
}
```

## Template-Based Values

Both the `recipe_path` and `context_overrides` can include template variables:

```json
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/{{recipe_type}}/{{component_id}}.json",
        "context_overrides": {
          "component_name": "{{component_display_name}}",
          "output_dir": "output/components/{{component_id}}"
        }
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
      "type": "read_files",
      "config": {
        "path": "specs/project_spec.md",
        "content_key": "project_spec"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/parse_project.json",
        "context_overrides": {
          "spec": "{{project_spec}}"
        }
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/generate_components.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/assemble_project.json"
      }
    }
  ]
}
```

## Common Use Cases

**Component Generation**:

```json
{
  "type": "execute_recipe",
  "config": {
    "recipe_path": "recipes/generate_component.json",
    "context_overrides": {
      "component_id": "utils",
      "component_name": "Utils Component"
    }
  }
}
```

**Template-Based Recipes**:

```json
{
  "type": "execute_recipe",
  "config": {
    "recipe_path": "recipes/component_template.json",
    "context_overrides": {
      "template_type": "create",
      "component_id": "{{component_id}}"
    }
  }
}
```

**Multi-Step Workflows**:

```json
{
  "type": "execute_recipe",
  "config": {
    "recipe_path": "recipes/workflow/{{workflow_name}}.json"
  }
}
```

## Important Notes

- The sub-recipe receives the **same context object** as the parent recipe (the shared context implements ContextProtocol)
- Context overrides are applied **before** sub-recipe execution
- Changes made to the context by the sub-recipe persist after it completes
- Template variables in both `recipe_path` and `context_overrides` are resolved before execution
- Sub-recipes can execute their own sub-recipes (nested execution)


=== File: recipes/recipe_executor/components/steps/execute_recipe/execute_recipe_spec.md ===
# ExecuteRecipeStep Component Specification

## Purpose

The ExecuteRecipeStep component enables recipes to execute other recipes as sub-recipes, allowing for modular composition and reuse. It serves as a key mechanism for building complex workflows from simpler modules, following the building-block inspired approach to recipe construction.

## Core Requirements

- Execute sub-recipes from a specified file path
- Share the current execution context with sub-recipes
- Support context overrides for sub-recipe execution
- Apply template rendering to recipe paths and context overrides
- Include appropriate logging for sub-recipe execution
- Follow a minimal design with clear error handling

## Implementation Considerations

- Use the same executor instance for sub-recipe execution
- Apply context overrides before sub-recipe execution
- Use template rendering for all dynamic values
- Keep the implementation simple and focused on a single responsibility
- Log detailed information about sub-recipe execution

## Implementation Hints

- Import the `Executor` within the `execute` method to avoid circular dependencies

## Logging

- Debug: None
- Info: Log the path of the sub-recipe being executed at both the start and end of execution

## Component Dependencies

### Internal Components

- **Protocols** – (Required) Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Interface** – (Required) Implements the step execution interface (via the StepProtocol)
- **Context** – (Required) Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor** – (Required) Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils/Templates** – (Required) Uses render_template for dynamic content resolution in paths and context overrides

### External Libraries

None

### Configuration Dependencies

None

## Error Handling

- Validate that the sub-recipe file exists
- Propagate errors from sub-recipe execution
- Log sub-recipe execution start and completion
- Include the sub-recipe path in error messages for debugging

## Output Files

- `recipe_executor/steps/execute_recipe.py`


=== File: recipes/recipe_executor/components/steps/llm_generate/llm_generate_docs.md ===
# LLMGenerateStep Component Usage

## Importing

```python
from recipe_executor.steps.llm_generate import LLMGenerateStep, LLMGenerateConfig
```

## Configuration

The LLMGenerateStep is configured with a LLMGenerateConfig:

```python
class LLMGenerateConfig(StepConfig):
    """
    Config for LLMGenerateStep.

    Fields:
        prompt: The prompt to send to the LLM (templated beforehand).
        model: The model identifier to use (provider/model_name format).
        max_tokens: The maximum number of tokens for the LLM response.
        mcp_servers: List of MCP servers for access to tools.
        output_format: The format of the LLM output (text, files, or JSON).
            - text: Plain text output.
            - files: List of files generated by the LLM.
            - object: Object based on the provided JSON schema.
            - list: List of items based on the provided JSON schema.
        output_key: The name under which to store the LLM output in context.
    """

    prompt: str
    model: str = "openai/gpt-4o"
    max_tokens: Optional[Union[str, int]] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = None
    output_format: "text" | "files" | Dict[str, Any]
    output_key: str = "llm_output"
```

## Basic Usage in Recipes

The LLMGenerateStep can be used in recipes via the `llm_generate` step type:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "What is the weather in Redmond, WA today?",
        "model": "openai/o4-mini",
        "mcp_servers": [
          {
            "url": "http://localhost:3001/sse"
          }
        ],
        "output_format": "text",
        "output_key": "capital_result"
      }
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
      "type": "read_files",
      "config": {
        "path": "specs/component_spec.md",
        "content_key": "component_spec_content"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Based on the following specification, generate python code for a component:\n\n{{component_spec_content}}",
        "model": "{{model|default:'openai/o4-mini'}}",
        "output_format": "files",
        "output_key": "component_code_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        # Prefer using "files_key" over "files" when using LLMGenerateStep with "files" output format
        "files_key": "component_code_files",
        "root": "./output"
      }
    }
  ]
}
```

## Dynamic Output Keys

The output key can be templated to create dynamic storage locations:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a JSON object with user details.",
        "model": "{{model|default:'openai/o4-mini'}}",
        "output_format": {
          "type": "object",
          "properties": {
            "user": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string"
                },
                "age": {
                  "type": "integer"
                }
              },
              "required": ["name", "age"]
            }
          }
        },
        "output_key": "user_details_{{name}}"
      }
    }
  ]
}
```

## MCP Integration

The LLMGenerateStep can integrate with MCP servers for tool access. The MCP servers can be specified in the `mcp_servers` field of the configuration. The LLM will use these servers to access tools during the generation process.

### MCP Server Configuration Formats

The MCP server configuration can be specified in two formats:

- **HTTP**: For HTTP-based MCP servers, provide:

  - `url`: The URL of the MCP server.
  - `headers`: Optional dictionary of headers to include in the requests.

Example:

```json
{
  "mcp_servers": [
    {
      "url": "http://localhost:3001/sse",
      "headers": {
        "Authorization": "{{token}}"
      }
    }
  ]
}
```

- **STDIO**: For STDIO-based MCP servers, provide:

  - `command`: The command to run the MCP server.
  - `args`: List of arguments for the command.
  - `env`: Optional dictionary of environment variables for the command.
  - `cwd`: Optional working directory for the command.

Example:

```json
{
  "mcp_servers": [
    {
      "command": "python",
      "args": ["-m", "/path/to/mcp_server.py"],
      "env": {
        "MCP_TOKEN": "{{token}}"
      },
      "cwd": "/path/to/mcp"
    }
  ]
}
```

## LLM Output Formats

The LLM can return different formats based on the `output_format` parameter:

- **"text"**: Returns a plain text output.
- **"files"**: Returns a list of `FileSpec` objects, this is provided as a convenience due to the common use case of generating files from LLMs.
- **object**: Returns a JSON object based on the provided JSON schema. The schema is validated before the LLM call, and if invalid, the step will fail.
- **list**: Returns a list of items based on the provided JSON schema. The schema is validated before the LLM call, and if invalid, the step will fail.

### Text Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "What is the capital of France?",
    "model": "openai/gpt-4o",
    "max_tokens": 100,
    "output_format": "text",
    "output_key": "capital_result"
  }
}
```

Context after execution:

```json
{
  "capital_result": "The capital of France is Paris."
}
```

### Files Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "Generate Python files for a simple calculator.",
    "model": "openai/o4-mini",
    "output_format": "files",
    "output_key": "calculator_files"
  }
}
```

Context after execution:

```json
{
  "calculator_files": [
    {
      "path": "calculator.py",
      "content": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b"
    },
    {
      "path": "test_calculator.py",
      "content": "import calculator\n\ndef test_add():\n    assert calculator.add(1, 2) == 3\n\ndef test_subtract():\n    assert calculator.subtract(2, 1) == 1"
    }
  ]
}
```

### Object Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "Generate a JSON object with user details.",
    "model": "openai/o4-mini",
    "output_format": {
      "type": "object",
      "properties": {
        "user": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "age": {
              "type": "integer"
            }
          },
          "required": ["name", "age"]
        }
      }
    },
    "output_key": "user_details"
  }
}
```

Context after execution:

```json
{
  "user_details": {
    "user": {
      "name": "Alice",
      "age": 30
    }
  }
}
```

### List Example

Request:

```json
{
  "type": "llm_generate",
  "config": {
    "prompt": "Extract the list of users from this document: {{document_content}}.",
    "model": "openai/o4-mini",
    "output_format": [
      {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "age": {
            "type": "integer"
          }
        },
        "required": ["name", "age"]
      }
    ],
    "output_key": "user_details"
  }
}
```

Context after execution:

```json
{
  "user_details": [
    {
      "name": "Alice",
      "age": 30
    },
    {
      "name": "Bob",
      "age": 25
    }
  ]
}
```


=== File: recipes/recipe_executor/components/steps/llm_generate/llm_generate_spec.md ===
# LLMGenerateStep Component Specification

## Purpose

The LLMGenerateStep component enables recipes to generate content using large language models (LLMs). It serves as the bridge between recipes and the LLM subsystem, handling prompt templating, model selection, MCP server tools, structured output, and storing generation results in the execution context.

## Core Requirements

- Process prompt templates using context data
- Support configurable model selection
- Support MCP server configuration for tool access
- Support multiple output formats (text, files, object, list)
- Call LLMs to generate content
- Store generated results in the context with dynamic key support
- Include appropriate logging for LLM operations

## Implementation Considerations

- Use `render_template` for templating prompts, model identifiers, mcp server configs, and output key
- Convert any MCP Server configurations to `MCPServer` instances (via `get_mcp_server`) to pass as `mcp_servers` to the LLM component
- Accept a string for `max_tokens` and convert it to an integer to pass to the LLM component
- In order to support dyanmic output keys, set the result type to `Any` prior to determining the output format and then set the output key immediately after the LLM call
- If `output_format` is an object (JSON schema) or list:
  - Use `json_object_to_pydantic_model` to create a dynamic Pydantic model from the JSON schema
  - Pass the dynamic model to the LLM call as the `output_type` parameter
  - After receiving the results, convert the output to a Dict[str, Any] and store it in the context
- If `output_format` is a list:
  - Wrap the list in an object with a root key `items`:
    ```python
    object_schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": // Define the item schema here
            }
        }
    }
    ```
  - Use `json_object_to_pydantic_model` to create a dynamic Pydantic model from the JSON schema
  - Pass the dynamic model to the LLM call as the `output_type` parameter
  - After receiving the results, convert the output to a Dict[str, Any] and store the `items` list in the context
- If `output_format` is "files":
  - Pass the following `FileSpecCollection` model to the LLM call:
    ```python
    class FileSpecCollection(BaseModel):
        files: List[FileSpec]
    ```
  - After receiving the results, store the `files` value (not the entire `FileSpecCollection`) in the context
- Instantiate the `LLM` component with optional MCP servers from context config:
  ```python
  mcp_server_configs = context.get_config().get("mcp_servers", [])
  mcp_servers = [get_mcp_server(logger=self.logger, config=mcp_server_config) for mcp_server_config in mcp_server_configs]
  llm = LLM(logger, model=config.model, mcp_servers=mcp_servers)
  ```
- Use `await llm.generate(prompt, output_type=...)` to perform the generation call

## Logging

- Debug: Log when an LLM call is being made (details of the call are handled by the LLM component)
- Info: None

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol for context data access and StepProtocol for the step interface (decouples from concrete Context and BaseStep classes)
- **Step Interface**: Implements the step behavior via `StepProtocol`
- **Context**: Uses a context implementing `ContextProtocol` to retrieve input values and store generation output
- **Models**: Uses the `FileSpec` model for file generation output
- **LLM**: Uses the LLM component class `LLM` from `llm_utils.llm` to interact with language models and optional MCP servers
- **MCP**: Uses the `get_mcp_server` function to convert MCP server configurations to `MCPServer` instances
- **Utils/Models**: Uses `json_object_to_pydantic_model` to create dynamic Pydantic models from JSON objects, after receiving the results from the LLM use `.model_dump()` to convert the Pydantic model to a dictionary
- **Utils/Templates**: Uses `render_template` for dynamic content resolution in prompts and model identifiers

### External Libraries

- **Pydantic**: For BaseModel creation

### Configuration Dependencies

None

## Error Handling

- Handle LLM-related errors gracefully
- Log LLM call failures with meaningful context
- Ensure proper error propagation for debugging
- Validate configuration before making LLM calls

## Output Files

- `recipe_executor/steps/llm_generate.py`


=== File: recipes/recipe_executor/components/steps/loop/loop_docs.md ===
# LoopStep Component Usage

The **LoopStep** component allows you to iterate over a collection of items and execute specified sub-steps for each item. It is useful for processing lists or arrays of data in a structured manner.

## Importing

Import the LoopStep and its configuration:

```python
from recipe_executor.steps.loop import LoopStep, LoopStepConfig
```

## Configuration

The LoopStep is configured via a `LoopStepConfig` object. This configuration defines the collection to iterate over, the key for the current item, the sub-steps to execute, and how to handle results.

```python
class LoopStepConfig(StepConfig):
    """
    Configuration for LoopStep.

    Fields:
        items: Key in the context containing the collection to iterate over. Supports template variable syntax
               with dot notation for accessing nested data structures (e.g., "data.items", "response.results").
        item_key: Key to use when storing the current item in each iteration's context.
        max_concurrency: Maximum number of items to process concurrently.
                         Default = 1 means process items sequentially (no parallelism).
                         n > 1 means process up to n items at a time.
                         0 means no explicit limit (all items may run at once, limited only by system resources).
        delay: Time in seconds to wait between starting each parallel task.
               Default = 0 means no delay (all allowed items start immediately).
        substeps: List of sub-step configurations to execute for each item.
        result_key: Key to store the collection of results in the context.
        fail_fast: Whether to stop processing on the first error.
    """

    items: str
    item_key: str
    max_concurrency: int = 1
    delay: float = 0.0
    substeps: List[Dict[str, Any]]
    result_key: str
    fail_fast: bool = True
```

## Parallel Execution Support

The LoopStep supports parallel processing of items:

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "max_concurrency": 3,  // Process up to 3 items in parallel
    "delay": 0.2,          // Wait 0.2 seconds between starting each task
    "substeps": [...],
    "result_key": "processed_components"
  }
}
```

### Parallel Execution Parameters

- **max_concurrency**: Maximum number of items to process concurrently.

  - `0` (default): Process all items at once (limited only by system resources)
  - `1`: Process items sequentially (no parallelism)
  - `n > 1`: Process up to n items at a time

- **delay**: Time in seconds to wait between starting each parallel task.
  - `0.0` (default): Start all allowed tasks immediately
  - `n > 0`: Add n seconds delay between starting each task

### When to Use Parallel Execution

Parallel execution is most beneficial for loops where:

- Each item's processing is independent of other items
- Processing each item involves significant wait time (e.g., LLM calls, network requests)
- The number of items is large enough to benefit from parallelism

## Step Registration

To enable the use of LoopStep in recipes, register it in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.loop import LoopStep

STEP_REGISTRY["loop"] = LoopStep
```

## Basic Usage in Recipes

The LoopStep allows you to run multiple steps for each item in a collection. Sub-steps are defined within a dedicated `substeps` array.

### Example Recipe (JSON)

```json
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "components",
        "item_key": "component",
        "substeps": [
          {
            "type": "llm_generate",
            "config": {
              "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
              "model": "{{model}}",
              "output_format": "files",
              "output_key": "component_questions"
            }
          },
          {
            "type": "write_files",
            "config": {
              "root": "{{output_dir}}/components/{{component.id}}",
              "files_key": "component_questions"
            }
          }
        ],
        "result_key": "processed_components"
      }
    }
  ]
}
```

## How It Works

For each iteration:

1. The LoopStep renders the `items` path using template rendering to resolve nested paths (e.g., "data.items" becomes the actual array from context["data"]["items"])
2. The LoopStep clones the parent context to create an isolated execution environment
3. It places the current item in the cloned context using the `item_key`
4. It executes all specified steps using the cloned context
5. After execution, it extracts the result from the context (using the same `item_key`)
6. The result is added to a collection that will be stored in the parent context under `result_key`

## Accessing Nested Data

The `items` parameter can reference nested data in the context using dot notation. This is processed using template rendering, similar to other Recipe Executor components:

```json
{
  "type": "loop",
  "config": {
    "items": "data.users.list",
    "item_key": "user",
    "substeps": [...]
  }
}
```

This example would iterate over the array found at `context["data"]["users"]["list"]`.

## Template Variables

Within each iteration, you can reference:

- The current item using the specified `item_key` (e.g., `{{current_component}}`)
- Properties of the current item (e.g., `{{current_component.id}}`)
- The iteration index using `{{__index}}` (for arrays) or key using `{{__key}}` (for objects)
- Other context values from the parent context

## Common Usage Patterns

### Processing Collection of Objects

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Generate questions for component: {{component.name}}\n\nDescription: {{component.description}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "component_questions"
        }
      },
      {
        "type": "write_files",
        "config": {
          "root": "output/{{component.id}}",
          "files_key": "component_questions"
        }
      }
    ],
    "result_key": "processed_components"
  }
}
```

### Processing Files from a Directory

```json
{
  "type": "loop",
  "config": {
    "items": "code_files",
    "item_key": "file",
    "substeps": [
      {
        "type": "read_files",
        "config": {
          "path": "{{file.path}}",
          "content_key": "file_content"
        }
      },
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Analyze this code file:\n{{file_content}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "file_analysis"
        }
      }
    ],
    "result_key": "analyzed_files"
  }
}
```

### Transforming an Array

```json
{
  "type": "loop",
  "config": {
    "items": "input_data",
    "item_key": "item",
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Transform this data item: {{item}}\nIndex: {{__index}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "transformed_item"
        }
      }
    ],
    "result_key": "transformed_data"
  }
}
```

### Parallel Processing Example

```json
{
  "type": "loop",
  "config": {
    "items": "components",
    "item_key": "component",
    "max_concurrency": 5,
    "substeps": [
      {
        "type": "llm_generate",
        "config": {
          "prompt": "Generate a blueprint for component: {{component.name}}",
          "model": "{{model}}",
          "output_format": "files",
          "output_key": "blueprint"
        }
      },
      {
        "type": "write_files",
        "config": {
          "files_key": "blueprint",
          "root": "{{output_dir}}/components/{{component.id}}"
        }
      }
    ],
    "result_key": "processed_blueprints"
  }
}
```

In this example, up to 5 components will be processed simultaneously, each generating and writing a blueprint. This can significantly reduce execution time for LLM-intensive operations across multiple items.

## Error Handling

By default, the LoopStep will stop processing on the first error (`fail_fast: true`). You can change this behavior:

```json
{
  "type": "loop",
  "items": "components",
  "item_key": "component",
  "substeps": [...],
  "result_key": "processed_components",
  "fail_fast": false
}
```

With `fail_fast: false`, the LoopStep will:

- Continue processing remaining items even if some fail
- Include successful results in the output collection
- Log errors for failed items
- Add information about failed items to the `__errors` key in the result collection

## Important Notes

- Each item is processed in isolation with its own context clone
- Changes to the parent context during iteration are not visible to subsequent iterations
- The final result is always a collection, even if only one item is processed
- If the items collection is empty, an empty collection is stored in the result_key
- If a referenced key doesn't exist in the context, an error is raised
- Collection elements can be of any type (objects, strings, numbers, etc.)
- The LoopStep supports both array and object collections


=== File: recipes/recipe_executor/components/steps/loop/loop_spec.md ===
# LoopStep Component Specification

## Purpose

The LoopStep component enables recipes to iterate over a collection of items, executing a specified set of steps for each item. It serves as a fundamental building block for batch processing, enabling modular workflows that operate on multiple similar items without requiring separate recipes.

## Core Requirements

- Process each item in a collection using a specified set of steps
- Support template rendering for the `items` path to access nested data structures via dot notation (e.g., "results.data.items")
- Isolate processing of each item to prevent cross-contamination
- Store the results of processing each item in a designated collection
- Support conditional execution based on item properties
- Provide consistent error handling across all iterations
- Maintain processing state to enable resumability
- Support various collection types (arrays, objects)
- Support concurrent processing of items using configurable parallelism settings (max_concurrency > 1)
- Provide control over the number of items processed simultaneously
- Allow for staggered execution of parallel items via optional delay parameter
- Prevent nested thread pool creation that could lead to deadlocks or resource exhaustion
- Provide reliable completion of all tasks regardless of recipe structure or nesting

## Implementation Considerations

- Use template rendering to resolve the `items` path before accessing data, enabling support for nested paths
- Clone the context for each item to maintain isolation between iterations
- Use a unique context key for each processed item to prevent collisions
- Execute the specified steps for each item using the current executor
- Collect results into a unified collection once all items are processed
- Log progress for each iteration to enable monitoring
- Support proper error propagation while maintaining iteration context
- Handle empty collections gracefully
- Leverage asyncio for efficient processing
- Support structured iteration history for debugging
- Use asyncio for concurrency control and task management
- If parallel item processing is enabled (max_concurrency > 1):
  - Implement an async execution model to allow for non-blocking I/O operations
  - When executing items in parallel, properly await async operations and run sync operations directly
  - Use `Context.clone()` to create independent context copies for each item
  - Implement a configurable launch delay (using `asyncio.sleep`) for staggered start times
  - Monitor exceptions and implement fail-fast behavior
  - Provide clear logging for item lifecycle events and execution summary
  - Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols**: Leverages ContextProtocol for context sharing, ExecutorProtocol for execution, and StepProtocol for the step interface contract
- **Step Base**: Adheres to the step execution interface via StepProtocol
- **Step Registry**: Uses the step registry to instantiate the `execute_recipe` step for each sub-step
- **Context**: Shares data via a context object implementing the ContextProtocol between the main recipe and sub-recipes
- **Executor**: Uses an executor implementing ExecutorProtocol to run the sub-recipe
- **Utils/Templates**: Uses template rendering for the `items` path and sub-step configurations

### External Libraries

- **asyncio**: Uses asyncio for asynchronous processing and managing parallel processing of loop items
- **time**: Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Logging

- Debug: Log the start/end of each item processing with its index/key, log steps execution within the loop
- Info: Log high-level information about how many items are being processed and the result collection

## Error Handling

- Validate the items collection exists and is iterable before starting
- Validate that steps are properly specified
- Handle both empty collections and single items gracefully
- Provide clear error messages when an item fails processing
- Include the item key/index in error messages for easier debugging
- Allow configuration of whether to fail fast or continue on errors

## Output Files

- `recipe_executor/steps/loop.py` - (LoopStep implementation)


=== File: recipes/recipe_executor/components/steps/mcp/mcp_docs.md ===
# MCPStep Component Usage

## Importing

```python
from recipe_executor.steps.mcp import MCPStep, MCPConfig
```

## Configuration

The MCPStep is configured with a `MCPConfig`:

```python
class MCPConfig(StepConfig):
    """
    Configuration for MCPStep.

    Fields:
        server: Configuration for the MCP server.
        tool_name: Name of the tool to invoke.
        arguments: Arguments to pass to the tool as a dictionary.
        result_key: Context key under which to store the tool result as a dictionary.
    """
    server: Dict[str, Any]
    tool_name: str
    arguments: Dict[str, Any]
    result_key: str = "tool_result"
```

The `server` field is a dictionary containing the server configuration, which can include:

For HTTP servers:

- `url`: str - the URL of the MCP server.
- `headers`: Optional[Dict[str, Any]] -headers to include in the request.

For stdio servers:

- `command`: str - the command to run the MCP server.
- `args`: List[str] - arguments to pass to the command.
- `env`: Optional[Dict[str, str]] - environment variables to set for the command.
- `working_dir`: The working directory for the command.

## Basic Usage in Recipes

The `MCPStep` is available via the `mcp` step type in recipes:

```json
{
  "steps": [
    {
      "type": "mcp",
      "config": {
        "server": {
          "url": "http://localhost:5000",
          "headers": {
            "api_key": "your_api_key"
          }
        },
        "tool_name": "get_stock",
        "arguments": { "item_id": "{{item_id}}" },
        "result_key": "stock_info"
      }
    }
  ]
}
```

After execution, the context contains:

```json
{
  "stock_info": {
    "item_id": 123,
    "name": "Widget",
    "price": 19.99,
    "in_stock": true,
    "quantity": 42
  }
}
```

## Template-Based Configuration

All string configuration fields support templating using context variables.


=== File: recipes/recipe_executor/components/steps/mcp/mcp_spec.md ===
# MCPStep Component Specification

## Purpose

The MCPStep component allows recipes to invoke tools on remote MCP servers and store the result in the execution context.

## Core Requirements

- Accept configuration for the MCP server, tool name, arguments, and result key.
- Use a minimal MCP client implementation:
  - Connect to the MCP server using the provided configuration.
  - Call the specified tool with the provided arguments.
- Handle errors:
  - Raise a `ValueError` with a clear message if the call fails.
- Remain stateless across invocations.

## Implementation Considerations

- Retrieve configuration values via the step config object.
- Use `render_template` to resolve templated configuration values before use.
- Use `sse_client` or `stdio_client` to create `ClientSession` instance.
  - For `stdio_client`:
    - Use `StdioServerParameters` for `server` config parameter.
    - Use `cwd` as the working directory for the command.
- Intialize session and execute session.call_tool with the tool name and arguments.
- Wrap exceptions from the client in `ValueError` including the tool name and service.
- Convert the `mcp.types.CallToolResult` to `Dict[str, Any]`.
- Store converted tool result dictionary in context under `result_key`.
- Overwrite existing context values if `result_key` already exists.

## Logging

- Debug: Log connection attempts and tool invocation details (tool name, arguments).
- Info: None by default.

## Component Dependencies

### Internal Components

- **Protocols**: Uses `ContextProtocol` for context interactions and `StepProtocol` for the step interface.
- **Utils/Templates**: Uses `render_template` for resolving templated parameters.

### External Libraries

- **mcp**: Provides `sse_client`, `stdio_client`, `CallToolResult` `StdioServerParameters` and `ClientSession` for MCP server interactions.

### Configuration Dependencies

None

## Error Handling

- Raise `ValueError` on connection failures or tool invocation errors with descriptive messages.
- Allow exceptions from the client to propagate if not caught.

## Output Files

- `recipe_executor/steps/mcp.py`


=== File: recipes/recipe_executor/components/steps/parallel/parallel_docs.md ===
# ParallelStep Component Usage

The **ParallelStep** component enables the concurrent execution of multiple sub-steps within a recipe. It is ideal for improving performance when independent tasks can be executed in parallel.

## Importing

Import the ParallelStep and its configuration:

```python
from recipe_executor.steps.parallel import ParallelStep, ParallelConfig
```

## Configuration

The ParallelStep is configured via a `ParallelConfig` object. This configuration defines the list of sub-steps to run concurrently, along with optional settings for controlling concurrency.

```python
class ParallelConfig(StepConfig):
    """Config for ParallelStep.

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
```

## Step Registration

To enable the use of ParallelStep in recipes, register it in the step registry:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.parallel import ParallelStep

STEP_REGISTRY["parallel"] = ParallelStep
```

## Basic Usage in Recipes

The ParallelStep allows you to run multiple steps concurrently. Sub-steps are defined within a dedicated `substeps` array.

### Example Recipe (JSON)

```json
{
  "steps": [
    {
      "type": "parallel",
      "config": {
        "substeps": [
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "recipes/subtask_a.json",
              "context_overrides": {
                "input_data": "{{shared_input}}"
              }
            }
          },
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "recipes/subtask_b.json",
              "context_overrides": {
                "input_data": "{{shared_input}}"
              }
            }
          }
        ],
        "max_concurrency": 2, // Process up to 2 sub-steps in parallel
        "delay": 0.5 // Optional delay of 0.5 seconds between starting each sub-step
      }
    }
  ]
}
```

## Integration with Other Steps

The ParallelStep is designed to integrate seamlessly with the rest of your recipe:

- **Copies of Context:** All sub-steps are provided a copy of the same context (the shared context implements ContextProtocol), enabling them to read from common data.
- **Independent Execution:** Use ParallelStep only for tasks that do not depend on each other nor write back to context beyond the parallel block’s lifecycle, as each cloned context is discarded after the parallel block completes.

## Important Notes

- **Error Handling:** If any sub-step fails, the entire parallel execution aborts. Handle errors within each sub-step to ensure graceful degradation.
- **Resource Constraints:** Adjust `max_concurrency` based on system resources to avoid overwhelming the executor.
- **Delay Between Sub-steps:** Use the `delay` parameter to control the timing of sub-step execution, which can help manage resource contention.


=== File: recipes/recipe_executor/components/steps/parallel/parallel_spec.md ===
# ParallelStep Component Specification

## Purpose

The ParallelStep component enables the Recipe Executor to run multiple sub-recipes concurrently within a single step. It improves execution efficiency by parallelizing independent tasks while maintaining isolation between them.

## Core Requirements

- Accept a list of sub-step configurations (each sub-step is an `execute_recipe` step definition)
- Clone the current execution context for each sub-step to ensure isolation
- Execute sub-steps concurrently with a configurable maximum concurrency limit
- Support an optional delay between launching each sub-step
- Wait for all sub-steps to complete before proceeding, with appropriate timeout handling
- Implement fail-fast behavior: if any sub-step fails, stop launching new ones and report the error
- Prevent nested thread pool creation that could lead to deadlocks or resource exhaustion
- Provide reliable completion of all tasks regardless of recipe structure or nesting

## Implementation Considerations

- Use asyncio for concurrency control and task management
- Implement an async execution model to allow for non-blocking I/O operations
- When executing substeps, properly await async operations and run sync operations directly
- Add configurable timeouts to prevent indefinite waiting for task completion
- Use `Context.clone()` to create independent context copies for each sub-step
- Implement a configurable launch delay (using `asyncio.sleep`) for staggered start times
- Monitor exceptions and implement fail-fast behavior
- Provide clear logging for sub-step lifecycle events and execution summary
- Manage resources efficiently to prevent memory or thread leaks

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol for context management, ExecutorProtocol for parallel execution, and StepProtocol for the step interface
- **Step Base**: Adheres to the step execution interface via StepProtocol
- **Step Registry**: Uses the step registry to instantiate the `execute_recipe` step for each sub-step

### External Libraries

- **asyncio**: Utilizes asyncio for asynchronous task management and parallel execution
- **time**: Uses `time.sleep` to implement delays between sub-step launches

### Configuration Dependencies

None

## Logging

- Debug: Log sub-step start/completion events, thread allocation, and configuration details
- Info: Log start and completion with a summary of the parallel execution (number of steps and success/failure counts)

## Error Handling

- Implement fail-fast behavior when any sub-step encounters an error
- Cancel pending sub-steps if an error occurs
- Include clear error context identifying which sub-step failed
- Ensure proper thread pool shutdown to prevent orphaned threads
- Propagate the original exception with contextual information about the failure

## Output Files

- `recipe_executor/steps/parallel.py` (ParallelStep implementation)


=== File: recipes/recipe_executor/components/steps/read_files/read_files_docs.md ===
# ReadFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.read_files import ReadFilesStep, ReadFilesConfig
```

## Configuration

The ReadFilesStep is configured with a ReadFilesConfig:

```python
class ReadFilesConfig(StepConfig):
    """
    Configuration for ReadFilesStep.

    Fields:
        path (Union[str, List[str]]): Path, comma-separated string, or list of paths to the file(s) to read (may be templated).
        content_key (str): Name to store the file content in context.
        optional (bool): Whether to continue if a file is not found.
        merge_mode (str): How to handle multiple files' content. Options:
            - "concat" (default): Concatenate all files with newlines between filenames + content
            - "dict": Store a dictionary with filenames as keys and content as values
    """
    path: Union[str, List[str]]
    content_key: str
    optional: bool = False
    merge_mode: str = "concat"
```

## Step Registration

The ReadFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.read_files import ReadFilesStep

STEP_REGISTRY["read_files"] = ReadFilesStep
```

## Basic Usage in Recipes

### Reading a Single File

The ReadFilesStep can be used to read a single file (just like the original `read_file` step):

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/component_spec.md",
        "content_key": "component_spec"
      }
    }
  ]
}
```

### Reading Multiple Files

You can read multiple files by providing a comma-separated string of paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/component_spec.md,specs/component_docs.md",
        "content_key": "component_specs"
      }
    }
  ]
}
```

You can also read multiple files by providing a list of path strings:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": ["specs/component_spec.md", "specs/component_docs.md"],
        "content_key": "component_specs",
        "merge_mode": "concat"
      }
    }
  ]
}
```

### Reading Multiple Files as a Dictionary

You can store multiple files as a dictionary with filenames as keys:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": ["specs/component_spec.md", "specs/component_docs.md"],
        "content_key": "component_specs",
        "merge_mode": "dict"
      }
    }
  ]
}
```

## Template-Based Paths

The `path` parameter can include template variables from the context:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "specs/{{component_id}}_spec.md",
        "content_key": "component_spec"
      }
    }
  ]
}
```

Template variables can also be used within list paths:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": [
          "specs/{{component_id}}_spec.md",
          "specs/{{component_id}}_docs.md"
        ],
        "content_key": "component_files"
      }
    }
  ]
}
```

## Optional Files

You can specify that files are optional. If an optional file doesn't exist, execution will continue:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": ["specs/required_file.md", "specs/optional_file.md"],
        "content_key": "component_files",
        "optional": true
      }
    }
  ]
}
```

If an optional file is not found:

- For a single file: an empty string is stored in the context
- For multiple files with `merge_mode: "concat"`: the missing file is skipped in the concatenated result
- For multiple files with `merge_mode: "dict"`: the missing file is omitted from the dictionary

## Common Use Cases

**Loading Multiple Related Specifications**:

```json
{
  "type": "read_files",
  "config": {
    "path": [
      "specs/{{component_id}}_spec.md",
      "specs/{{component_id}}_docs.md"
    ],
    "content_key": "component_files",
    "merge_mode": "concat"
  }
}
```

**Loading Templates with Optional Components**:

```json
{
  "type": "read_files",
  "config": {
    "path": [
      "templates/email_base.txt",
      "templates/email_header.txt",
      "templates/email_footer.txt"
    ],
    "content_key": "email_templates",
    "optional": true,
    "merge_mode": "dict"
  }
}
```

**Dynamic Path Resolution with Multiple Files**:

```json
{
  "type": "read_files",
  "config": {
    "path": [
      "docs/{{project}}/{{component}}/README.md",
      "docs/{{project}}/{{component}}/USAGE.md"
    ],
    "content_key": "documentation",
    "merge_mode": "dict"
  }
}
```

**Command Line Integration**:

You can also supply paths via command-line context values:

```bash
recipe-tool --execute recipes/generate.json files_to_read="specs/component_a.md,specs/component_b.md"
```

Then in the recipe you can use that context value:

```json
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{files_to_read.split(',')|default:'specs/default.md'}}",
        "content_key": "input_files"
      }
    }
  ]
}
```

## Important Notes

- The step uses UTF-8 encoding by default for all files
- If the file is JSON, it will be parsed and stored as a dictionary
- When a file is optional and missing, it is handled according to the specified `merge_mode`
- Template variables in all paths are resolved before reading the files
- When using `merge_mode: "dict"`, the keys in the output are the full paths of the files
- All paths support template rendering (including each path in a list)


=== File: recipes/recipe_executor/components/steps/read_files/read_files_spec.md ===
# ReadFilesStep Component Specification

## Purpose

The ReadFilesStep component reads one or more files from the filesystem and stores their content in the execution context. It serves as a foundational step for loading data into recipes (such as specifications, templates, and other input files) with support for both single-file and multi-file operations.

## Core Requirements

- Read a file or multiple files from specified path(s)
- Support input specified as a single path string, a comma-separated string of paths, or a list of path strings
- If a single string is provided, detect commas to determine if it represents multiple paths and split accordingly
- Support template-based path resolution for all paths
- Store all file content in the context under a single specified key
- Support reading files in text format with UTF-8 encoding
- Where possible, deserialize the content to a Python object (e.g., JSON, YAML) if the file format allows
- Provide flexible content merging options for multi-file reads
- Support optional file handling for cases when files might not exist
- Include appropriate logging and error messages
- Follow a minimal design with clear error handling

## Implementation Considerations

- Render template strings for the `path` parameter before evaluating the input type
- Use template rendering to support dynamic paths for single path, comma-separated paths in one string, and lists of paths
- Handle missing files explicitly with meaningful error messages
- Use consistent UTF-8 encoding for text files
- Implement an `optional` flag to continue execution if files are missing
- For multiple files, provide a way to merge content (default: concatenate with newlines separating each file’s content)
- Provide a clear content structure when reading multiple files (e.g. a dictionary with filenames as keys)
- Keep the implementation simple and focused on a single responsibility
- For backwards compatibility, preserve the behavior of the original single-file read step

## Logging

- Debug: Log each file path before attempting to read (useful for diagnosing failures)
- Info: Log the successful reading of each file (including its path) and the final storage key used in the context

## Component Dependencies

### Internal Components

- **Step Interface**: Implements the step interface via StepProtocol
- **Context**: Stores file content using a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils/Templates**: Uses render_template for dynamic path resolution

### External Libraries

- **pyyaml**: For parsing YAML files if the content is in YAML format

### Configuration Dependencies

None

## Error Handling

- Raise a FileNotFoundError with a clear message when required files do not exist
- Support the `optional` flag to continue execution (with empty content) if files are missing
- Handle error cases differently for single-file versus multiple-file scenarios
- Log appropriate warnings and information during execution
- When reading multiple files and some are optional, continue processing those files that exist

## Output Files

- `recipe_executor/steps/read_files.py`


=== File: recipes/recipe_executor/components/steps/registry/registry_docs.md ===
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
    "conditional": ConditionalStep,
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
}
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
from recipe_executor.steps.registry import STEP_REGISTRY

... code ...
    step_type = step["type"]
    if step_type not in STEP_REGISTRY:
        raise ValueError(f"Unknown step type '{step_type}'")

    step_class = STEP_REGISTRY[step_type]
    step_config = step.get("config", {})
    step_instance = step_class(logger, step_config)
    await step_instance.execute(context)
```

## Important Notes

- Step type names must be unique across the entire system
- Steps must be registered before the executor tries to use them
- Standard steps are automatically registered when the package is imported
- Custom steps need to be explicitly registered by the user


=== File: recipes/recipe_executor/components/steps/registry/registry_spec.md ===
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

## Logging

- Debug: None
- Info: None

## Component Dependencies

### Internal Components

None

### External Libraries

None

### Configuration Dependencies

None

## Output Files

- `recipe_executor/steps/registry.py`
- `recipe_executor/steps/__init__.py` (details below)

```python
# recipe_executor/steps/__init__.py
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.conditional import ConditionalStep
from recipe_executor.steps.execute_recipe import ExecuteRecipeStep
from recipe_executor.steps.llm_generate import LLMGenerateStep
from recipe_executor.steps.loop import LoopStep
from recipe_executor.steps.mcp import MCPStep
from recipe_executor.steps.parallel import ParallelStep
from recipe_executor.steps.read_files import ReadFilesStep
from recipe_executor.steps.write_files import WriteFilesStep

# Register steps by updating the registry
STEP_REGISTRY.update({
    "conditional": ConditionalStep,
    "execute_recipe": ExecuteRecipeStep,
    "llm_generate": LLMGenerateStep,
    "loop": LoopStep,
    "mcp": MCPStep,
    "parallel": ParallelStep,
    "read_files": ReadFilesStep,
    "write_files": WriteFilesStep,
})
```


=== File: recipes/recipe_executor/components/steps/write_files/write_files_docs.md ===
# WriteFilesStep Component Usage

## Importing

```python
from recipe_executor.steps.write_files import WriteFilesStep, WriteFilesConfig
```

## Configuration

The WriteFilesStep is configured with a WriteFilesConfig:

```python
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
```

## Step Registration

The WriteFilesStep is typically registered in the steps package:

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.write_files import WriteFilesStep

STEP_REGISTRY["write_files"] = WriteFilesStep
```

## Basic Usage in Recipes

Either `files_key` or `files` is required in the configuration. If both are provided, `files` takes precedence.

The `files_key` is the context key where the generated files are stored. The `files` parameter can be used to directly provide a list of dictionaries with `path` and `content` keys. Alternatively, the path and content can be specfied using `path_key` and `content_key` respectively to reference values in the context.

The WriteFilesStep can be used in recipes like this:

Files Key Example:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a Python script that prints 'Hello, world!'",
        "model": "openai/o4-mini",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        # Preferred way to receive "files" from other steps that create FileSpec objects
        "files_key": "generated_files",
        "root": "output/src"
      }
    }
  ]
}
```

Files Example:

```json
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files": [
          { "path": "src/main.py", "content": "print('Hello, world!')" },
          {
            "path": "src/{{component_name}}_utils.py",
            "content_key": "generated_code"
          },
          {
            "path_key": "generated_config_path",
            "content_key": "generated_config_data"
          }
        ],
        "root": "output/src"
      }
    }
  ]
}
```

## Supported Context Values

The WriteFilesStep can work with two types of artifacts in the context:

### Single FileSpec object

```python
from recipe_executor.models import FileSpec
# Example of generating a FileSpec object
file = FileSpec(path="src/main.py", content="print('Hello, world!')")
# Store in context
context["generated_file"] = file
```

### List of FileSpec objects

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

## Automatic JSON Serialization

When the content to be written is a Python dictionary or list, WriteFilesStep automatically serializes it to properly formatted JSON:

```json
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate configuration data for a project.",
        "model": "openai/o4-mini",
        "output_format": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "version": { "type": "string" },
            "dependencies": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "output_key": "project_config"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "config.json",
            "content_key": "project_config"
          }
        ],
        "root": "output"
      }
    }
  ]
}
```

In this example, `project_config` is a Python dictionary, but when written to `config.json`, it will be automatically serialized as proper JSON with double quotes and indentation.

## Using Template Variables

The root path and individual file paths can include template variables:

```json
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "output/{{project_name}}"
      }
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

## Common Use Cases

**Writing Generated Code**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/src",
    "files_key": "generated_files"
  }
}
```

**Writing Structured Data as JSON**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/data",
    "files": [
      {
        "path": "config.json",
        "content_key": "config_data"
      }
    ]
  }
}
```

When `config_data` is a Python dictionary or list, it will be automatically serialized as formatted JSON.

**Project-Specific Output**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/{{project_name}}",
    "files_key": "project_files"
  }
}
```

**Component Generation**:

```json
{
  "type": "write_files",
  "config": {
    "root": "output/components",
    "files_key": "component_result"
  }
}
```

## Important Notes

- Directories are created automatically if they don't exist
- Files are overwritten without confirmation if they already exist
- All paths are rendered using template variables from the context (ContextProtocol)
- File content is written using UTF-8 encoding
- Both FileSpec and List[FileSpec] input formats are supported
- Python dictionaries and lists are automatically serialized to properly formatted JSON with indentation
- JSON serialization uses `json.dumps(content, ensure_ascii=False, indent=2)` for consistent formatting


=== File: recipes/recipe_executor/components/steps/write_files/write_files_spec.md ===
# WriteFilesStep Component Specification

## Purpose

The WriteFilesStep component writes generated files to disk based on content from the execution context. It handles creating directories, resolving paths, and writing file content, serving as the output mechanism for the Recipe Executor system.

## Core Requirements

- Write one or more files to disk from the context
- Support both single FileSpec and list of FileSpec formats as input
- Optional use of `files_key` to specify the context key for file content or `files` for direct input
- While `FileSpec` is preferred, the component should also support a list of dictionaries with `path` and `content` keys and then write the files to disk, preserving the original structure of `content`
- Create directories as needed for file paths
- Apply template rendering to all file paths, content, and keys
- Automatically serialize Python dictionaries or lists to proper JSON format when writing to files
- Provide appropriate logging for file operations
- Follow a minimal design with clear error handling

## Implementation Considerations

- Support multiple file output formats (single FileSpec or list of FileSpec)
- Use template rendering for dynamic path resolution
- Create parent directories automatically if they do not exist
- Apply template rendering to content prior to detecting its type, in case the content is a string that needs to be serialized
- Automatically detect when content is a Python dictionary or list and serialize it to proper JSON with indentation
- When serializing to JSON, use `json.dumps(content, ensure_ascii=False, indent=2)` for consistent, readable formatting
- Handle serialization errors with clear messages
- Keep the implementation simple and focused on a single responsibility
- Log details about files written for troubleshooting

## Logging

- Debug: Log each file's path and content before writing (to help debug failures)
- Info: Log the successful writing of each file (including its path) and the size of its content

## Component Dependencies

### Internal Components

- **Step Interface** – (Required) Follows the step interface via StepProtocol
- **Models** – (Required) Uses FileSpec models for content structure
- **Context** – (Required) Reads file content from a context that implements ContextProtocol (artifacts stored under a specified key)
- **Utils/Templates** – (Required) Uses render_template for dynamic path resolution

### External Libraries

- **json** - (Required) For serializing Python dictionaries and lists to JSON

### Configuration Dependencies

None

## Error Handling

- Validate that the specified artifact exists in context
- Ensure the artifact contains a valid single FileSpec or list of FileSpec objects
- Handle serialization errors with clear error messages when content cannot be converted to JSON
- Handle file writing errors with clear messages
- Log successes and failures appropriately

## Output Files

- `recipe_executor/steps/write_files.py`


=== File: recipes/recipe_executor/components/utils/models/models_docs.md ===
# Pydantic-Model Utilities

## Importing

```python
from recipe_executor.utils.models import json_schema_object_to_pydantic_model
```

## Conversion from JSON Object to Pydantic

This utility function converts a JSON object definition into a Pydantic model. It
allows you to define an object as a JSON-Schema fragment and then generate a strongly-typed
Pydantic model that can be used for data validation and serialization.

The generated model will have fields corresponding to the properties defined in the
JSON-Schema. The types of the fields will be inferred from the JSON-Schema types.

```python
def json_object_to_pydantic_model(
    object_schema: Dict[str, Any],
    model_name: str = "SchemaModel"
) -> Type[pydantic.BaseModel]:
    """
    Convert a JSON object dictionary into a dynamic Pydantic model.

    Args:
        object_schema: A valid JSON-Schema fragment describing an object.
        model_name: Name given to the generated model class.

    Returns:
        A subclass of `pydantic.BaseModel` suitable for validation & serialization.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
```

Basic usage example:

```python
from recipe_executor.utils.models import json_object_to_pydantic_model

user_schema = {
    "type": "object",
    "properties": {
        "name":  {"type": "string"},
        "age":   {"type": "integer"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

User = json_object_to_pydantic_model(user_schema, model_name="User")

instance = User(name="Alice", age=30, email="alice@example.com")
print(instance.model_dump())      # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

NOTE: An **object** is required at the root level of the schema. If the root type is not an object, a `ValueError` will be raised.


=== File: recipes/recipe_executor/components/utils/models/models_spec.md ===
# Models-Utility Component Specification

## Purpose

Provide reusable helpers for Pydantic models, such as conversion from JSON-Schema object definitions to fully-typed
`pydantic.BaseModel` subclasses.

## Core Requirements

- `json_object_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]`
  Converts any root-level **object** (incl. nested structures & `"required"`) into a `BaseModel` created with `pydantic.create_model`.
- The schema must be a valid JSON-Schema object fragment. Chilren of the root object can be:
  - JSON-Schema primitive types: `"string"`, `"integer"`, `"number"`, `"boolean"`.
  - Compound types: `"object"`, `"array"` (alias `"list"`).
  - Unknown / unsupported `"type"` values fall back to `typing.Any`.
- All schema types must yield a valid BaseModel subclass:
  - Root object schemas become a model with fields matching properties
  - Any other root type (e.g., array, string, number) is rejected as invalid.
- Strictly validate input schemas before processing.
- Stateless, synchronous, no logging, no I/O.
- Raise `ValueError` on malformed schemas (e.g., missing `"type"`).

## Implementation Considerations

- Use **`pydantic.create_model`** for creating all models.
- Generate deterministic nested-model names using a counter for nested objects.
- Provide clear error messages for schema validation issues.

## Component Dependencies

### Internal Components

- **None**

### External Libraries

- **pydantic** – (Required) Provides `BaseModel` and `create_model`.
- **typing** – (Required) `Any`, `List`, `Optional`, `Type`.

### Configuration Dependencies

None

## Logging

None

## Error Handling

- Raise **`ValueError`** with a clear message when the input schema is invalid or unsupported.
- Include details about the specific validation error in the error message.
- Validate schema types before processing to avoid cryptic errors.

## Dependency Integration Considerations

None

## Output Files

- `recipe_executor/utils/models.py`


=== File: recipes/recipe_executor/components/utils/templates/templates_docs.md ===
# Template Utility Component Usage

## Importing

```python
from recipe_executor.utils.templates import render_template
```

## Template Rendering

The Templates utility component provides a `render_template` function that renders Liquid templates using values from a context object implementing the ContextProtocol:

```python
def render_template(text: str, context: ContextProtocol) -> str:
    """
    Render the given text as a Liquid template using the provided context.

    Args:
        text (str): The template text to render.
        context (ContextProtocol): The context providing values for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

Basic usage example:

```python
from recipe_executor.utils.templates import render_template

# Create a context with some values
context = Context(artifacts={"name": "World", "count": 42})

# Render a template string using the context
template = "Hello, {{name}}! You have {{count}} messages."
result = render_template(template, context)

print(result)  # Hello, World! You have 42 messages.
```

## Template Syntax

The template rendering uses Liquid syntax. Here are some common features:

### Variable Substitution

```python
# Simple variable
template = "User: {{username}}"

# Nested paths (if context contains nested dictionaries)
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


=== File: recipes/recipe_executor/components/utils/templates/templates_spec.md ===
# Utils Component Specification

## Purpose

The Utils component provides general utility functions for recipes, primarily focused on template rendering. It offers a way to render strings with template variables against the execution context, enabling dynamic content generation in recipes.

## Core Requirements

- Render strings as templates using context data
- Utilize a standard templating engine (Liquid) for consistency
- Ensure that all context values are accessible to the templates
- Handle errors in template rendering gracefully
- Keep the utility functions stateless and reusable

## Implementation Considerations

- Use the Liquid templating library directly without unnecessary abstraction
- Pass the `context.dict()` to the Liquid template for rendering
- Handle rendering errors gracefully with clear error messages
- Keep the implementation stateless and focused on its single responsibility

## Logging

- None

## Component Dependencies

### Internal Components

- **Protocols**: Uses ContextProtocol definition for context data access

### External Libraries

- **python-liquid**: Uses the Liquid templating engine for rendering

### Configuration Dependencies

None

## Error Handling

- Wrap template rendering in try/except blocks
- Raise ValueError with a clear message if rendering fails
- Use `liquid.exceptions.LiquidError` for Liquid-specific errors, otherwise just raise a generic ValueError
- Ensure that the error message includes the template and context for easier debugging

## Output Files

- `recipe_executor/utils/templates.py`


=== File: recipes/recipe_executor/docs/recipe-executor-build-flow.excalidraw ===
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "main-flow-group",
      "type": "rectangle",
      "x": 120,
      "y": 80,
      "width": 200,
      "height": 600,
      "angle": 0,
      "strokeColor": "transparent",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1012473515,
      "version": 67,
      "versionNonce": 241155753,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745692830338,
      "link": null,
      "locked": false,
      "index": "a0"
    },
    {
      "id": "process-component-group",
      "type": "rectangle",
      "x": 400.01268594946185,
      "y": 46.20345012424031,
      "width": 520,
      "height": 712.9076455248853,
      "angle": 0.001839002649331789,
      "strokeColor": "#999999",
      "backgroundColor": "#f5f5f5",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 40,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1308022037,
      "version": 137,
      "versionNonce": 110702471,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "process-component-label",
          "type": "text"
        },
        {
          "id": "No3GKwzTAcDax9MiojCy8",
          "type": "arrow"
        }
      ],
      "updated": 1745693717684,
      "link": null,
      "locked": false,
      "index": "a1"
    },
    {
      "id": "process-component-label",
      "type": "text",
      "x": 567.9727765866689,
      "y": 51.20345012424031,
      "width": 184.07981872558594,
      "height": 25,
      "angle": 0.001839002649331789,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 93,
      "versionNonce": 1684897191,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693052141,
      "link": null,
      "locked": false,
      "text": "Process Component",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "baseline": 18,
      "containerId": "process-component-group",
      "originalText": "Process Component",
      "lineHeight": 1.25,
      "index": "a2",
      "autoResize": true
    },
    {
      "id": "start-build",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 52.44439697265625,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 291,
      "versionNonce": 1102013129,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "start-build-text"
        },
        {
          "id": "TlqYH6PsCDPG6udk91uqK",
          "type": "arrow"
        }
      ],
      "updated": 1745693615405,
      "link": null,
      "locked": false,
      "index": "a5"
    },
    {
      "id": "start-build-text",
      "type": "text",
      "x": 136.6089859008789,
      "y": 69.94439697265625,
      "width": 152.5598602294922,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 240,
      "versionNonce": 327261385,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Start build.json",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "start-build",
      "originalText": "Start build.json",
      "lineHeight": 1.25,
      "index": "a6",
      "autoResize": true
    },
    {
      "id": "read-components",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 152.44439697265625,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 287,
      "versionNonce": 1971950087,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "read-components-text"
        },
        {
          "id": "TlqYH6PsCDPG6udk91uqK",
          "type": "arrow"
        },
        {
          "id": "4kX9qa1KQzQdyPHPMVMQc",
          "type": "arrow"
        }
      ],
      "updated": 1745693667529,
      "link": null,
      "locked": false,
      "index": "a7"
    },
    {
      "id": "read-components-text",
      "type": "text",
      "x": 108.36900329589844,
      "y": 169.94439697265625,
      "width": 209.03982543945312,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 277,
      "versionNonce": 1483670889,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Read components.json",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "read-components",
      "originalText": "Read components.json",
      "lineHeight": 1.25,
      "index": "a8",
      "autoResize": true
    },
    {
      "id": "component-loop",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 252.44439697265625,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 889566749,
      "version": 354,
      "versionNonce": 1452406473,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "component-loop-text"
        },
        {
          "id": "WM7UQjc4eu62cZzmhf5n0",
          "type": "arrow"
        },
        {
          "id": "vXkaDZ84Vx95q_If5vxaP",
          "type": "arrow"
        },
        {
          "id": "4kX9qa1KQzQdyPHPMVMQc",
          "type": "arrow"
        },
        {
          "id": "_Ug_hzIUd5ivlzrUxoOpa",
          "type": "arrow"
        }
      ],
      "updated": 1745693760466,
      "link": null,
      "locked": false,
      "index": "a9"
    },
    {
      "id": "component-loop-text",
      "type": "text",
      "x": 136.64898681640625,
      "y": 269.94439697265625,
      "width": 152.4798583984375,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 308,
      "versionNonce": 1277567047,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693679186,
      "link": null,
      "locked": false,
      "text": "Component Loop",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "component-loop",
      "originalText": "Component Loop",
      "lineHeight": 1.25,
      "index": "aA",
      "autoResize": true
    },
    {
      "id": "match-component",
      "type": "diamond",
      "x": 93.3333740234375,
      "y": 352.44439697265625,
      "width": 239.111083984375,
      "height": 140,
      "angle": 0,
      "strokeColor": "#e6961e",
      "backgroundColor": "#fff9db",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 1355480981,
      "version": 482,
      "versionNonce": 2113310055,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "match-component-text"
        },
        {
          "id": "match-to-complete",
          "type": "arrow"
        },
        {
          "id": "ySSobv5QuYECoDtsy9PpX",
          "type": "arrow"
        },
        {
          "id": "WM7UQjc4eu62cZzmhf5n0",
          "type": "arrow"
        },
        {
          "id": "vXkaDZ84Vx95q_If5vxaP",
          "type": "arrow"
        }
      ],
      "updated": 1745693627051,
      "link": null,
      "locked": false,
      "index": "aB"
    },
    {
      "id": "match-component-text",
      "type": "text",
      "x": 158.21517944335938,
      "y": 402.44439697265625,
      "width": 109.79193115234375,
      "height": 40,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 421,
      "versionNonce": 674825769,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Match\ncomponent_id?",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "match-component",
      "originalText": "Match component_id?",
      "lineHeight": 1.25,
      "index": "aC",
      "autoResize": true
    },
    {
      "id": "build-complete",
      "type": "rectangle",
      "x": 93.3333740234375,
      "y": 552.4443969726562,
      "width": 239.111083984375,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 379,
      "versionNonce": 883100809,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "build-complete-text"
        },
        {
          "id": "match-to-complete",
          "type": "arrow"
        }
      ],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "index": "aD"
    },
    {
      "id": "build-complete-text",
      "type": "text",
      "x": 143.38898468017578,
      "y": 569.9443969726562,
      "width": 138.99986267089844,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 336,
      "versionNonce": 394433385,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693494484,
      "link": null,
      "locked": false,
      "text": "Build complete",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "build-complete",
      "originalText": "Build complete",
      "lineHeight": 1.25,
      "index": "aE",
      "autoResize": true
    },
    {
      "id": "start-processing",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 99.99999999999999,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 394,
      "versionNonce": 2020006951,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "start-processing-text"
        },
        {
          "id": "JrrnHW0v8d0iK7XEIn7KE",
          "type": "arrow"
        },
        {
          "id": "ySSobv5QuYECoDtsy9PpX",
          "type": "arrow"
        }
      ],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "index": "aF"
    },
    {
      "id": "start-processing-text",
      "type": "text",
      "x": 578.6727659055166,
      "y": 117.49999999999999,
      "width": 162.67984008789062,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 362,
      "versionNonce": 656479495,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Start processing",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "start-processing",
      "originalText": "Start processing",
      "lineHeight": 1.25,
      "index": "aG",
      "autoResize": true
    },
    {
      "id": "edit-mode",
      "type": "diamond",
      "x": 528.2349149533682,
      "y": 206.88888549804688,
      "width": 263.5555419921875,
      "height": 70,
      "angle": 0,
      "strokeColor": "#e6961e",
      "backgroundColor": "#fff9db",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 889566749,
      "version": 556,
      "versionNonce": 1427116199,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "edit-mode-text"
        },
        {
          "id": "Lm5YCicKEwjG6SrJlxhgr",
          "type": "arrow"
        },
        {
          "id": "TKV39LSOmiDZlottftzrO",
          "type": "arrow"
        },
        {
          "id": "JrrnHW0v8d0iK7XEIn7KE",
          "type": "arrow"
        }
      ],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "index": "aH"
    },
    {
      "id": "edit-mode-text",
      "type": "text",
      "x": 607.1638471433096,
      "y": 229.38888549804688,
      "width": 105.91990661621094,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 447,
      "versionNonce": 1777785223,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Edit mode?",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "edit-mode",
      "originalText": "Edit mode?",
      "lineHeight": 1.25,
      "index": "aI",
      "autoResize": true
    },
    {
      "id": "generate-code",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 793.7777404785157,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 889566749,
      "version": 959,
      "versionNonce": 1677812201,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "generate-code-text"
        },
        {
          "id": "No3GKwzTAcDax9MiojCy8",
          "type": "arrow"
        },
        {
          "id": "gEZESsXP0bh46KowvfnaH",
          "type": "arrow"
        }
      ],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "index": "aX"
    },
    {
      "id": "generate-code-text",
      "type": "text",
      "x": 539.1927701779775,
      "y": 811.2777404785157,
      "width": 241.63983154296875,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 951,
      "versionNonce": 1731149001,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "text": "Generate code with LLM",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "generate-code",
      "originalText": "Generate code with LLM",
      "lineHeight": 1.25,
      "index": "aY",
      "autoResize": true
    },
    {
      "id": "write-files",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 894.3736477578617,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 989,
      "versionNonce": 729851241,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "write-files-text"
        },
        {
          "id": "gEZESsXP0bh46KowvfnaH",
          "type": "arrow"
        },
        {
          "id": "pMzLB4zInNiFofgl3Y5rB",
          "type": "arrow"
        }
      ],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "index": "aZ"
    },
    {
      "id": "write-files-text",
      "type": "text",
      "x": 569.9927732297353,
      "y": 911.8736477578617,
      "width": 180.03982543945312,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 968,
      "versionNonce": 351932489,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "text": "Write files to disk",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "write-files",
      "originalText": "Write files to disk",
      "lineHeight": 1.25,
      "index": "aa",
      "autoResize": true
    },
    {
      "id": "component-processed",
      "type": "rectangle",
      "x": 528.2349149533682,
      "y": 993.777801513672,
      "width": 263.5555419921875,
      "height": 60,
      "angle": 0,
      "strokeColor": "#e03131",
      "backgroundColor": "#ffc9c9",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 1065,
      "versionNonce": 1568811241,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "component-processed-text"
        },
        {
          "id": "pMzLB4zInNiFofgl3Y5rB",
          "type": "arrow"
        },
        {
          "id": "_Ug_hzIUd5ivlzrUxoOpa",
          "type": "arrow"
        }
      ],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "index": "ab"
    },
    {
      "id": "component-processed-text",
      "type": "text",
      "x": 558.4927884885244,
      "y": 1011.2778015136719,
      "width": 203.039794921875,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 1043,
      "versionNonce": 587146185,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693942088,
      "link": null,
      "locked": false,
      "text": "Component processed",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "component-processed",
      "originalText": "Component processed",
      "lineHeight": 1.25,
      "index": "ac",
      "autoResize": true
    },
    {
      "id": "match-to-complete",
      "type": "arrow",
      "x": 212.94497197207912,
      "y": 489.0027799411689,
      "width": 0.053221249073601484,
      "height": 63.19257596539569,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 575559813,
      "version": 1466,
      "versionNonce": 1428697959,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "match-to-complete-label"
        }
      ],
      "updated": 1745693495409,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          0.053221249073601484,
          63.19257596539569
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "match-component",
        "focus": -1.9525714378687554e-12,
        "gap": 1
      },
      "endBinding": {
        "elementId": "build-complete",
        "focus": 0.001126879562748117,
        "gap": 1
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "index": "ag"
    },
    {
      "id": "match-to-complete-label",
      "type": "text",
      "x": 198.90886039679975,
      "y": 535.6530534632341,
      "width": 76.37994384765625,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 96,
      "versionNonce": 1715050119,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745692890508,
      "link": null,
      "locked": false,
      "text": "All done",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "match-to-complete",
      "originalText": "All done",
      "lineHeight": 1.25,
      "index": "ah",
      "autoResize": true
    },
    {
      "id": "resource-gathering-group",
      "type": "rectangle",
      "x": 420.0126859494619,
      "y": 327.111083984375,
      "width": 480,
      "height": 414.6666870117187,
      "angle": 0,
      "strokeColor": "#999999",
      "backgroundColor": "#f5f5f5",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 40,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 180,
      "versionNonce": 1816858887,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "resource-gathering-label",
          "type": "text"
        },
        {
          "id": "No3GKwzTAcDax9MiojCy8",
          "type": "arrow"
        }
      ],
      "updated": 1745693908200,
      "link": null,
      "locked": false,
      "index": "b054"
    },
    {
      "id": "resource-gathering-label",
      "type": "text",
      "x": 568.1009944575176,
      "y": 332.111083984375,
      "width": 190.9598388671875,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 118,
      "versionNonce": 1473980263,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Resource Gathering",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "baseline": 18,
      "containerId": "resource-gathering-group",
      "originalText": "Resource Gathering",
      "lineHeight": 1.25,
      "index": "b058",
      "autoResize": true
    },
    {
      "id": "read-existing",
      "type": "rectangle",
      "x": 436.4571439572744,
      "y": 382.8888854980469,
      "width": 200.44445800781256,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 544,
      "versionNonce": 67615143,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "read-existing-text"
        },
        {
          "id": "6N-w-y-fbb-EvC6JZKd_z",
          "type": "arrow"
        },
        {
          "id": "Lm5YCicKEwjG6SrJlxhgr",
          "type": "arrow"
        }
      ],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "index": "b05G"
    },
    {
      "id": "read-existing-text",
      "type": "text",
      "x": 447.68767963818163,
      "y": 395.3888854980469,
      "width": 185.11984252929688,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 492,
      "versionNonce": 793945863,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864109,
      "link": null,
      "locked": false,
      "text": "Read existing code",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 18,
      "containerId": "read-existing",
      "originalText": "Read existing code",
      "lineHeight": 1.25,
      "index": "b05K",
      "autoResize": true
    },
    {
      "id": "begin-resource",
      "type": "rectangle",
      "x": 690.2348539182119,
      "y": 377.1111145019531,
      "width": 169.77783203124997,
      "height": 60,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 1134,
      "versionNonce": 974901575,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "begin-resource-text"
        },
        {
          "id": "6N-w-y-fbb-EvC6JZKd_z",
          "type": "arrow"
        },
        {
          "id": "txAQy8HQxjXGPX1j3tK72",
          "type": "arrow"
        },
        {
          "id": "TKV39LSOmiDZlottftzrO",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05O"
    },
    {
      "id": "begin-resource-text",
      "type": "text",
      "x": 707.8720668452129,
      "y": 382.1111145019531,
      "width": 141.63986206054688,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 1046,
      "versionNonce": 9532871,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Begin resource\ngathering",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "begin-resource",
      "originalText": "Begin resource gathering",
      "lineHeight": 1.25,
      "index": "b05V",
      "autoResize": true
    },
    {
      "id": "read-resources",
      "type": "rectangle",
      "x": 560.6793119260244,
      "y": 485.1111145019531,
      "width": 200,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 577,
      "versionNonce": 2072375303,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "read-resources-text"
        },
        {
          "id": "6VmKlz1y04BVdreg61LvH",
          "type": "arrow"
        },
        {
          "id": "Vgds8WcHv-rwllevydla4",
          "type": "arrow"
        },
        {
          "id": "Z-3bD58eObNSkj3oJF7A7",
          "type": "arrow"
        },
        {
          "id": "InCdCyFcpdufmS8GII_rx",
          "type": "arrow"
        },
        {
          "id": "txAQy8HQxjXGPX1j3tK72",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05Z"
    },
    {
      "id": "read-resources-text",
      "type": "text",
      "x": 574.2475398676738,
      "y": 485.1111145019531,
      "width": 180,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 557,
      "versionNonce": 1509555911,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Read component \nresources",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "read-resources",
      "originalText": "Read component resources",
      "lineHeight": 1.25,
      "index": "b05d",
      "autoResize": true
    },
    {
      "id": "component-spec",
      "type": "rectangle",
      "x": 445.79045694555566,
      "y": 576.2221984863281,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 889566749,
      "version": 613,
      "versionNonce": 1495283975,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "component-spec-text"
        },
        {
          "id": "6VmKlz1y04BVdreg61LvH",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05l"
    },
    {
      "id": "component-spec-text",
      "type": "text",
      "x": 460.3586848872051,
      "y": 576.2221984863281,
      "width": 138,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1949657323,
      "version": 597,
      "versionNonce": 925688647,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Component \nspec & docs",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "component-spec",
      "originalText": "Component spec & docs",
      "lineHeight": 1.25,
      "index": "b05p",
      "autoResize": true
    },
    {
      "id": "dependency-specs",
      "type": "rectangle",
      "x": 710.0126859494619,
      "y": 574.8888854980469,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1355480981,
      "version": 708,
      "versionNonce": 1631845767,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "dependency-specs-text"
        },
        {
          "id": "Z-3bD58eObNSkj3oJF7A7",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b05t"
    },
    {
      "id": "dependency-specs-text",
      "type": "text",
      "x": 718.5809138911113,
      "y": 574.8888854980469,
      "width": 150,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1733104981,
      "version": 700,
      "versionNonce": 1267304391,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Dependency \nspecs",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "dependency-specs",
      "originalText": "Dependency specs",
      "lineHeight": 1.25,
      "index": "b06",
      "autoResize": true
    },
    {
      "id": "reference-docs",
      "type": "rectangle",
      "x": 445.79045694555566,
      "y": 674.6666564941406,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1483783083,
      "version": 694,
      "versionNonce": 824279559,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "reference-docs-text"
        },
        {
          "id": "Vgds8WcHv-rwllevydla4",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b068"
    },
    {
      "id": "reference-docs-text",
      "type": "text",
      "x": 460.3586848872051,
      "y": 674.6666564941406,
      "width": 138,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 575559813,
      "version": 713,
      "versionNonce": 1412426823,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Reference \ndocumentation",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "reference-docs",
      "originalText": "Reference documentation",
      "lineHeight": 1.25,
      "index": "b06G",
      "autoResize": true
    },
    {
      "id": "implementation-guidance",
      "type": "rectangle",
      "x": 710.0126859494619,
      "y": 674.2221984863281,
      "width": 160,
      "height": 50,
      "angle": 0,
      "strokeColor": "#2b8a3e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1284169547,
      "version": 757,
      "versionNonce": 1037616775,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "implementation-guidance-text"
        },
        {
          "id": "impl-to-generate",
          "type": "arrow"
        },
        {
          "id": "InCdCyFcpdufmS8GII_rx",
          "type": "arrow"
        }
      ],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "index": "b06V"
    },
    {
      "id": "implementation-guidance-text",
      "type": "text",
      "x": 718.5809138911113,
      "y": 674.2221984863281,
      "width": 150,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "roundness": null,
      "seed": 1071351147,
      "version": 787,
      "versionNonce": 2118127815,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Implementation \nguidance",
      "fontSize": 20,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 43,
      "containerId": "implementation-guidance",
      "originalText": "Implementation guidance",
      "lineHeight": 1.25,
      "index": "b06d",
      "autoResize": true
    },
    {
      "id": "6VmKlz1y04BVdreg61LvH",
      "type": "arrow",
      "x": 545.7727229981788,
      "y": 572.8052642622937,
      "width": 47.30404982368725,
      "height": 36.60343761385059,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b06l",
      "roundness": {
        "type": 2
      },
      "seed": 1801237897,
      "version": 87,
      "versionNonce": 703447047,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          47.30404982368725,
          -36.60343761385059
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "component-spec",
        "focus": -0.14907197530670954,
        "gap": 9.499993006387399
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": 0.24612620907912405,
        "gap": 4.055548985800101
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "Vgds8WcHv-rwllevydla4",
      "type": "arrow",
      "x": 599.8037261443935,
      "y": 671.6074528069355,
      "width": 40.53882491883894,
      "height": 133.0416386396846,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07",
      "roundness": {
        "type": 2
      },
      "seed": 1818662599,
      "version": 96,
      "versionNonce": 80963561,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.53882491883894,
          -133.0416386396846
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "reference-docs",
        "focus": 0.7471482901769576,
        "gap": 8.624072449867985
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": 0.10754451607894333,
        "gap": 11.166663487753226
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "Z-3bD58eObNSkj3oJF7A7",
      "type": "arrow",
      "x": 757.3322058954111,
      "y": 571.2875954741792,
      "width": 33.84082560758338,
      "height": 33.515771920341535,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b078",
      "roundness": {
        "type": 2
      },
      "seed": 1545336231,
      "version": 87,
      "versionNonce": 1919297319,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -33.84082560758338,
          -33.515771920341535
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "dependency-specs",
        "focus": -0.03612419808308407,
        "gap": 9.944451014199899
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": -0.2695214623176754,
        "gap": 8.944434483846976
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "InCdCyFcpdufmS8GII_rx",
      "type": "arrow",
      "x": 716.1137583068642,
      "y": 670.0320131514782,
      "width": 44.14977939494236,
      "height": 130.62735573922714,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07G",
      "roundness": {
        "type": 2
      },
      "seed": 553239817,
      "version": 98,
      "versionNonce": 1808827081,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -44.14977939494236,
          -130.62735573922714
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "implementation-guidance",
        "focus": -0.7239509963766171,
        "gap": 11.335609221312886
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": -0.01184352091943551,
        "gap": 13.388892491659476
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "6N-w-y-fbb-EvC6JZKd_z",
      "type": "arrow",
      "x": 641.0207490585129,
      "y": 405.1329125346552,
      "width": 44.09482620891515,
      "height": 0.5098887052896544,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07V",
      "roundness": {
        "type": 2
      },
      "seed": 43314087,
      "version": 137,
      "versionNonce": 1501866567,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          44.09482620891515,
          0.5098887052896544
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "read-existing",
        "focus": -0.1640780531010233,
        "gap": 4.2777599758601355
      },
      "endBinding": {
        "elementId": "begin-resource",
        "focus": 0.02852590417115995,
        "gap": 5.4999499850773645
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "txAQy8HQxjXGPX1j3tK72",
      "type": "arrow",
      "x": 735.3897552089527,
      "y": 443.1117345279079,
      "width": 27.741264404019148,
      "height": 36.04802330088597,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [
        "Lu7jj21UPmC9cu5LkmnFY"
      ],
      "frameId": null,
      "index": "b07l",
      "roundness": {
        "type": 2
      },
      "seed": 180458663,
      "version": 194,
      "versionNonce": 1848066473,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694355350,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -27.741264404019148,
          36.04802330088597
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "begin-resource",
        "focus": 0.11140668419726422,
        "gap": 6.000620025954788
      },
      "endBinding": {
        "elementId": "read-resources",
        "focus": 0.19414877883603365,
        "gap": 5.951356673159239
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "Lm5YCicKEwjG6SrJlxhgr",
      "type": "arrow",
      "x": 555.6585971353172,
      "y": 261.8426683137163,
      "width": 84.72089247115377,
      "height": 110.5915995218673,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b08",
      "roundness": {
        "type": 2
      },
      "seed": 936758247,
      "version": 277,
      "versionNonce": 73504839,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "xVAgpR0GaV1f3TmIDtleh"
        }
      ],
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -55.38083715945703,
          33.3795365834244
        ],
        [
          -84.72089247115377,
          110.5915995218673
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "edit-mode",
        "focus": 0.32587639018981124,
        "gap": 11.070642880362529
      },
      "endBinding": {
        "elementId": "read-existing",
        "focus": -0.7219531043557784,
        "gap": 10.454617662463306
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "xVAgpR0GaV1f3TmIDtleh",
      "type": "text",
      "x": 659.5709798633462,
      "y": 303.55554135640557,
      "width": 31.679977416992188,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b09",
      "roundness": null,
      "seed": 158002921,
      "version": 6,
      "versionNonce": 1413940903,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "Yes",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "Lm5YCicKEwjG6SrJlxhgr",
      "originalText": "Yes",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "TKV39LSOmiDZlottftzrO",
      "type": "arrow",
      "x": 757.0488218945784,
      "y": 261.9059533511263,
      "width": 75.31010413314891,
      "height": 108.57343605155523,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0A",
      "roundness": {
        "type": 2
      },
      "seed": 687006793,
      "version": 165,
      "versionNonce": 509096873,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "8RJwXFA9LGNWiMUP2N8CI"
        }
      ],
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          49.89556405784424,
          42.205137044061246
        ],
        [
          75.31010413314891,
          108.57343605155523
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "edit-mode",
        "focus": -0.4709659440177606,
        "gap": 9.318459145273223
      },
      "endBinding": {
        "elementId": "begin-resource",
        "focus": 0.7394161091333835,
        "gap": 6.631725099271591
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "8RJwXFA9LGNWiMUP2N8CI",
      "type": "text",
      "x": 629.5302613520402,
      "y": 299.11110623677666,
      "width": 24.639999389648438,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0B",
      "roundness": null,
      "seed": 1060006023,
      "version": 5,
      "versionNonce": 1811204327,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693864110,
      "link": null,
      "locked": false,
      "text": "No",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "TKV39LSOmiDZlottftzrO",
      "originalText": "No",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "JrrnHW0v8d0iK7XEIn7KE",
      "type": "arrow",
      "x": 657.9672537188909,
      "y": 162.24967745501525,
      "width": 3.5916628735916447,
      "height": 41.40642020378138,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0C",
      "roundness": {
        "type": 2
      },
      "seed": 411630215,
      "version": 83,
      "versionNonce": 959772519,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          3.5916628735916447,
          41.40642020378138
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "start-processing",
        "focus": 0.023683167370835805,
        "gap": 8.499991310968312
      },
      "endBinding": {
        "elementId": "edit-mode",
        "focus": 0.011216488877313238,
        "gap": 5.531463613547234
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "ySSobv5QuYECoDtsy9PpX",
      "type": "arrow",
      "x": 322.4084843739512,
      "y": 408.2221984863281,
      "width": 192.80568654826016,
      "height": 278.9443692101363,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0D",
      "roundness": {
        "type": 2
      },
      "seed": 180146279,
      "version": 566,
      "versionNonce": 1780497511,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "NKUopUtAQg7Fs4YyyBWRr"
        }
      ],
      "updated": 1745694288798,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.09150460581526,
          -54.55557017855995
        ],
        [
          76.53590157847151,
          -278.9443692101363
        ],
        [
          192.80568654826016,
          -278.7729242076256
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "match-component",
        "focus": 1.127588354989266,
        "gap": 8.318410397820681
      },
      "endBinding": {
        "elementId": "start-processing",
        "focus": 0.01116812420855947,
        "gap": 13.020744031156823
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "NKUopUtAQg7Fs4YyyBWRr",
      "type": "text",
      "x": 359.5488552517391,
      "y": 330.50006887647936,
      "width": 31.679977416992188,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0E",
      "roundness": null,
      "seed": 1049245513,
      "version": 6,
      "versionNonce": 2050530567,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693525142,
      "link": null,
      "locked": false,
      "text": "Yes",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "ySSobv5QuYECoDtsy9PpX",
      "originalText": "Yes",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "WM7UQjc4eu62cZzmhf5n0",
      "type": "arrow",
      "x": 110.82625442060541,
      "y": 399.3332824707031,
      "width": 21.659578429120216,
      "height": 80.21141096777939,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "dashed",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0H",
      "roundness": {
        "type": 2
      },
      "seed": 1800707817,
      "version": 255,
      "versionNonce": 1901156903,
      "isDeleted": false,
      "boundElements": [
        {
          "type": "text",
          "id": "6ySc2-R0LtKidxe2b4DF8"
        }
      ],
      "updated": 1745694278439,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -21.659578429120216,
          -31.055503633286264
        ],
        [
          -14.32185769629072,
          -80.21141096777939
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "match-component",
        "focus": -1.0307036212977265,
        "gap": 11.857736154251425
      },
      "endBinding": {
        "elementId": "component-loop",
        "focus": 0.8941879693598793,
        "gap": 9.03502031610239
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "6ySc2-R0LtKidxe2b4DF8",
      "type": "text",
      "x": 60.2066921658016,
      "y": 347.77777883741686,
      "width": 97.91996765136719,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0I",
      "roundness": null,
      "seed": 799412681,
      "version": 11,
      "versionNonce": 669770089,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745693587258,
      "link": null,
      "locked": false,
      "text": "No / Next",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "WM7UQjc4eu62cZzmhf5n0",
      "originalText": "No / Next",
      "autoResize": true,
      "lineHeight": 1.25
    },
    {
      "id": "TlqYH6PsCDPG6udk91uqK",
      "type": "arrow",
      "x": 221.6332405573659,
      "y": 117.99998792012626,
      "width": 0,
      "height": 24.000000000000014,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0J",
      "roundness": {
        "type": 2
      },
      "seed": 267050183,
      "version": 39,
      "versionNonce": 1514526345,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          0,
          24.000000000000014
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "start-build",
        "focus": -0.07314026933450148,
        "gap": 5.555590947470009
      },
      "endBinding": {
        "elementId": "read-components",
        "focus": 0.07314026933450145,
        "gap": 10.444409052529977
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "vXkaDZ84Vx95q_If5vxaP",
      "type": "arrow",
      "x": 216.454383877382,
      "y": 315.0942248689289,
      "width": 0.939056935310191,
      "height": 32.087568165422226,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0L",
      "roundness": {
        "type": 2
      },
      "seed": 538640583,
      "version": 47,
      "versionNonce": 915370631,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -0.939056935310191,
          32.087568165422226
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "component-loop",
        "focus": -0.037539217727723284,
        "gap": 2.6498278962726545
      },
      "endBinding": {
        "elementId": "match-component",
        "focus": 0.00605453416230627,
        "gap": 9.782672166268867
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "4kX9qa1KQzQdyPHPMVMQc",
      "type": "arrow",
      "x": 218.34720075878334,
      "y": 214.5142930292676,
      "width": 0.02258885210054018,
      "height": 36.13951050089938,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0M",
      "roundness": {
        "type": 2
      },
      "seed": 1702849671,
      "version": 424,
      "versionNonce": 1379671401,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694322821,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -0.02258885210054018,
          36.13951050089938
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "read-components",
        "focus": -0.0458152814053177,
        "gap": 2.0698960566113556
      },
      "endBinding": {
        "elementId": "component-loop",
        "focus": 0.04529255544040108,
        "gap": 1.7905934424892678
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "No3GKwzTAcDax9MiojCy8",
      "type": "arrow",
      "x": 665.0829553727528,
      "y": 743.9962399756761,
      "width": 1.2286518662745038,
      "height": 49.204726843819344,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0N",
      "roundness": {
        "type": 2
      },
      "seed": 996460329,
      "version": 203,
      "versionNonce": 2115357193,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694335782,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          1.2286518662745038,
          49.204726843819344
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "resource-gathering-group",
        "focus": 0.00034113018436506915,
        "gap": 3.389306545125919
      },
      "endBinding": {
        "elementId": "generate-code",
        "focus": 0.05482991593078177,
        "gap": 2.454290873120044
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "gEZESsXP0bh46KowvfnaH",
      "type": "arrow",
      "x": 660.0126455360576,
      "y": 854.3383522863093,
      "width": 0.24589269522857649,
      "height": 38.87115588992208,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0O",
      "roundness": {
        "type": 2
      },
      "seed": 1419197705,
      "version": 261,
      "versionNonce": 1854568199,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694335782,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -0.24589269522857649,
          38.87115588992208
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "generate-code",
        "focus": -0.0014646109516322778,
        "gap": 1
      },
      "endBinding": {
        "elementId": "write-files",
        "focus": -0.0033574349763533357,
        "gap": 1.1641395816303657
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "pMzLB4zInNiFofgl3Y5rB",
      "type": "arrow",
      "x": 660.3273200205763,
      "y": 954.8254451370203,
      "width": 1.6762311007936432,
      "height": 37.16520851425264,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0P",
      "roundness": {
        "type": 2
      },
      "seed": 810555273,
      "version": 280,
      "versionNonce": 1858183401,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1745694335782,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -1.6762311007936432,
          37.16520851425264
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "write-files",
        "focus": -0.012679826081854605,
        "gap": 1
      },
      "endBinding": {
        "elementId": "component-processed",
        "focus": -0.020996382804093442,
        "gap": 1.7871478623990242
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    },
    {
      "id": "_Ug_hzIUd5ivlzrUxoOpa",
      "type": "arrow",
      "x": 517.3991931202238,
      "y": 1029.3560781594817,
      "width": 534.4547156150668,
      "height": 751.5995291234158,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "dashed",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "index": "b0Q",
      "roundness": {
        "type": 2
      },
      "seed": 576766729,
      "version": 1542,
      "versionNonce": 992018345,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1745694215011,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -197.5658911521761,
          -55.800580248238475
        ],
        [
          -421.1214331443636,
          -233.63387161990215
        ],
        [
          -534.4547156150668,
          -536.0783077461871
        ],
        [
          -513.1214331443637,
          -741.6339021374803
        ],
        [
          -434.929376342646,
          -751.5995291234158
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "component-processed",
        "focus": -0.6822153893110063,
        "gap": 10.835721833144362
      },
      "endBinding": {
        "elementId": "component-loop",
        "focus": 0.4710666539072743,
        "gap": 10.863557245859681
      },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": false
    }
  ],
  "appState": {
    "gridSize": 20,
    "gridStep": 5,
    "gridModeEnabled": false,
    "viewBackgroundColor": "#f5f5f5"
  },
  "files": {}
}

=== File: recipes/recipe_executor/docs/recipe-executor-build-flow.svg ===
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 962.192248250424 1028.0518890578503" width="962.192248250424" height="1028.0518890578503"><!-- svg-source:excalidraw --><metadata></metadata><defs><style class="style-fonts">
      @font-face { font-family: Virgil; src: url(data:font/woff2;base64,d09GMgABAAAAABpkAAsAAAAAKbgAABoVAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAABmAAgSQRCArJOLZCC1YAATYCJAOBKAQgBYMcByAbKx+jorTx1cj+6oA3sV7KiIhICK2traPDavg5hoo1NwOkkuqHPYiZH4ep1+ouNDzN7d/d7W6Z5DaqVkQJi6K3wRhR4UCwEAubUowI2uAHJj/Kyt8YhV/7F0/Inu3dfWCjspECgVCpJK3BXmjFqje8bvZhzVstJFCNFCoGNU5EkC8iw3qsN4eagrdOoWLy5MvRXLmxWTsQqHsgVV9j/9mVjM3ZOzuzu8kDBZ6huiwPfpqzL/nnEls4sKwBQHL1CXXCzth5lppJt1kIlD63XSD4mUSLTdGg6Zr7fJK/qgprWLb/u6b2MrZAkkDV+ElToF8AiBpQ6m7u3MiJCVNmlzeVITnDwolOzpmt5kydA4MDe0iRCwCvNgVwNaYbCsA/zQBAghJFArCa3KcPGHqBjyciAIBgwcy3Xg+URNqOlv+V0LVIWgBA/3pNQJ/+EwAiXYrUIXAsLaQHcbpBRFrc6X29BImlYxAniUkqm3wN7Nr2v7FbhRK7LZOFmrT+nP//unu7vou7sPM7t8l9sdUtbW6zm9k0CC6DNlBaPwulcWEDlG8f7QmNBOYgAtLDJx1EwlsvfAB+FNwE0NEeV/ZtFj3jruLwkjWua+u/jymNENeY62VRHH++3CbjZ2VoBc58n2R3k95J5McJ1BebTLmJZKaTiClB/OXRiagepyxcSjuUQm8UvswIFR/RC1QJTDJGGqf5HfMk+j0w02ZAtPhCxRrrIjvhAKcBuyVoWE3IOHCapR7FqG0gp2b+ebIdECJF5ZrE3rkclHzurCKfoz2vOkRnawCh7QaVPjmBxrCgeoymITVbLtlWy2E2kXQ3TJN1mW+nPmuV5VZK9VQ2OMCVH4An0Dj69Z3DuF7E1Nx9rodobAmATKKogsMBloaHkgJIqCqSDdiGEJmkA2UAlA3mupYbW0GjqdhBgY7bU9G/QQontLJ4LfTw97Af1pyLUiHvxgY491Ipd/i6i902Y7uMeRwW6MoNukRu8owGS9eEDcd58oyWfz+RIwHxQ6Lh0ziwGX7Cv1DQrYvUr9TydV4p3+Om8SH7vLZNhsmGOzVzV/u4cBL9rdG+U3SbIM9xy+HWXoXFnG3B5OsTuYCSjoRAWAWAXUQfYADLh+G3NnhJdZfUs30vQ+/NdaBlME9WY4ffFyWc4xaNo0k1BoCaDXL/kBu6CnafhBN5kRc4Cqjvp5+CtM5+3/h0YrLO4nizz9duVQoIRUxxdH6kqGY9Fr3V0V0+8vVQFDt8Hoz6pZLqeEag2P0jsl8E4v8YNaboSZx4DSogXYCNgkpGekwHwkIIC4rdI64rkY6F+IQGMS81NACkEKMdACULpCMASCFAHaIeQDilOu7sQMzTTzlGmHpZ/V/qpY9+Gcc2+RNzsl/HC7St1FF0q7LaJNe9+3f+kjurWEyXnmw9CNKF//ELuEXdS+zhsRVT2QjnHHNnxX2Lik2DBIihjM3vGtmmswROX0CjL2NnRdW8U5BYaHWNZZOPUTY4L+H1ucIICyI5LlAoKe8VK20BjNci/X5sdAPfFugEttmhLhwOqYphvYSENorUDWnQwI9EnlYF76Y7cFr3XyneSxYo3ypdrq8tEZqOOkrIKgBnWVikELt3gfwzAK11mroabZASqsYEPTD8b8tV5qrGDHH8Bga+jTBP3lErUFgCsWhfHORNVhvfFzEltFizB4CyTEoxbC4rJIK8jHDfOUMCm5pBYij6kDrSJqK0kSTlk0chYroSzvFIs+sWEBkEMuBCjtSjASZta1Sfthw1EGJ3mSzWUlGW2DI3HHUkhFAhLEmVFYtEqzPZ0pybJsmj7wekn/NgLoH2nRYfG0N03AT0sQIXIjYhaXcpbRLS/BB6pyhjRhMRB9LCqVMNwOv7SBv3Rtx7I6vZPhb/th/2i8W58ezsheayCaoJLEkMLbi6K7NTtVJtNserHvKsPwQmrF3Vclxpnl20lXEAirbSSCuy+njH8tfPqSeYC9MkY47XkFJYNrxycYQcn7t61HemUjneeK+HotaifQeX+PH6THHzETFECLo8i9BkjutdWu0pChOGd5MISNqr52DXh460884wYNAqdqnSW/PLS7cKO1tidW1nxL3VHmk8oAraNWHSVcRBTb61bTBCSNiZaK0NihwS+lqRF2omslmLgcubUopMfCYem+xnVO6CRyn3cmflqh4nYj0gZBdAiBIK3QHvSqtIGUVq3xZAn7Fb11LrjH8zBGBdng/LeqjzTXUyXjP4fIXEolIS5gHgDm8E2wDek/Y88dMZc0XTJ/OljlTRJMku9U4anD2u6/GWmcvmBdqymmzf3hX+YvF0YVjWhSbu6AXmAqQrJ/Oqv8TH/vVQo1en5at4Vq2q25OIX4vQ7NKl7BYuFiV7qxZIbVrrxI5ak6Fjji1aROoJiCOmCHap4qmE+LGcGKGouy/h5Wx1Ve0RUlh+jh4LYcs/r+3UO2blS/RBumL+aiQz3Mu6MEL7qX2y+jiUGHo/HuBOPD9bqtKyiACiRDMY2NNq6c0eJuYgXaXsTcZV2eZmZJ41d1hB7NA1jwEYM8Y8j8NEZaRbKFWtgzlmbuYrH0o2Z8x/3qV0C1Ge47lsdC8xO8yp7Bq4mDBVHNeyPZsZA0gxN+l+aIIj2Tza4CWJCGwCuKt6RIAfnQBtxWyYARDnWtIaEt5NUUBElRLlYKKjfqE8eZb1v09P0hRO2lA2KndSq9fb85yIUa7GXPM51YGfiysoJhkrIlAA8GyzcldoCETZmE+aqlT1k9yM+MikqTepB4K08Bfng+vMObZa7CenGigPUfUHI7a02u7R10+TIudHUOYUVbz7Xc8nt+LlT+QEOg+0FYdNca5yDtfd7rtUsyabZ/nR0hnnjFf7WMuBospEn6pPmou+XEpes4P7mRhFoxrYxUgySjaPU6k5WfaN6m4mAG2pYQrJruvfbd6IZBVoGBy0VLYiSpf/r4gBeBT6h6RhEqSRcncXaYJANZqteptvYPlu6VjdNLJaD88FeWrNPM9DXX/KKRinXOXePXcUWRnHMfDpN2QkLRsuiR1+wG2vWZ4yyMiPAWS+369SpWt+I9YE0fhNc4TOITijPp/KXxPJnbN0+YGVxKWmzllWA6aEGI/780aoqvEgjbCJ+BxlWX7nTY3ZXTcZQNPUP+WTwtLVKk3kfyFRKtHKtVS5Rkc4sKxx6ZLx5sr18yxpwvEePfpoym8FikpDRopZY09yUlXSPCqGRIhWPVmtT/gtFmFYCyqHE8n27c3Ttruj6hFIW3ipbckU6hoaP5So/zClniDJ0FhaR6SPj480/9j8AtAqfflcvhJnK+oHRJDaIDFQZIQLVWbHztc1YDeus/b1S9Y2oHnfUdQxj3R0hcXlxuSH6eTEQ/zlL2t3xv6hc5UOYrbYT/k/fnQN+od6jdrXKIZ3U1U7REAEgJ1QxYbE0jcO4CT9/wnm47mXZ/dyyzH/3Ey6sdRAYg1GLlXTY57HMaBLtrRRsUUfTI+yHXZyrzqOxOFzpeRY5m2jMgWjG2xcSGFmYQbAktz59fY1675N6UPM41aJVzE1UMIg2HMTEEHa/tPAY2isxAUJ7XhbELn/l6QaHtaUILwlz5ta2Xsx8b6jUZMd3c983bvkS0Cei9C494wOcr5UC4CY4gfKPASAhCKs2uqhxuRKiYGONH6QXkgQ/UHGaIMqgkrneEs5N/ljnKZ/AF7AFKP55FN/VLNabjmYKibeC9no8URLACAKe0jQ77PTuul7z4EDRwaO8I+M7BAObBkY4HcD/wp2SHk0rX8j6L/G2XpNunHrTsFGj/6VvOOGOSEuFoOysoptdIMLBbq5h/929bkl9QkoNDQuZDsmVaz6/1r7YI/ooui13v8XNjrNlpopfQZCQYH6q8A0YgSenMcle2MOqu3O8OEtNBus467O7saGxnW8Yz6riLOAVsBLgNqKp736Usj5+ee5HdtrQaMD6esTbku/XupmZ9riWo9yLVoKNWDXWB8DhjAC37hszI0ym+qzQK//UI2Gf3fmzJl87QRWgrq5Km5rmpvJwtG8RvbDifmRaRX0lvqNFM598DiDtMEK9Wu7eJs4ZMrvmPxMSckBxkF3tulqnu2dfdeb7YE6zUdODtQJ1Td0IJwJgKHxArq7KwZBcJHjJhrM6jm/3BMiQ4empYokZhxKSGNv/nofjTr2dHYc5fKldqCBsQaRuvnmaIk0CNiCPoo196SZDeDfaB5xdRtyjjZJRtYAPa6uRMi9RkJYhF96LmgCUQX8QJUAmeRN1LYstkH4tiYN06YKDeGMibc/hqdtOdWgVaMmanaiFsPrUKXY3pD4zYA6djaRbIRvF0DvF8F9FukFi0Pscq7enh150MOZU4IwF/X6vPCQcxmaMk5bqwFxI25xYGwGeb+rs1TO5c1YA4rBLQwc/LtY96Fuoff8r1JwFPhLxwoNkwGgq6O6irRVuZeZpJxnL9/psjYmm4JVdc59ALFg/Qibpre2OcwxdyQIkOilPpdPqa3buZXAWnJtGB40NVpGRjCUaf+UVU7SwyQ+4ZyBeAEC7ol8k/dwxH0n8p4PGlGXF63LbNVb9O7K0/m3Db9cuV1w8TeVsIS5mu7Rqqe+Ipx20X9m2kEqi5Gz9FY8apbF24qXZdc547Whn0GqGCgLp2bH1cV7EUEFloWyCRocAYXYWD5cguYrfkOVWi/iOMNwmfv44GjfuePLHHeGeG0Y2PgDGhs2tVvmOVSP0/P3anij/5bi0QQMDxfDZb4BSJ6zlj5IGpzUnP++PPSOZQHupp2f4rSH9LZtv+ygbJERp0piwcRQMnMwCRlkskCJHUOTkTT6tUcx7Qe619IvF3yduaej1vyM8z/5Xmy1HJQJ3FdxDngtw/TeFDiWr2qW03ei751KS/NV8yF7TWiSrii81ju7M+vweOycR09lls+in2rGd+c47pazWxoRykO3AX+tnzJVy/Qu8coM3TuxzieO/MfEFquL62cNkLRrhRVvTmOuZxnxF3fEn4igMSu94uIJPh9NKFw49YoJacCzcoe0wIPM0zp6o/FPGkFLKqEzR5OCCcH+hQsTuYCR3jC0PWBXmuyn7l8EcQ8s18s9h2cwNuIoRxgaBgJpoU7R0waCEsPBX5lqqEyo91zIYbzPysI7TRxUikhRbpFwA/DbGTYPbESqiBZ4UGUOm34eJ/XICpnDjZf55wUQsHzo8UAgmb2HGr//WcYb31xnNjGz7o7C/cJyUsdOyyrLfMB0KltARKqDYOIyGjDLDrMLNwXi02cDhgxsMVbm1DVnuKlCJZHQQIdrHjdgTlQ9OCP+GrkhL+Au2tC2KznBPZXA1eZo2H1f/E7GXzd0XYLneXjGTCFNB4TKjAEsg9fAA7imnl2MvbqTRCUEhjrx1WE7eDjUEAVd/v3beNN74HMt3mlt4jSc6nO6LTw8xJE6Zt1qxbZitewij3X++jzuSAKw6T/8/rWgpF7tsUYhSIziAxEVi03ogUFrbiCk7vhEcjLgWc3M35Vvz7fwlwIy0JujTzA9eiV7cKpfQ9x/ARTHIuD17YlozvEWq+olzrdQMVaWgJrcTegi96xAqyHktjP96MjHJ11y8h01ugjLWBZjMszSdgEWBInKOlCGr87OuB5yb7rCampO1H9iiy/+NyC+Es4V/fQfdZfnYcl8v3sBCjWLeo1CasQNstHkELEbx5vNmiCl4bMJFwBpNiPoV68BGXT4jZcSiic+6R5I1cmstd5zo+k3tw02mqTQXOTUL6s6DKCp95P67PqiZUoy2r0MzoFM7Arp8XnBY0nOJOzslgRhc3dIbPLSvLeq6NrSWqgZTnY7cDgbPIHMSBtSwKPkCKKm8622NH4YqR7LTwrSIpYKBjuhXroudu2II+fYt7YiqgAz+rhSLPjJ65tU7ccWVnukNOGBJPaNqwPfdXYyl1sRnl8zI+/aENcv+/Vd0y6bqHD0mzSI1X5aYRGg5hCl9a8X95792olfcc0tE/DVDt9ZISmqJ2MN6F9DdNMEfQcXyy4T7YGtokhqqYEZQClDYxEUruk4QjChHYy/0VACZSUYWGffHVei3fm7SuC1pupWipXrB/npTgeUuPUY6Sl4ZuXm8O/uzZWV5gbvDraXfOxmHIZ9oqDtAkqnV1GUWrYkvcyP6+jBvAnNKzUic/DB8ThFX8ZIAw7wQ0+TnLgvqNyqe8wBkvMMSl/uzFhJUIsQ5K0SZ8aYxs3CIJNbeMOKgcTgAqjE4BsfRMyBjDVKYviw14yOBj5pLcyRttGDHLZmZKA0CdDP1a3r5OV7P1JOicvqYqcmkeE/I4L3PW58Zb9Wk4gU+u99F72zljXHofQrNPrxm+KfatjxhcJ/P0EP44kpi9uTKao9MGnUIhWPliqAqWFMzH9fFabbzoOQNohHKNhGXdCJjz41Y3FKCOTTsTrMk1LtIUzyUAI4AZbYnJ2U8a5PQ/Do4Ca/Mcz0D2cqMlFhiDs/RZV9fef4R8wMypwN2VanMuRytj4Al27ThPKD/3TDZGKISFLas1RIHw8J6g3swxeeJnqGq3evuzQtsiEmaZynd+4T7/p2Lve3JbhOgjsUS/FTOr09aBY43i6DQkEysf1AJnehu5DRHTmCQfl8jJxNZg//z87yZb+vT1Rm5BWPehnERNT98Hd7S1+mCbSRSmuJLcnj0SUTbSmt8tLXG9i2qwMx/uA116mau9OL79BCQAnhzgvJ+HtJ4p4Pyzt927ksDUi8V8hnTWh737shII6JJcRE0Oxx5Ci5NGF5pJEUlZp+PjnMADACZWJyXPf7rDhtVFTc4bIzzLseIjUnX7hqK8L4XTqiWuKhx5NwLuEVOv81jC7M2nov4BGLrQ/Lqt2idACRzyd8q4PjKqiUG2ReL2tLsAeCo0oUUjiBhWTDDsRGQQR5cRP4/wx17CCS0D1ENtZin1PG44mNHGHGDucMP08OM51M8Lpm5OtJdA2gBuT9Bpl69qUek2fYIpiVpFYe7LuGQdxrfOyEN+Ez8I4uj70u/sitrb8aSHCTQLDEt0q9F1CBu6eJR27V/td1dD5PvwXvR40dMScEigNcer40n+bRlmZQoao0o3Bslfc7moKaQzMepX34ZbNCckPAS3maJfe9UOqFW3IyMxlsXztYDMEEmFi0J2W+buqwIvAMmVTuovZjo2ul4x6wqhqf7d5mbNr5oXIjqpJO76cwsXIE0384N9uUWwg0pC/9GZh/s86lJ+PyAh1NfQeuCgIJg2TyN3hAJAe28ZyFVBJiIFGhXE4lFE+N8KuY3EFtn+LwpyDuLDNoEOUHvGp7leF76i0nLL/UPTqp7daJ/vhJQiZk+9Jlixel9Vza/3XjKwPnwcVEWap2DnNbCkvnDikSn/fB92Jt5CpYBrQFnupVuL0FHtvh15E8Sg9g01VhIRZ2UHLjLu1nwjjyehcUiUBQHEMzIzpf5U8kQXZgq0gOvaO/Mckg7Knqrh52NVhZZuQs5PhEVIGRHFhl5SxVjtdxo6GQAJyX1FT5VT5p/Xv/xtj4rtgphf5YbO1857elDVKCX+UXccn+tTPD1f4+6by4cD2Zdm6TMDgtKIAX3rnpm8Vu9DPH0SwnLyAjzXzN1lHxfXZXqfFfyoIXdTFudyzB23BEeJkYXxVZ0rspdKih4U7650xvA+kAAZQ5QpYcorYvN2ROaoJztNPXjmrNt7e79vU5xaFEMXAnV/+8Xhahn0oLViB8iekNbXaww+2fCFLl9XFr7AqXGP/0at7n8btWUWlPF9zaDlQ69nXPcPlTl71DSjIvoE/RErg9SV3qmhChL7rihNWqNOyPOR6pKCxGXslGtC1GrmUpap4Ztf9989rS9z+PmGEciRKX05TIvjrDbBQvWAAOTEBml4R0jQonIroMFd39RRPBzqBIy1jl0NYK3t4gT8hWBr2FZXeGVJf3HQGLCt/rGUOMbrKe4sXTnHCUzRCvSF+bRlRLdK2V8ww4O+f45OX7ZmXB3LAkU6NoAflytueVcU8IryEAsMtBGf79MTyCK9hDE3/0gANKiIl1/q8jyBiaKQ3b0G70uo88vBl7BSpn8UhWKhb0ju0mW3QTblwRREFwsIdnpMT3XdEnMjf+7QW3xd3bQlAE8IQYhaFSqMoLbix/4EbMROvweCVLwMPflKncsuFaLSuUcLvyIus09zv2/j/UGUeNpcxSyKwsoGU0zzIGafVakfxHe6mD1rgZEZGvyncSbf4xrs5QDkjHVSZ0ppSpw/szX5Wm/9IXyGtNJ+Aa+xhdR6JTC5UILEWL8zRteZFWHNMi0rFCIQT206qmFquFvo6ds2a4vC5mm6jomuJTgOPHSXNnf2K81olBgnkXV2qsgruSoV0pm0FrEaUp/uLnDir9Tz+Jxhmue0rF2TWqQpKR3+HDfN9hwPxnkAKKcXrQYDpzNJjzw/B+nDZ6Teo8gbNbUrunf0LwCzjSs0EwGHNMvqgsJ8SR9KdovSdAHTTPlzSQPJOaT49+SyAjj9QUuFNd+236S+C3oxcr/3//9wn35DR/Ng3BMgfy+UPT2cMwsCzpixBfkl90APQLwB/RYVHnCnK7kXpzb7oEclAAtbvxD+4eVYxbG2r/w+l6zt1P0ALEPuFwRJr4W7DzD17evb61CHDdsTK93/IWLS84uGvQGNeVh3sdPEhsG/9cxa8fXp4T5Dh+hWgN2eWG824hfuXouY4V6Rk/DwwGsNZCC4cS8vGyIKAT8TbaaXIOQjE6B6PZP4dIZ5rD4YmcQ7lyBkwB4KxValJ+IGsEsigFZHcXavqMSlEzWa+OiJR8MkEnoaPoKGRKoafnG6M4x4ly6o4iX0h3EAXeRGE3YZSEjkiNeg3aHqFSJ6owm4iPYr4nGYCMxOAu0qYgkwd2tSGSojViWn0E9bMvYNdQYhLzIEi7VWpov8hTbfMDlJ5QKbQoKGE5ELgSCgAA); }
      @font-face { font-family: Excalifont; src: url(data:font/woff2;base64,d09GMgABAAAAAAdkAA4AAAAADFgAAAcPAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhYbgj4cNAZgAGwRCAqNGIl3CxYAATYCJAMoBCAFgxgHIBusCaOiglNJ9s+FzIlaxuNLHGpqsxBRLuWXHVt2oJTymbyKh+/3o517//trPl2TaBJHNIpKYysWCdWmM7RGXkrzNzyd+i+och2y3l1UpAgrakoFJJsPQetkEoMvoAGwiuv3P4B/////3mnvUzTW8bGE2wJZYu3b2q+1cG36fQo4sXTj2JRGYZoG2gkUA08tneGJFHSAfV8VcZjaKtAHz0ih0S0EeiyJQj9yLC0PcO/0tjUA7oO2ynrAfSrraAJcdPhtND2519YELHlMlOxvOqCrgy5xPjZs/ug1M90M/shvZfSNkK/fuOOTFqihl/pNldBq/mcyXoLx4MbAGQuoE7VQxLg83IAi9V2rGNI6OmZwd9NEfZbSOEi0CpOiucREnyIwYtPCmIfr6o3jr/BRZp8B3DzkcMm82KXVlfIMcFqmiet8/AW6YeORM4kZ4IZxPU3Xf7k2vCG6xgH4BPEhA4w/FOPFwpjjDGHTXUyMWH8pnxznKUOxSs069NTKlGj/xnrgtbMOW0LC7C4AgnSmQ/QkjGlacwHIt8AonOGjJOICfwSbYiQwxz6qtDQfkxK842/H+nKFpEbD4q09LNrvrtLDxBG9WI/L8pQnjrjky7kLnuQoi1ykHDfxyFXnJ0YXA0n8IITjKmTeYIcvI7gKx3GEVag5bVo0sUZXeaui/TfZI3p4BIP5ets5PXxCrBUSh9THULWRix1RLsFK5Txbz8Dy5eghp1ETd3HBHiUIAiX2EWpiATXajxrR0cPQeeTgSQNHJdHtF5EmlqmQZOlwHY7gtnlPwub1tpierSxcMcWaCln7kbsGx2V9nJYhTxEqwbIh8WyqaH/ifg644ueiD9AXGAt1EI7rFApo/3WeJkUov3BAzM6/d+7SMftCYpR1ufAypDBEG7z0edgZ7b1ChcnkQKjVxCHUyJDDWhg7AF9gY8p5gB9FdIWkhnU3HD97VncfUohIDbrPiBoLiENqdCE001So0Clw9CHzYvkd7Ix209dSIhcNEgMYybtjDDknOyclTi3wjM4aezWqheVnUIJQo8QiK/R8Ioty2P8gBzcggv339/v7n7U9AGvP6GG5Hzwyp0JG3HGdiASwzO+rEZA4h7MEHznwJAk7k48Jj/EoZCiZSpp4hPoQeotLIV1JSIHjiAQ3RL0QizSJyMPkfnBEJL4DjKgw+ICLPg9D8nHBrW1UwSMuhHbfOf2XEHKG9sAVGHsBa933nb7G3nRkmr64eTeVGwe2XSu282cmtf209xiU/YdxVlAoDTGqM0HecCuo5IWXjyVIc+cNfSuPZJdQe6iWnnunXe84xKbUJ2f9Pk5JTPFDOqx3ypCP0pAu4aCyY6sw5kGJTfL1DUURyA5Lxdcfhu+gIok0s3TLLufBbRfDNVv2fCSMf3np8x0uz5zas6eo8tfo5RIroVmK82nwThjUWLveBilFQfULJtM5FuyzP3gv5UUgkipAmfHrIBpDRnLWWGXlSa613l07GRfmExMtyvh/j/cu/8N9D+8fPFQFe9A6L2+xqTn3GogK7rhU1UVkp7F/Kr/Rmh0ppGcX01DEt+G9h2v3l6WN24zefzu2TeAEfzSVhWZn0mMkcc4lX3Wbtf8azbCj5n7iu6MVgR/7VC+Dd+jS2mvJf9Nr66S1x6LFysiUmcj7vglHIxsHbX+tbPHip4oL0OSgBCh6qZrilOfh5nD3EjNvd5ylyBWiMBp/OFUPouNtDIIgn6/ttCejINtHe/273BfSY/K50f4JZa945o2fb3TJNaM60n70Ph3XlYTkTJpl/3Cm82+TfvL370/n/1gUGLP5Iwtmq+PQEICDXpYKXp0TQP1COKkg9tYbVnYny97+IDbYpsj6xmr1hRpU6yGitVQJvN86Gf1SdxiMyn5PWH+StSlhXRAj8zj3v0o/r5+zTkdPxHfXDiTSO+FjN16+mx21tT8wPauVPwSSwpcz1fX02tSxzKqYIKz4x8qCD/a6o90FlvTWvetnDoflyqJoSx05McGxODGIGNYzc/jxGwIoNKo0TldVGh4Vj6BJQcz+fX6Z3ve3G/fXjew32M7imK/W91DRyWPz2W97fsuQRzr5quuXLYNht4RoX8DB/kwcAPz8+nV/fff+8lUJBnRJwvz19rUbFPr+Gf1dvbanKRMfu8hl9OzBSz/uyZF9RbzSgTglKJlpHSXo8UOH065RlNmFY50uo4liBXjqVScJY65J0oDvksaMKUkxrUzS2uYCHcF9gaN6lJNpUKtKsyYd3OWoVK1TA5k2BSq1aVeNwRA+bx68UhwqUb+mV4sa7fh8efDBJ26Qz+RAkp0r4JN3NnucXIkyhFLkgFqFWMEtepWGWtVqHAjEBiBxsQ+vHPwaKFPH+Syu0Oa8380DX7QGDfi8s30AlYIqocttquCBBobqf1oAAAA=); }</style></defs><rect x="0" y="0" width="962.192248250424" height="1028.0518890578503" fill="#f5f5f5"></rect><g stroke-linecap="round" transform="translate(151.5244827968972 44.27408754417837) rotate(0 100 300)"><path d="M0 0 C52.77 1.58, 103.46 1.48, 200 0 M0 0 C67.68 0.26, 134.44 -0.06, 200 0 M200 0 C198.68 129.2, 198.5 259.78, 200 600 M200 0 C201.81 146.95, 202.52 293.97, 200 600 M200 600 C156.19 600.38, 110.76 600.14, 0 600 M200 600 C132.57 600.69, 64.2 601.29, 0 600 M0 600 C-0.24 380.57, 0.38 160.34, 0 0 M0 600 C-2.33 439.81, -2.54 279.39, 0 0" stroke="transparent" stroke-width="1" fill="none"></path></g><g stroke-opacity="0.4" fill-opacity="0.4" stroke-linecap="round" transform="translate(431.53716874635904 10.477537668418684) rotate(0.10536709032008844 260 356.45382276244266)"><path d="M32 0 C181.79 0.66, 333.44 -1.2, 488 0 C512.45 -0.26, 522.77 9.03, 520 32 C515.86 256.11, 516.56 478.99, 520 680.91 C523.46 704.27, 509.72 714.55, 488 712.91 C346.26 713.31, 203.05 715.18, 32 712.91 C9.44 712.05, -1.63 705.21, 0 680.91 C0.45 537.86, -0.83 396.25, 0 32 C2.9 13, 10.46 0.5, 32 0" stroke="none" stroke-width="0" fill="#f5f5f5"></path><path d="M32 0 C181.7 2.02, 330.36 2.24, 488 0 M32 0 C143.64 -1.04, 256.04 -0.6, 488 0 M488 0 C510.71 -1.07, 520.72 11.94, 520 32 M488 0 C508.92 -1.82, 518.93 11.04, 520 32 M520 32 C521.77 259.66, 522.08 486.17, 520 680.91 M520 32 C519.3 227.24, 519.48 422.1, 520 680.91 M520 680.91 C520.48 703.97, 508.59 711.52, 488 712.91 M520 680.91 C519.23 703.4, 507.49 711.33, 488 712.91 M488 712.91 C382.11 712.72, 276.44 712.01, 32 712.91 M488 712.91 C354.23 714.14, 220.52 714.07, 32 712.91 M32 712.91 C11.35 714.89, -0.84 704.24, 0 680.91 M32 712.91 C10.83 714.71, 2.21 701.5, 0 680.91 M0 680.91 C0.1 463.26, 0.33 246.16, 0 32 M0 680.91 C1.23 520.46, 1.32 360.78, 0 32 M0 32 C-1.26 12.34, 10.09 1.43, 32 0 M0 32 C-0.82 12.04, 9.51 -0.28, 32 0" stroke="#999999" stroke-width="1" fill="none"></path></g><g transform="translate(599.4972593835662 15.477537668418684) rotate(0.10536709032008844 92.03990936279297 12.499999999999996)"><text x="92.03990936279297" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Process Component</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 16.71848451683462) rotate(0 119.5555419921875 30)"><path d="M15 0 C85.51 0.55, 155.71 -0.17, 224.11 0 C232.04 -3.06, 241.2 8.28, 239.11 15 C235.98 21.58, 238.58 28.39, 239.11 45 C236 53.36, 230.8 57.21, 224.11 60 C141.25 62.82, 60.08 63.47, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C74 2.61, 131.87 2.4, 224.11 0 M15 0 C67.8 -1.62, 119.73 -1.97, 224.11 0 M224.11 0 C235.7 -0.51, 241.05 4.95, 239.11 15 M224.11 0 C233.23 -0.06, 238.81 3.87, 239.11 15 M239.11 15 C240.15 21.29, 240.51 28.47, 239.11 45 M239.11 15 C240.04 24.55, 239.61 33.49, 239.11 45 M239.11 45 C238.85 56.4, 232.54 60.76, 224.11 60 M239.11 45 C240.16 57.23, 232.46 60.95, 224.11 60 M224.11 60 C162.58 59.59, 101.65 57.88, 15 60 M224.11 60 C155.83 61.64, 88.74 61.7, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(168.1334686977761 34.21848451683462) rotate(0 76.2799301147461 12.5)"><text x="76.2799301147461" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Start build.json</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 116.71848451683462) rotate(0 119.5555419921875 30)"><path d="M15 0 C98.73 -2.5, 180.14 2.89, 224.11 0 C233.84 0.82, 237.06 7.26, 239.11 15 C242.99 24.26, 241.66 29.88, 239.11 45 C236.59 55.8, 233.12 62.93, 224.11 60 C152.35 56.37, 80.23 58.67, 15 60 C3.39 56.5, 0.21 51.71, 0 45 C2.87 38.7, -0.94 26.6, 0 15 C2.49 6.26, 7.23 -3.24, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C78.1 -0.21, 139.7 0.43, 224.11 0 M15 0 C71.5 -1.48, 127.42 -0.58, 224.11 0 M224.11 0 C233.2 -0.42, 241.06 6.04, 239.11 15 M224.11 0 C233.42 -1.31, 237.74 2.86, 239.11 15 M239.11 15 C240.36 26.72, 237.64 36.9, 239.11 45 M239.11 15 C238.38 24.95, 240.11 35.46, 239.11 45 M239.11 45 C238.4 53.59, 232.59 61.31, 224.11 60 M239.11 45 C237.28 56.85, 232.48 58.73, 224.11 60 M224.11 60 C173.09 61.76, 124.09 61.93, 15 60 M224.11 60 C178.17 59.29, 132.56 59.2, 15 60 M15 60 C3.11 58.66, 1.24 55.78, 0 45 M15 60 C5.05 58.91, 0.46 55, 0 45 M0 45 C2.08 33.37, 1.9 25.15, 0 15 M0 45 C0.33 38.92, -0.25 31.65, 0 15 M0 15 C0.49 4.64, 3.36 0.82, 15 0 M0 15 C1.96 6.18, 3.79 0.8, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(139.89348609279563 134.21848451683462) rotate(0 104.51991271972656 12.5)"><text x="104.51991271972656" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Read components.json</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 216.71848451683462) rotate(0 119.5555419921875 30)"><path d="M15 0 C65.43 -4.33, 118.95 -0.45, 224.11 0 C233.42 -0.14, 236.65 3.7, 239.11 15 C239.94 20.23, 238.16 26.33, 239.11 45 C239.77 52.12, 234.11 57.89, 224.11 60 C143.76 59.77, 68.12 59.38, 15 60 C1.59 58.64, -1.63 54.26, 0 45 C2.19 39.11, -1.51 28.86, 0 15 C-3.6 3.29, 8.17 3.44, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C81.37 2.71, 149.53 1.07, 224.11 0 M15 0 C65.84 -2.01, 115.37 -0.42, 224.11 0 M224.11 0 C233.62 0.7, 239.01 6.7, 239.11 15 M224.11 0 C233.32 -1.57, 240.83 2.84, 239.11 15 M239.11 15 C237.67 23.85, 239.88 36.07, 239.11 45 M239.11 15 C239.06 20.88, 239.38 28.62, 239.11 45 M239.11 45 C240.08 55.5, 235.8 59.94, 224.11 60 M239.11 45 C239.56 53.77, 232.58 57.71, 224.11 60 M224.11 60 C146.16 62.85, 70.25 60.26, 15 60 M224.11 60 C151.54 58.67, 79.07 58.77, 15 60 M15 60 C3.83 61.59, 0.65 56.92, 0 45 M15 60 C6.48 57.86, 0.55 56.62, 0 45 M0 45 C0.1 33.91, 0.2 24.97, 0 15 M0 45 C1.02 36.06, -0.07 27.92, 0 15 M0 15 C-0.17 5.42, 4.24 -0.08, 15 0 M0 15 C1.84 7.23, 3.98 -1.21, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(168.17346961330344 234.21848451683462) rotate(0 76.23992919921875 12.5)"><text x="76.23992919921875" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Component Loop</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 316.7184845168346) rotate(0 119.5555419921875 70)"><path d="M150 17.75 C164.88 30.89, 180.99 36.16, 209.11 53.25 C238.19 72.99, 241.83 68.75, 209.11 88.75 C185.08 100.66, 161.47 112.81, 150 122.25 C120.84 140.11, 118.4 142.1, 90 122.25 C64.43 105.87, 47.62 99.2, 30 88.75 C-2.92 73.38, -3.06 69.52, 30 53.25 C54.34 38.7, 72.16 29.31, 90 17.75 C122.9 -3.14, 119.93 0.73, 150 17.75" stroke="none" stroke-width="0" fill="#fff9db"></path><path d="M150 17.75 C166.09 28.06, 184.97 38.39, 209.11 53.25 M150 17.75 C169.17 29.31, 187.64 41.42, 209.11 53.25 M209.11 53.25 C239.21 71.06, 239.08 70.01, 209.11 88.75 M209.11 53.25 C240.12 69.56, 240.89 72.24, 209.11 88.75 M209.11 88.75 C190.45 97.38, 169.42 109.92, 150 122.25 M209.11 88.75 C187.62 101.16, 167.39 113.01, 150 122.25 M150 122.25 C119.99 140.38, 119.5 140.98, 90 122.25 M150 122.25 C120.8 140.03, 121.51 140.95, 90 122.25 M90 122.25 C77.36 116.62, 65.24 106.55, 30 88.75 M90 122.25 C74.49 113.47, 56.6 103.33, 30 88.75 M30 88.75 C-0.38 70.12, -0.99 69.61, 30 53.25 M30 88.75 C1.13 71.9, -2.18 70.6, 30 53.25 M30 53.25 C47.61 42.83, 62.07 32.49, 90 17.75 M30 53.25 C43.79 45.51, 57.45 36.98, 90 17.75 M90 17.75 C120.74 0.14, 118.76 -0.46, 150 17.75 M90 17.75 C120.51 -0.57, 118.86 -0.06, 150 17.75" stroke="#e6961e" stroke-width="1" fill="none"></path></g><g transform="translate(189.73966224025656 366.7184845168346) rotate(0 54.895965576171875 20)"><text x="54.895965576171875" y="14.096" font-family="Virgil, Segoe UI Emoji" font-size="16px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Match</text><text x="54.895965576171875" y="34.096000000000004" font-family="Virgil, Segoe UI Emoji" font-size="16px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">component_id?</text></g><g stroke-linecap="round" transform="translate(124.85785682033469 516.7184845168347) rotate(0 119.5555419921875 30)"><path d="M15 0 C85.51 0.55, 155.71 -0.17, 224.11 0 C232.04 -3.06, 241.2 8.28, 239.11 15 C235.98 21.58, 238.58 28.39, 239.11 45 C236 53.36, 230.8 57.21, 224.11 60 C141.25 62.82, 60.08 63.47, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#a5d8ff"></path><path d="M15 0 C74 2.61, 131.87 2.4, 224.11 0 M15 0 C67.8 -1.62, 119.73 -1.97, 224.11 0 M224.11 0 C235.7 -0.51, 241.05 4.95, 239.11 15 M224.11 0 C233.23 -0.06, 238.81 3.87, 239.11 15 M239.11 15 C240.15 21.29, 240.51 28.47, 239.11 45 M239.11 15 C240.04 24.55, 239.61 33.49, 239.11 45 M239.11 45 C238.85 56.4, 232.54 60.76, 224.11 60 M239.11 45 C240.16 57.23, 232.46 60.95, 224.11 60 M224.11 60 C162.58 59.59, 101.65 57.88, 15 60 M224.11 60 C155.83 61.64, 88.74 61.7, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#1971c2" stroke-width="1" fill="none"></path></g><g transform="translate(174.91346747707297 534.2184845168347) rotate(0 69.49993133544922 12.5)"><text x="69.49993133544922" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Build complete</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 64.27408754417836) rotate(0 131.77777099609375 30.000000000000007)"><path d="M15 0 C108.44 -2.34, 199.67 2.8, 248.56 0 C258.28 0.82, 261.51 7.26, 263.56 15 C267.43 24.26, 266.11 29.88, 263.56 45 C261.03 55.8, 257.56 62.93, 248.56 60 C168.45 56.47, 88 58.66, 15 60 C3.39 56.5, 0.21 51.71, 0 45 C2.87 38.7, -0.94 26.6, 0 15 C2.49 6.26, 7.23 -3.24, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C85.28 -0.32, 154.14 0.3, 248.56 0 M15 0 C78.07 -1.56, 140.6 -0.71, 248.56 0 M248.56 0 C257.65 -0.42, 265.5 6.04, 263.56 15 M248.56 0 C257.87 -1.31, 262.18 2.86, 263.56 15 M263.56 15 C264.81 26.72, 262.08 36.9, 263.56 45 M263.56 15 C262.83 24.95, 264.56 35.46, 263.56 45 M263.56 45 C262.84 53.59, 257.04 61.31, 248.56 60 M263.56 45 C261.72 56.85, 256.92 58.73, 248.56 60 M248.56 60 C191.61 61.79, 136.59 61.96, 15 60 M248.56 60 C197.27 59.16, 146.3 59.07, 15 60 M15 60 C3.11 58.66, 1.24 55.78, 0 45 M15 60 C5.05 58.91, 0.46 55, 0 45 M0 45 C2.08 33.37, 1.9 25.15, 0 15 M0 45 C0.33 38.92, -0.25 31.65, 0 15 M0 15 C0.49 4.64, 3.36 0.82, 15 0 M0 15 C1.96 6.18, 3.79 0.8, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(610.1972487024138 81.77408754417836) rotate(0 81.33992004394531 12.500000000000007)"><text x="81.33992004394531" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Start processing</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 171.16297304222525) rotate(0 131.77777099609375 35)"><path d="M165 9 C178.55 9.69, 195.51 18.67, 230.56 27 C262.86 35.86, 261.09 34.7, 230.56 45 C217.95 48.04, 202.69 51.26, 165 61 C132.66 67.12, 132 67.89, 99 61 C71.81 53.89, 50.02 47.46, 33 45 C-3.41 34.64, -1.63 35.26, 33 27 C49.49 24.09, 60.06 16.44, 99 9 C128.4 -1.71, 135.17 3.44, 165 9" stroke="none" stroke-width="0" fill="#fff9db"></path><path d="M165 9 C184.66 17.09, 206.22 21.08, 230.56 27 M165 9 C181.3 12.04, 196.28 18.16, 230.56 27 M230.56 27 C263.06 36.7, 263.45 37.7, 230.56 45 M230.56 27 C262.77 34.43, 265.27 33.84, 230.56 45 M230.56 45 C207.96 49.11, 189 56.81, 165 61 M230.56 45 C216.3 48.17, 202.3 52.86, 165 61 M165 61 C132.97 70.5, 133.69 69.94, 99 61 M165 61 C132.45 68.77, 130.46 67.71, 99 61 M99 61 C73.14 57.52, 49.66 48.73, 33 45 M99 61 C76.45 55.22, 53.88 49.75, 33 45 M33 45 C-1.17 37.59, 0.65 37.92, 33 27 M33 45 C1.48 33.86, 0.55 37.62, 33 27 M33 27 C53.22 19.88, 73.56 14.62, 99 9 M33 27 C51.63 21.57, 68.25 16.65, 99 9 M99 9 C131.83 0.42, 131.24 -0.08, 165 9 M99 9 C133.84 2.23, 130.98 -1.21, 165 9" stroke="#e6961e" stroke-width="1" fill="none"></path></g><g transform="translate(638.6883299402068 193.66297304222525) rotate(0 52.95995330810547 12.5)"><text x="52.95995330810547" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Edit mode?</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 758.051828022694) rotate(0 131.77777099609375 30)"><path d="M15 0 C71.79 -4.28, 131.54 -0.57, 248.56 0 C257.86 -0.14, 261.09 3.7, 263.56 15 C264.38 20.23, 262.6 26.33, 263.56 45 C264.21 52.12, 258.56 57.89, 248.56 60 C159.17 59.91, 74.27 59.54, 15 60 C1.59 58.64, -1.63 54.26, 0 45 C2.19 39.11, -1.51 28.86, 0 15 C-3.6 3.29, 8.17 3.44, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C89.38 2.7, 165.48 1.14, 248.56 0 M15 0 C71.68 -2.06, 127.12 -0.55, 248.56 0 M248.56 0 C258.06 0.7, 263.45 6.7, 263.56 15 M248.56 0 C257.77 -1.57, 265.27 2.84, 263.56 15 M263.56 15 C262.12 23.85, 264.32 36.07, 263.56 45 M263.56 15 C263.5 20.88, 263.83 28.62, 263.56 45 M263.56 45 C264.53 55.5, 260.24 59.94, 248.56 60 M263.56 45 C264.01 53.77, 257.02 57.71, 248.56 60 M248.56 60 C161.73 62.85, 76.85 60.37, 15 60 M248.56 60 C167.46 58.55, 86.45 58.64, 15 60 M15 60 C3.83 61.59, 0.65 56.92, 0 45 M15 60 C6.48 57.86, 0.55 56.62, 0 45 M0 45 C0.1 33.91, 0.2 24.97, 0 15 M0 45 C1.02 36.06, -0.07 27.92, 0 15 M0 15 C-0.17 5.42, 4.24 -0.08, 15 0 M0 15 C1.84 7.23, 3.98 -1.21, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(570.7172529748748 775.551828022694) rotate(0 120.81991577148438 12.5)"><text x="120.81991577148438" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Generate code with LLM</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 858.64773530204) rotate(0 131.77777099609375 30)"><path d="M15 0 C80.96 1.7, 147.75 -2.53, 248.56 0 C257.63 1.99, 266.28 2.75, 263.56 15 C261.71 25.01, 260.24 35.85, 263.56 45 C264.39 55.11, 256.96 62.1, 248.56 60 C158.37 55.31, 75.21 60.34, 15 60 C2.08 62.38, -3.06 53.52, 0 45 C2.89 32.7, -0.64 25.26, 0 15 C2.9 1.86, 4.93 0.73, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C80.31 1.21, 148.21 1.45, 248.56 0 M15 0 C91.21 -0.38, 166.82 0.04, 248.56 0 M248.56 0 C258.65 0.06, 263.53 4.01, 263.56 15 M248.56 0 C259.57 -1.44, 265.34 6.24, 263.56 15 M263.56 15 C264.08 22.98, 262.26 34.38, 263.56 45 M263.56 15 C263.27 26.73, 264.26 37.32, 263.56 45 M263.56 45 C263.54 55.38, 258.06 60.98, 248.56 60 M263.56 45 C264.36 55.03, 260.06 60.95, 248.56 60 M248.56 60 C198.34 61.56, 148.56 59.17, 15 60 M248.56 60 C185.95 60.25, 121.21 59.37, 15 60 M15 60 C4.62 59.12, -0.99 53.61, 0 45 M15 60 C6.13 60.9, -2.18 54.6, 0 45 M0 45 C0.73 36.66, -1.69 27.87, 0 15 M0 45 C-0.17 38.9, -0.47 31.65, 0 15 M0 15 C0.74 5.14, 3.76 -0.46, 15 0 M0 15 C0.51 4.43, 3.86 -0.06, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(601.5172560266326 876.14773530204) rotate(0 90.01991271972656 12.5)"><text x="90.01991271972656" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Write files to disk</text></g><g stroke-linecap="round" transform="translate(559.7593977502654 958.0518890578503) rotate(0 131.77777099609375 29.999999999999943)"><path d="M15 0 C93.76 0.28, 172.22 -0.4, 248.56 0 C256.48 -3.06, 265.65 8.28, 263.56 15 C260.42 21.58, 263.02 28.39, 263.56 45 C260.44 53.36, 255.24 57.21, 248.56 60 C156.17 62.77, 65.4 63.39, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#ffc9c9"></path><path d="M15 0 C80.7 2.58, 145.31 2.38, 248.56 0 M15 0 C73.87 -1.75, 131.92 -2.07, 248.56 0 M248.56 0 C260.14 -0.51, 265.5 4.95, 263.56 15 M248.56 0 C257.68 -0.06, 263.25 3.87, 263.56 15 M263.56 15 C264.59 21.29, 264.95 28.47, 263.56 45 M263.56 15 C264.49 24.55, 264.05 33.49, 263.56 45 M263.56 45 C263.3 56.4, 256.99 60.76, 248.56 60 M263.56 45 C264.61 57.23, 256.9 60.95, 248.56 60 M248.56 60 C179.83 59.43, 111.68 57.8, 15 60 M248.56 60 C172.32 61.76, 97.23 61.81, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#e03131" stroke-width="1" fill="none"></path></g><g transform="translate(590.0172712854217 975.5518890578503) rotate(0 101.5198974609375 12.5)"><text x="101.5198974609375" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Component processed</text></g><g mask="url(#mask-match-to-complete)" stroke-linecap="round"><g transform="translate(244.4694547689763 453.2768674853473) rotate(0 0.026610624536800742 31.596287982697845)"><path d="M0.16 1 C0.24 11.73, 0.15 53.47, 0.2 63.77 M-1.21 0.47 C-1.26 10.91, -0.86 51.37, -0.67 61.95" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(244.4694547689763 453.2768674853473) rotate(0 0.026610624536800742 31.596287982697845)"><path d="M-9.53 38.58 C-5.51 45.35, -3.73 52.34, -0.67 61.95 M-9.53 38.58 C-6.76 44.68, -5.31 51.89, -0.67 61.95" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(244.4694547689763 453.2768674853473) rotate(0 0.026610624536800742 31.596287982697845)"><path d="M7.57 38.35 C6.81 45.21, 3.81 52.26, -0.67 61.95 M7.57 38.35 C5.74 44.51, 2.57 51.78, -0.67 61.95" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-match-to-complete"><rect x="0" y="0" fill="#fff" width="344.5226760180499" height="616.469443450743"></rect><rect x="206.306093469685" y="472.37315546804507" fill="#000" width="76.37994384765625" height="25" opacity="1"></rect></mask><g transform="translate(206.30609346968498 472.37315546804507) rotate(0 37.65874408399293 13.02644847230053)"><text x="38.189971923828125" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">All done</text></g><g stroke-opacity="0.4" fill-opacity="0.4" stroke-linecap="round" transform="translate(451.5371687463591 291.38517152855337) rotate(0 240 207.33334350585938)"><path d="M32 0 C151.41 0.61, 271.35 -2.1, 448 0 C468.41 1.99, 482.72 8.42, 480 32 C475.97 162.53, 475.01 293.59, 480 382.67 C480.84 404.11, 467.73 416.76, 448 414.67 C289.78 410.64, 136.06 413.85, 32 414.67 C7.75 417.05, -3.06 402.52, 0 382.67 C5.17 256.8, 2.88 134.08, 0 32 C2.9 7.53, 10.6 0.73, 32 0" stroke="none" stroke-width="0" fill="#f5f5f5"></path><path d="M32 0 C149.21 1.44, 268.08 1.59, 448 0 M32 0 C167.88 -0.48, 303.37 -0.21, 448 0 M448 0 C469.43 0.06, 479.97 9.67, 480 32 M448 0 C470.35 -1.44, 481.78 11.9, 480 32 M480 32 C481.97 144.8, 480.79 259.82, 480 382.67 M480 32 C480.01 158.48, 480.65 284.22, 480 382.67 M480 382.67 C479.99 404.38, 468.84 415.65, 448 414.67 M480 382.67 C480.8 404.03, 470.84 415.61, 448 414.67 M448 414.67 C358.23 415.8, 268.73 414.27, 32 414.67 M448 414.67 C335.61 414.82, 221.86 414.26, 32 414.67 M32 414.67 C10.29 413.79, -0.99 402.61, 0 382.67 M32 414.67 C11.8 415.57, -2.18 403.6, 0 382.67 M0 382.67 C0.34 284.07, -1.24 185.18, 0 32 M0 382.67 C0.09 301.65, -0.11 219.89, 0 32 M0 32 C0.74 10.81, 9.42 -0.46, 32 0 M0 32 C0.51 10.1, 9.53 -0.06, 32 0" stroke="#999999" stroke-width="1" fill="none"></path></g><g transform="translate(599.6254772544148 296.38517152855337) rotate(0 95.47991943359375 12.5)"><text x="95.47991943359375" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Resource Gathering</text></g><g stroke-linecap="round" transform="translate(467.9816267541716 347.16297304222525) rotate(0 100.22222900390625 25)"><path d="M12.5 0 C61.32 2.3, 111.13 -2.71, 187.94 0 C195.35 1.99, 203.17 1.92, 200.44 12.5 C198.66 20.64, 197.19 29.61, 200.44 37.5 C201.28 45.94, 194.68 52.1, 187.94 50 C119.27 45.05, 58.93 51.01, 12.5 50 C1.25 52.38, -3.06 44.36, 0 37.5 C2.81 26.98, -0.72 21.32, 0 12.5 C2.9 1.03, 4.1 0.73, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C61.23 1.05, 113.02 1.33, 187.94 0 M12.5 0 C69.69 -0.32, 126.19 0.19, 187.94 0 M187.94 0 C196.37 0.06, 200.41 3.17, 200.44 12.5 M187.94 0 C197.29 -1.44, 202.23 5.4, 200.44 12.5 M200.44 12.5 C200.93 18.85, 199.11 28.63, 200.44 37.5 M200.44 12.5 C200.16 22.44, 201.14 31.24, 200.44 37.5 M200.44 37.5 C200.43 46.21, 195.78 50.98, 187.94 50 M200.44 37.5 C201.25 45.87, 197.79 50.95, 187.94 50 M187.94 50 C150.35 51.77, 113.26 48.94, 12.5 50 M187.94 50 C141.25 50.3, 92.03 49.26, 12.5 50 M12.5 50 C3.79 49.12, -0.99 44.44, 0 37.5 M12.5 50 C5.3 50.9, -2.18 45.43, 0 37.5 M0 37.5 C0.73 30.57, -1.69 23.18, 0 12.5 M0 37.5 C-0.18 32.57, -0.48 26.48, 0 12.5 M0 12.5 C0.74 4.31, 2.92 -0.46, 12.5 0 M0 12.5 C0.51 3.6, 3.03 -0.06, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(479.2121624350788 359.66297304222525) rotate(0 92.55992126464844 12.5)"><text x="92.55992126464844" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Read existing code</text></g><g stroke-linecap="round" transform="translate(721.7593367151092 341.3852020461315) rotate(0 84.888916015625 30)"><path d="M15 0 C62.12 1.44, 108.88 0.63, 154.78 0 C162.71 -3.06, 171.87 8.28, 169.78 15 C166.65 21.58, 169.24 28.39, 169.78 45 C166.66 53.36, 161.47 57.21, 154.78 60 C98.93 62.92, 44.99 63.65, 15 60 C3.43 60.83, 0.44 54.28, 0 45 C-0.49 37.61, 0.67 34.68, 0 15 C-3.5 8.36, 2.14 -2.42, 15 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M15 0 C55.01 2.63, 93.74 2.39, 154.78 0 M15 0 C50.57 -1.17, 85.17 -1.56, 154.78 0 M154.78 0 C166.37 -0.51, 171.72 4.95, 169.78 15 M154.78 0 C163.9 -0.06, 169.47 3.87, 169.78 15 M169.78 15 C170.81 21.29, 171.17 28.47, 169.78 45 M169.78 15 C170.71 24.55, 170.27 33.49, 169.78 45 M169.78 45 C169.52 56.4, 163.21 60.76, 154.78 60 M169.78 45 C170.83 57.23, 163.12 60.95, 154.78 60 M154.78 60 C113.65 60.15, 73.2 58.22, 15 60 M154.78 60 C109.04 61.22, 64.66 61.28, 15 60 M15 60 C5.81 61, -1.07 55.49, 0 45 M15 60 C5.93 57.85, -1 56.13, 0 45 M0 45 C1.64 37.59, -1.79 33.22, 0 15 M0 45 C-1.25 37.63, 0.4 32.29, 0 15 M0 15 C1.31 5.08, 5.58 0.05, 15 0 M0 15 C0.88 6.67, 2.72 -0.72, 15 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(739.3965496421101 346.3852020461315) rotate(0 70.81993103027344 25)"><text x="70.81993103027344" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Begin resource</text><text x="70.81993103027344" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">gathering</text></g><g stroke-linecap="round" transform="translate(592.2037947229217 449.3852020461315) rotate(0 100 25)"><path d="M12.5 0 C82.7 -2.89, 150.28 3.2, 187.5 0 C195.56 0.82, 197.95 6.42, 200 12.5 C203.79 20.75, 202.46 25.37, 200 37.5 C197.48 46.64, 194.84 52.93, 187.5 50 C127.37 46.01, 66.82 48.61, 12.5 50 C2.55 46.5, 0.21 42.54, 0 37.5 C2.9 32.62, -0.92 21.96, 0 12.5 C2.49 5.43, 6.39 -3.24, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C65.65 -0.05, 117.1 0.67, 187.5 0 M12.5 0 C59.84 -1.43, 106.53 -0.41, 187.5 0 M187.5 0 C194.93 -0.42, 201.95 5.21, 200 12.5 M187.5 0 C195.14 -1.31, 198.62 2.03, 200 12.5 M200 12.5 C201.21 22.4, 198.49 30.76, 200 37.5 M200 12.5 C199.26 20.7, 200.99 29.45, 200 37.5 M200 37.5 C199.29 44.43, 194.32 51.31, 187.5 50 M200 37.5 C198.17 47.69, 194.2 48.73, 187.5 50 M187.5 50 C144.74 51.8, 104.26 52, 12.5 50 M187.5 50 C149 49.46, 110.87 49.36, 12.5 50 M12.5 50 C2.27 48.66, 1.24 46.61, 0 37.5 M12.5 50 C4.22 48.91, 0.46 45.83, 0 37.5 M0 37.5 C2.05 27.64, 1.86 21.18, 0 12.5 M0 37.5 C0.32 32.56, -0.25 26.43, 0 12.5 M0 12.5 C0.49 3.8, 2.52 0.82, 12.5 0 M0 12.5 C1.96 5.35, 2.95 0.8, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(605.7720226645711 449.3852020461315) rotate(0 90 25)"><text x="90" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Read component </text><text x="90" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">resources</text></g><g stroke-linecap="round" transform="translate(477.31493974245285 540.4962860305066) rotate(0 80 25)"><path d="M12.5 0 C43.65 -4.38, 78.31 0.01, 147.5 0 C155.14 -0.14, 157.54 2.87, 160 12.5 C160.85 16.7, 159.07 21.77, 160 37.5 C160.66 42.95, 155.83 47.89, 147.5 50 C94.58 49.29, 46.99 48.85, 12.5 50 C0.76 48.64, -1.63 45.09, 0 37.5 C2.2 32.69, -1.5 23.52, 0 12.5 C-3.6 2.46, 7.33 3.44, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C54.58 2.64, 98.7 0.78, 147.5 0 M12.5 0 C45.63 -1.76, 77.28 0.03, 147.5 0 M147.5 0 C155.34 0.7, 159.9 5.86, 160 12.5 M147.5 0 C155.04 -1.57, 161.72 2.01, 160 12.5 M160 12.5 C158.57 19.74, 160.77 30.34, 160 37.5 M160 12.5 C159.99 17.29, 160.32 23.94, 160 37.5 M160 37.5 C160.97 46.33, 157.52 49.94, 147.5 50 M160 37.5 C160.45 44.6, 154.3 47.71, 147.5 50 M147.5 50 C96.47 52.79, 47.75 49.85, 12.5 50 M147.5 50 C100.78 49.17, 54.17 49.28, 12.5 50 M12.5 50 C3 51.59, 0.65 47.75, 0 37.5 M12.5 50 C5.65 47.86, 0.55 47.46, 0 37.5 M0 37.5 C0.06 27.94, 0.15 20.54, 0 12.5 M0 37.5 C0.98 29.9, -0.1 23.1, 0 12.5 M0 12.5 C-0.17 4.59, 3.41 -0.08, 12.5 0 M0 12.5 C1.84 6.4, 3.15 -1.21, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(491.88316768410226 540.4962860305066) rotate(0 69 25)"><text x="69" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Component </text><text x="69" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">spec &amp; docs</text></g><g stroke-linecap="round" transform="translate(741.5371687463592 539.1629730422253) rotate(0 80 25)"><path d="M12.5 0 C49.61 2.49, 87.7 -2.52, 147.5 0 C154.91 1.99, 162.72 1.92, 160 12.5 C158.22 20.64, 156.75 29.61, 160 37.5 C160.84 45.94, 154.23 52.1, 147.5 50 C94.08 45.47, 48.99 51.43, 12.5 50 C1.25 52.38, -3.06 44.36, 0 37.5 C2.81 26.98, -0.72 21.32, 0 12.5 C2.9 1.03, 4.1 0.73, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C49.78 0.78, 90.13 1.06, 147.5 0 M12.5 0 C56.48 -0.22, 99.75 0.29, 147.5 0 M147.5 0 C155.93 0.06, 159.97 3.17, 160 12.5 M147.5 0 C156.85 -1.44, 161.78 5.4, 160 12.5 M160 12.5 C160.48 18.85, 158.66 28.63, 160 37.5 M160 12.5 C159.71 22.44, 160.7 31.24, 160 37.5 M160 37.5 C159.99 46.21, 155.34 50.98, 147.5 50 M160 37.5 C160.8 45.87, 157.34 50.95, 147.5 50 M147.5 50 C118.65 51.72, 90.31 48.89, 12.5 50 M147.5 50 C111.78 50.3, 73.54 49.26, 12.5 50 M12.5 50 C3.79 49.12, -0.99 44.44, 0 37.5 M12.5 50 C5.3 50.9, -2.18 45.43, 0 37.5 M0 37.5 C0.73 30.57, -1.69 23.18, 0 12.5 M0 37.5 C-0.18 32.57, -0.48 26.48, 0 12.5 M0 12.5 C0.74 4.31, 2.92 -0.46, 12.5 0 M0 12.5 C0.51 3.6, 3.03 -0.06, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(750.1053966880086 539.1629730422253) rotate(0 75 25)"><text x="75" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Dependency </text><text x="75" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">specs</text></g><g stroke-linecap="round" transform="translate(477.31493974245285 638.940744038319) rotate(0 80 25)"><path d="M12.5 0 C58 1.5, 103.16 0.69, 147.5 0 C153.76 -3.06, 162.09 7.45, 160 12.5 C156.81 18, 159.41 23.73, 160 37.5 C156.88 44.19, 152.52 47.21, 147.5 50 C93.52 52.9, 41.45 53.63, 12.5 50 C2.6 50.83, 0.44 45.11, 0 37.5 C-0.48 31.15, 0.68 29.28, 0 12.5 C-3.5 7.52, 1.3 -2.42, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C51.19 2.61, 88.6 2.37, 147.5 0 M12.5 0 C46.88 -1.13, 80.28 -1.52, 147.5 0 M147.5 0 C157.42 -0.51, 161.94 4.12, 160 12.5 M147.5 0 C154.95 -0.06, 159.7 3.04, 160 12.5 M160 12.5 C161.02 17.72, 161.38 23.83, 160 37.5 M160 12.5 C160.93 20.46, 160.49 27.82, 160 37.5 M160 37.5 C159.74 47.24, 154.26 50.76, 147.5 50 M160 37.5 C161.05 48.06, 154.18 50.95, 147.5 50 M147.5 50 C107.78 50.2, 68.74 48.27, 12.5 50 M147.5 50 C103.32 51.18, 60.49 51.24, 12.5 50 M12.5 50 C4.97 51, -1.07 46.32, 0 37.5 M12.5 50 C5.1 47.85, -1 46.96, 0 37.5 M0 37.5 C1.61 31.15, -1.82 27.85, 0 12.5 M0 37.5 C-1.2 31.21, 0.45 26.94, 0 12.5 M0 12.5 C1.31 4.25, 4.75 0.05, 12.5 0 M0 12.5 C0.88 5.84, 1.88 -0.72, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(491.88316768410226 638.940744038319) rotate(0 69 25)"><text x="69" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Reference </text><text x="69" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">documentation</text></g><g stroke-linecap="round" transform="translate(741.5371687463592 638.4962860305066) rotate(0 80 25)"><path d="M12.5 0 C66.77 -2.97, 118.42 3.11, 147.5 0 C155.56 0.82, 157.95 6.42, 160 12.5 C163.79 20.75, 162.46 25.37, 160 37.5 C157.48 46.64, 154.84 52.93, 147.5 50 C101.04 46.14, 54.17 48.74, 12.5 50 C2.55 46.5, 0.21 42.54, 0 37.5 C2.9 32.62, -0.92 21.96, 0 12.5 C2.49 5.43, 6.39 -3.24, 12.5 0" stroke="none" stroke-width="0" fill="#b2f2bb"></path><path d="M12.5 0 C53.8 0.16, 93.4 0.89, 147.5 0 M12.5 0 C49.07 -1.14, 84.98 -0.12, 147.5 0 M147.5 0 C154.93 -0.42, 161.95 5.21, 160 12.5 M147.5 0 C155.14 -1.31, 158.62 2.03, 160 12.5 M160 12.5 C161.21 22.4, 158.49 30.76, 160 37.5 M160 12.5 C159.26 20.7, 160.99 29.45, 160 37.5 M160 37.5 C159.29 44.43, 154.32 51.31, 147.5 50 M160 37.5 C158.17 47.69, 154.2 48.73, 147.5 50 M147.5 50 C114.46 51.58, 83.7 51.78, 12.5 50 M147.5 50 C117.75 49.77, 88.38 49.66, 12.5 50 M12.5 50 C2.27 48.66, 1.24 46.61, 0 37.5 M12.5 50 C4.22 48.91, 0.46 45.83, 0 37.5 M0 37.5 C2.05 27.64, 1.86 21.18, 0 12.5 M0 37.5 C0.32 32.56, -0.25 26.43, 0 12.5 M0 12.5 C0.49 3.8, 2.52 0.82, 12.5 0 M0 12.5 C1.96 5.35, 2.95 0.8, 12.5 0" stroke="#2b8a3e" stroke-width="1" fill="none"></path></g><g transform="translate(750.1053966880086 638.4962860305066) rotate(0 75 25)"><text x="75" y="17.619999999999997" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Implementation </text><text x="75" y="42.62" font-family="Virgil, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">guidance</text></g><g stroke-linecap="round"><g transform="translate(577.297205795076 537.079351806472) rotate(0 23.652024911843625 -18.301718806925294)"><path d="M-0.28 0.48 C7.7 -5.76, 39.46 -30.75, 47.47 -36.92 M0.58 0.25 C8.54 -5.69, 39.28 -30.36, 47.12 -36.38" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(577.297205795076 537.079351806472) rotate(0 23.652024911843625 -18.301718806925294)"><path d="M33.94 -15.14 C37.64 -19.52, 39.13 -23.71, 47.12 -36.38 M33.94 -15.14 C37.93 -21.52, 42.54 -28.91, 47.12 -36.38" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(577.297205795076 537.079351806472) rotate(0 23.652024911843625 -18.301718806925294)"><path d="M23.37 -28.58 C29.48 -29.95, 33.31 -31.16, 47.12 -36.38 M23.37 -28.58 C30.67 -30.78, 38.61 -33.95, 47.12 -36.38" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(631.3282089412908 635.8815403511139) rotate(0 20.26941245941947 -66.5208193198423)"><path d="M-0.69 1.11 C6.05 -20.9, 34.41 -110.83, 41.1 -133.18 M1.15 0.65 C7.72 -21.08, 33.67 -109.67, 40.45 -131.72" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(631.3282089412908 635.8815403511139) rotate(0 20.26941245941947 -66.5208193198423)"><path d="M41.91 -106.76 C43.47 -114.72, 40.86 -126.33, 40.45 -131.72 M41.91 -106.76 C41.9 -114.11, 41.38 -122.22, 40.45 -131.72" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(631.3282089412908 635.8815403511139) rotate(0 20.26941245941947 -66.5208193198423)"><path d="M25.52 -111.66 C32.88 -117.78, 36.11 -127.65, 40.45 -131.72 M25.52 -111.66 C30.47 -117.48, 34.92 -124.09, 40.45 -131.72" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(788.8566886923084 535.5616830183576) rotate(0 -16.92041280379169 -16.757885960170768)"><path d="M0.49 0.35 C-5.32 -5.31, -28.6 -28.09, -34.39 -33.77 M0.09 0.05 C-5.62 -5.56, -27.9 -27.65, -33.44 -33.2" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.8566886923084 535.5616830183576) rotate(0 -16.92041280379169 -16.757885960170768)"><path d="M-11.83 -23.18 C-19.73 -28.03, -29.33 -31.75, -33.44 -33.2 M-11.83 -23.18 C-17.8 -25.89, -22.77 -28.52, -33.44 -33.2" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.8566886923084 535.5616830183576) rotate(0 -16.92041280379169 -16.757885960170768)"><path d="M-23.33 -11.64 C-26.72 -21.08, -31.79 -29.35, -33.44 -33.2 M-23.33 -11.64 C-26.29 -17.37, -28.27 -23.01, -33.44 -33.2" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(747.6382411037614 634.3061006956566) rotate(0 -22.07488969747118 -65.31367786961357)"><path d="M-0.74 0.56 C-8.1 -21.04, -36.36 -108.31, -43.71 -130.01 M1.07 -0.19 C-6.45 -22.1, -36.59 -109.93, -44.43 -131.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(747.6382411037614 634.3061006956566) rotate(0 -22.07488969747118 -65.31367786961357)"><path d="M-28.61 -112.45 C-32.95 -118.36, -38.2 -126.78, -44.43 -131.8 M-28.61 -112.45 C-33.99 -119.38, -40.66 -126.5, -44.43 -131.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(747.6382411037614 634.3061006956566) rotate(0 -22.07488969747118 -65.31367786961357)"><path d="M-44.75 -106.81 C-43.62 -114.52, -43.41 -124.85, -44.43 -131.8 M-44.75 -106.81 C-43.95 -116.03, -44.41 -125.31, -44.43 -131.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(672.5452318554102 369.40700007883356) rotate(0 22.047413104457576 0.2549443526448272)"><path d="M0.18 -0.12 C7.48 -0.15, 36.57 0.23, 43.94 0.25 M-0.39 -0.66 C6.82 -0.65, 36 0.65, 43.44 0.82" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(672.5452318554102 369.40700007883356) rotate(0 22.047413104457576 0.2549443526448272)"><path d="M22.47 7.64 C28.98 5.13, 35.48 3.78, 43.44 0.82 M22.47 7.64 C26.38 6.22, 31.74 4.72, 43.44 0.82" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(672.5452318554102 369.40700007883356) rotate(0 22.047413104457576 0.2549443526448272)"><path d="M22.99 -7.43 C29.39 -5.08, 35.73 -1.58, 43.44 0.82 M22.99 -7.43 C26.78 -5.7, 32.03 -4.04, 43.44 0.82" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(766.9142380058499 407.3858220720863) rotate(0 -13.870632202009574 18.024011650442986)"><path d="M0.43 -0.11 C-4.2 5.83, -23.16 30.08, -27.93 36.18 M-0.02 -0.64 C-4.71 5.36, -23.94 29.23, -28.45 35.28" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(766.9142380058499 407.3858220720863) rotate(0 -13.870632202009574 18.024011650442986)"><path d="M-21.44 13.64 C-23.41 19.12, -24.86 24.43, -28.45 35.28 M-21.44 13.64 C-23.96 21.62, -26.69 30.23, -28.45 35.28" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(766.9142380058499 407.3858220720863) rotate(0 -13.870632202009574 18.024011650442986)"><path d="M-9.18 23.21 C-14.47 26.18, -19.2 28.93, -28.45 35.28 M-9.18 23.21 C-16.37 27.61, -23.74 32.61, -28.45 35.28" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g mask="url(#mask-Lm5YCicKEwjG6SrJlxhgr)" stroke-linecap="round"><g transform="translate(587.1830799322145 226.11675585789465) rotate(0 -42.36044623557689 55.29579976093365)"><path d="M0.04 0.3 C-9.28 5.91, -41.91 15.4, -56.22 33.71 C-70.52 52.01, -81.19 97.27, -85.81 110.15 M-1.39 -0.59 C-10.32 4.64, -40.26 13.12, -53.94 31.75 C-67.62 50.39, -78.6 97.81, -83.49 111.24" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(587.1830799322145 226.11675585789465) rotate(0 -42.36044623557689 55.29579976093365)"><path d="M-84.83 86.28 C-83.95 91.84, -83.53 98.36, -83.49 111.24 M-84.83 86.28 C-83.57 93.64, -83.68 99.71, -83.49 111.24" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(587.1830799322145 226.11675585789465) rotate(0 -42.36044623557689 55.29579976093365)"><path d="M-68.47 91.25 C-72.14 95.43, -76.28 100.57, -83.49 111.24 M-68.47 91.25 C-71.55 97.36, -75.97 102.12, -83.49 111.24" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-Lm5YCicKEwjG6SrJlxhgr"><rect x="0" y="0" fill="#fff" width="771.9039724033682" height="436.70835537976194"></rect><rect x="515.9622540642613" y="246.99629244131904" fill="#000" width="31.679977416992188" height="25" opacity="1"></rect></mask><g transform="translate(515.9622540642614 246.99629244131904) rotate(0 28.336784333177008 34.44745596144611)"><text x="15.839988708496094" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Yes</text></g><g mask="url(#mask-TKV39LSOmiDZlottftzrO)" stroke-linecap="round"><g transform="translate(788.5733046914756 226.18004089530467) rotate(0 37.655052066574456 54.28671802577762)"><path d="M-0.64 -0.02 C7.63 6.78, 36.86 23.6, 49.6 41.58 C62.34 59.56, 71.53 96.69, 75.81 107.86 M1.23 -1.07 C9.31 5.8, 36.15 24.48, 48.49 42.79 C60.84 61.1, 70.8 97.64, 75.3 108.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.5733046914756 226.18004089530467) rotate(0 37.655052066574456 54.28671802577762)"><path d="M59.54 89.4 C64.35 94.79, 68.05 101.91, 75.3 108.8 M59.54 89.4 C62.97 94.5, 67.33 98.83, 75.3 108.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(788.5733046914756 226.18004089530467) rotate(0 37.655052066574456 54.28671802577762)"><path d="M75.7 83.81 C75.72 90.78, 74.59 99.58, 75.3 108.8 M75.7 83.81 C75.24 90.26, 75.71 95.94, 75.3 108.8" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-TKV39LSOmiDZlottftzrO"><rect x="0" y="0" fill="#fff" width="963.8834088246246" height="434.7534769468599"></rect><rect x="826.1488690544957" y="255.88517793936592" fill="#000" width="24.639999389648438" height="25" opacity="1"></rect></mask><g transform="translate(826.1488690544958 255.88517793936592) rotate(0 0.007685476727885998 24.16045343027622)"><text x="12.319999694824219" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">No</text></g><g stroke-linecap="round"><g transform="translate(689.4917365157881 126.52376499919362) rotate(0 1.7958314367958224 20.70321010189069)"><path d="M0.38 0.36 C0.89 7.36, 2.64 34.72, 3.16 41.62 M-0.08 0.06 C0.59 6.94, 3.64 33.97, 4.17 40.76" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(689.4917365157881 126.52376499919362) rotate(0 1.7958314367958224 20.70321010189069)"><path d="M-4.81 22.02 C-1.36 27.19, 1.24 33.82, 4.17 40.76 M-4.81 22.02 C-1.87 28.32, 1.42 35.38, 4.17 40.76" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(689.4917365157881 126.52376499919362) rotate(0 1.7958314367958224 20.70321010189069)"><path d="M9.34 20.63 C8.26 26.3, 6.34 33.36, 4.17 40.76 M9.34 20.63 C7.24 27.46, 5.51 35.01, 4.17 40.76" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g mask="url(#mask-ySSobv5QuYECoDtsy9PpX)" stroke-linecap="round"><g transform="translate(353.93296717084837 372.4962860305065) rotate(0 96.56316766324503 -147.86497758961605)"><path d="M0.18 0.14 C7.05 -9, 28.23 -8.9, 40.78 -55.49 C53.34 -102.08, 50.02 -242.15, 75.5 -279.4 C100.97 -316.66, 173.99 -279.05, 193.63 -279.02 M-1.18 -0.84 C5.63 -9.79, 27.03 -8.19, 40.2 -54.44 C53.37 -100.69, 52.16 -241.06, 77.85 -278.32 C103.53 -315.59, 175.26 -277.93, 194.31 -278.04" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(353.93296717084837 372.4962860305065) rotate(0 96.56316766324503 -147.86497758961605)"><path d="M169.46 -275.34 C176.25 -274.94, 181.01 -278.53, 194.31 -278.04 M169.46 -275.34 C176.39 -276.34, 183.14 -277.39, 194.31 -278.04" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(353.93296717084837 372.4962860305065) rotate(0 96.56316766324503 -147.86497758961605)"><path d="M173.54 -291.95 C179.16 -287.17, 182.84 -286.38, 194.31 -278.04 M173.54 -291.95 C179.52 -288.6, 185.2 -285.3, 194.31 -278.04" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask id="mask-ySSobv5QuYECoDtsy9PpX"><rect x="0" y="0" fill="#fff" width="646.7386537191085" height="751.4406552406429"></rect><rect x="391.46548362806755" y="188.16323247143862" fill="#000" width="31.679977416992188" height="25" opacity="1"></rect></mask><g transform="translate(391.4654836280676 188.16323247143856) rotate(0 59.03065120602585 36.46807596945186)"><text x="15.839988708496094" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Yes</text></g><g mask="url(#mask-WM7UQjc4eu62cZzmhf5n0)" stroke-linecap="round"><g transform="translate(142.3507372175026 363.6073700148815) rotate(0 -10.829789214560108 -40.10570548388969)"><path d="M-0.76 -0.28 C-4.19 -5.44, -19.04 -16.42, -21.32 -29.88 C-23.59 -43.33, -15.75 -72.48, -14.43 -81.02" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="8 9"></path></g><g transform="translate(142.3507372175026 363.6073700148815) rotate(0 -10.829789214560108 -40.10570548388969)"><path d="M-10.77 -56.44 C-12.33 -61.77, -10.78 -68.39, -14.43 -81.02" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g><g transform="translate(142.3507372175026 363.6073700148815) rotate(0 -10.829789214560108 -40.10570548388969)"><path d="M-27.42 -59.84 C-24.98 -64.25, -19.44 -70.06, -14.43 -81.02" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g></g><mask id="mask-WM7UQjc4eu62cZzmhf5n0"><rect x="0" y="0" fill="#fff" width="264.0103156466228" height="543.8187809826609"></rect><rect x="71.73117496269879" y="320.05186638159523" fill="#000" width="97.91996765136719" height="25" opacity="1"></rect></mask><g transform="translate(71.73117496269879 320.0518663815952) rotate(0 59.37581271349091 2.904440693710825)"><text x="48.959983825683594" y="17.619999999999997" font-family="Excalifont, Xiaolai, Segoe UI Emoji" font-size="20px" fill="#1e1e1e" text-anchor="middle" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">No / Next</text></g><g stroke-linecap="round"><g transform="translate(253.15772335426308 82.27407546430463) rotate(0 0 12.000000000000007)"><path d="M-0.4 0.16 C-0.45 4.02, -0.15 19.68, 0 23.68 M0.39 -0.23 C0.25 3.93, -0.43 20.31, -0.43 24.22" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(253.15772335426308 82.27407546430463) rotate(0 0 12.000000000000007)"><path d="M-4.26 12.84 C-2.7 16.81, -1.9 21.29, -0.43 24.22 M-4.26 12.84 C-3.07 16.42, -1.9 20.48, -0.43 24.22" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(253.15772335426308 82.27407546430463) rotate(0 0 12.000000000000007)"><path d="M3.95 13.04 C2.65 16.91, 0.61 21.32, -0.43 24.22 M3.95 13.04 C2.39 16.59, 0.8 20.58, -0.43 24.22" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(247.9788666742792 279.3683124131073) rotate(0 -0.4695284676550955 16.043784082711113)"><path d="M0.39 -0.2 C0.31 5.2, -0.27 27.31, -0.42 32.62 M-0.07 -0.78 C-0.18 4.46, -0.49 26.46, -0.59 31.93" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(247.9788666742792 279.3683124131073) rotate(0 -0.4695284676550955 16.043784082711113)"><path d="M-5.84 16.76 C-4.5 22.13, -1.82 26.59, -0.59 31.93 M-5.84 16.76 C-4.73 19.97, -3.81 23.13, -0.59 31.93" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(247.9788666742792 279.3683124131073) rotate(0 -0.4695284676550955 16.043784082711113)"><path d="M5.14 16.93 C3.12 22.29, 2.44 26.7, -0.59 31.93 M5.14 16.93 C3.85 20.1, 2.37 23.22, -0.59 31.93" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(249.87168355568053 178.78838057344598) rotate(0 -0.01129442605027009 18.06975525044969)"><path d="M0.36 -0.03 C0.3 5.98, -0.26 29.68, -0.29 35.68 M-0.12 -0.52 C-0.28 5.57, -0.87 29.97, -0.85 36.15" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(249.87168355568053 178.78838057344598) rotate(0 -0.01129442605027009 18.06975525044969)"><path d="M-6.82 19.09 C-5.07 23.91, -3.93 30.01, -0.85 36.15 M-6.82 19.09 C-4.96 23.39, -3.7 28.4, -0.85 36.15" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(249.87168355568053 178.78838057344598) rotate(0 -0.01129442605027009 18.06975525044969)"><path d="M5.54 19.25 C3.47 24.06, 0.78 30.11, -0.85 36.15 M5.54 19.25 C3.99 23.51, 1.83 28.48, -0.85 36.15" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(696.6074381696501 708.2703275198544) rotate(0 0.6143259331372519 24.602363421909672)"><path d="M0.53 0.32 C0.77 8.45, 1.2 40.87, 1.32 49.08 M0.13 0 C0.33 8.2, 0.81 41.59, 0.94 49.71" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(696.6074381696501 708.2703275198544) rotate(0 0.6143259331372519 24.602363421909672)"><path d="M-7.83 26.72 C-4.79 33.16, -3.19 39.34, 0.94 49.71 M-7.83 26.72 C-4.75 35.61, -1.47 43.63, 0.94 49.71" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(696.6074381696501 708.2703275198544) rotate(0 0.6143259331372519 24.602363421909672)"><path d="M9 26.46 C7.42 33.05, 4.41 39.31, 0.94 49.71 M9 26.46 C5.87 35.42, 2.93 43.55, 0.94 49.71" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(691.5371283329548 818.6124398304876) rotate(0 -0.12294634761428824 19.43557794496104)"><path d="M-0.4 0.43 C-0.38 6.79, 0.29 32.28, 0.24 38.62 M0.4 0.18 C0.37 6.84, 0.07 32.74, 0.06 39.19" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.5371283329548 818.6124398304876) rotate(0 -0.12294634761428824 19.43557794496104)"><path d="M-6.46 20.88 C-3.48 27.75, -2.55 32.04, 0.06 39.19 M-6.46 20.88 C-4.82 25.13, -3.35 29.48, 0.06 39.19" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.5371283329548 818.6124398304876) rotate(0 -0.12294634761428824 19.43557794496104)"><path d="M6.84 20.98 C5.47 27.77, 2.05 32.03, 0.06 39.19 M6.84 20.98 C5.42 25.23, 3.82 29.56, 0.06 39.19" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(691.8518028174735 919.0995326811988) rotate(0 -0.8381155503968216 18.58260425712632)"><path d="M-0.21 -0.03 C-0.43 6.15, -0.99 30.91, -1.15 37.18 M0.68 -0.52 C0.43 5.74, -0.99 31.68, -1.31 37.89" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.8518028174735 919.0995326811988) rotate(0 -0.8381155503968216 18.58260425712632)"><path d="M-6.74 20.1 C-5.01 26.73, -3.19 32.46, -1.31 37.89 M-6.74 20.1 C-5.14 26.93, -2.49 33.37, -1.31 37.89" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(691.8518028174735 919.0995326811988) rotate(0 -0.8381155503968216 18.58260425712632)"><path d="M5.97 20.77 C3.6 27.16, 1.33 32.68, -1.31 37.89 M5.97 20.77 C2.79 27.3, 0.67 33.49, -1.31 37.89" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(548.923675917121 993.6301657036602) rotate(0 -267.2273578075334 -375.7997645617079)"><path d="M-0.69 -0.82 C-33.61 -9.93, -127.27 -16.54, -197.47 -55.22 C-267.67 -93.91, -365.9 -152.98, -421.89 -232.94 C-477.89 -312.9, -518.27 -450.05, -533.43 -534.99 C-548.6 -619.93, -529.27 -706.37, -512.88 -742.6 C-496.49 -778.83, -448.26 -750.9, -435.09 -752.37" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="8 9"></path></g><g transform="translate(548.923675917121 993.6301657036602) rotate(0 -267.2273578075334 -375.7997645617079)"><path d="M-459.84 -748.82 C-453.64 -749.6, -443.76 -752.13, -435.09 -752.37" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g><g transform="translate(548.923675917121 993.6301657036602) rotate(0 -267.2273578075334 -375.7997645617079)"><path d="M-456.33 -765.56 C-451.28 -761.25, -442.47 -758.67, -435.09 -752.37" stroke="#1e1e1e" stroke-width="1.5" fill="none"></path></g></g><mask></mask></svg>

=== File: recipes/recipe_executor/recipes/generate_component_code.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "{% assign id_parts = component.id | split: '.' -%}{% assign path = id_parts | size | minus: 1 | join: '/' -%}{% assign id = id_parts | last -%}# Task\n\nYou are an expert developer. Based on the following specification{% if existing_code %} and existing code{% endif %}, generate python code for the {{ component.id }} component of a larger project.\n\n## Specification\n<SPECIFICATION>\n{{ spec }}\n</SPECIFICATION>\n\n{% if existing_code %}## Existing Code\n\nThis is the prior version of the code and can be used for reference, however the specifications or dependencies may have changed, so it may need to be updated.\n\n<EXISTING_CODE>\n{{ existing_code }}\n</EXISTING_CODE>\n\n{% endif %}## Usage Documentation\n\nThis is the usage documentation that will be provided to callers of this component, it is critical that this is considered a contract and must be fulfilled as this is what is being promised from this component.\n\n<USAGE_DOCUMENTATION>\n{{ docs }}\n</USAGE_DOCUMENTATION>\n\n{% if dep_docs %}## Dependency Documentation\n\nIncludes documentation for internal dependencies.\n{% for dep_doc in dep_docs %}<DEPENDENCY_DOC>\n{{ dep_docs[dep_doc] }}\n</DEPENDENCY_DOC>\n{% endfor %}\n{% endif %}{% if ref_docs %}# Reference Documentation\n\nIncludes additional documentation for external libraries that have been loaded into this project.\n{% for ref_doc in ref_docs %}<REFERENCE_DOC>\n{{ ref_docs[ref_doc] }}\n</REFERENCE_DOC>\n{% endfor %}\n{% endif %}## Guidance\n\nEnsure the code follows the specification exactly, implements all required functionality, and adheres to the implementation philosophy described in the tags. Include appropriate error handling and type hints. The implementation should be minimal but complete.\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{ implementation_philosophy }}\n</IMPLEMENTATION_PHILOSOPHY>\n\n{% if dev_guide %}<DEV_GUIDE>\n{{ dev_guide }}\n</DEV_GUIDE>\n\n{% endif %}# Output\n\nGenerate the appropriate file(s) (if the specification defines multiple output files, MAKE SURE TO CREATE ALL FILES at once and return in the `files` collection). For example, {{ output_path | default: 'recipe_executor' }}/{{ path }}/{{ id }}.<ext>, {{ output_path | default: 'recipe_executor' }}/{{ path }}/<other files defined in specification>, etc.\n\n",
        "model": "{{ model | default: 'openai/o4-mini' }}",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "{{ output_root | default: 'output' }}"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/process_component.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "{{ edit | default: false }}",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ existing_code_root | default: 'recipe_executor' }}/{{ component.id | replace: '.', '/' }}.py",
                "content_key": "existing_code",
                "optional": true
              }
            }
          ]
        }
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/recipes/read_component_resources.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/recipes/generate_component_code.json"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/read_component_resources.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/components/{{ component.id | replace: '.', '/' }}/{{ component.id | split: '.' | last }}_spec.md",
        "content_key": "spec"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ recipe_root | default: 'recipes/recipe_executor' }}/components/{{ component.id | replace: '.', '/' }}/{{ component.id | split: '.' | last }}_docs.md",
        "content_key": "docs",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{% for dep in component.deps %}{{ recipe_root | default: 'recipes/recipe_executor' }}/components/{{ dep | replace: '.', '/' }}/{{ dep | split: '.' | last }}_docs.md{% unless forloop.last %},{% endunless %}{% endfor %}",
        "content_key": "dep_docs",
        "merge_mode": "dict",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{% for ref in component.refs %}{{ refs_root | default: 'ai_context' }}/{{ ref }}{% unless forloop.last %},{% endunless %}{% endfor %}",
        "content_key": "ref_docs",
        "merge_mode": "dict",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
        "content_key": "implementation_philosophy"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/DEV_GUIDE_FOR_PYTHON.md",
        "content_key": "dev_guide"
      }
    }
  ]
}


=== File: recipes/recipe_executor/recipes/read_components.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "recipes/recipe_executor/components.json",
        "content_key": "components",
        "merge_mode": "dict"
      }
    }
  ]
}


