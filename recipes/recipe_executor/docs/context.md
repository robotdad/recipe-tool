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
```

### Retrieving Values

```python
def __getitem__(self, key: str) -> Any:
    """Dictionary-like access to artifacts."""

def get(self, key: str, default: Optional[Any] = None) -> Any:
    """Get an artifact with an optional default value."""

# Usage examples
value = context["key"]  # Raises KeyError if not found
value = context.get("key", default=None)  # Returns default if not found
```

### Checking Keys

```python
def __contains__(self, key: str) -> bool:
    """Check if a key exists in artifacts."""

# Usage example
if "key" in context:
    # Key exists
    pass
```

### Iteration

```python
def __iter__(self) -> Iterator[str]:
    """Iterate over artifact keys."""

def keys(self) -> Iterator[str]:
    """Return an iterator over the keys of artifacts."""

def __len__(self) -> int:
    """Return the number of artifacts."""

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

### Cloning Context

```python
def clone(self) -> Context:
    """Return a deep copy of the current context."""

# Usage example
cloned_context = context.clone()
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
