# Context Component Specification

## Purpose

The Context component is a core element of the Recipe Executor system, responsible for managing the shared state between steps in a recipe execution. It provides a simple dictionary-like interface for storing and retrieving artifacts and configuration values.

## Core Requirements

The Context component should:

1. Provide a dictionary-like interface for storing and retrieving values
2. Support basic operations like get, set, keys, and iteration
3. Maintain separation between artifacts (data passed between steps) and configuration
4. Offer methods to serialize the context state to a dictionary
5. Follow a minimalist design approach with no unnecessary abstractions

## Component Structure

The Context component should consist of a single class:

```python
class Context:
    def __init__(self, artifacts=None, config=None):
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts (dict, optional): Initial artifacts to store
            config (dict, optional): Configuration values
        """

    def __getitem__(self, key):
        """Dictionary-like access to artifacts"""

    def __setitem__(self, key, value):
        """Dictionary-like setting of artifacts"""

    def get(self, key, default=None):
        """Get an artifact with an optional default value"""

    def keys(self):
        """Return keys of artifacts"""

    def __len__(self):
        """Return number of artifacts"""

    def __iter__(self):
        """Iterate over artifact keys"""

    def as_dict(self):
        """Return a copy of the artifacts as a dictionary"""
```

## Usage Patterns

The Context component should support the following usage patterns:

```python
# Creating a context
context = Context()
context = Context(artifacts={"spec": "..."})
context = Context(config={"output_dir": "..."})

# Setting values
context["key"] = value

# Getting values
value = context["key"]
value = context.get("key", default_value)

# Checking existence
if "key" in context:
    ...

# Iteration
for key in context:
    ...

# Getting all artifacts
artifacts_dict = context.as_dict()
```

## Implementation Philosophy

The Context component should follow these principles:

1. **Ruthless Simplicity**: The implementation should be as simple as possible, avoiding unnecessary abstractions
2. **Minimal State**: Maintain only essential state (artifacts and config)
3. **Direct Access**: Provide direct dictionary-like access to artifacts without indirection
4. **Immutable Export**: The `as_dict()` method should return a copy of the artifacts to prevent accidental mutation

## Integration Points

The Context component integrates with:

1. **Executor**: The executor will create and pass the context between steps
2. **Steps**: All steps will receive and potentially modify the context
3. **Utilities**: Template rendering will use values from the context

## Error Handling

The Context component should provide clear error messages when:

- A non-existent key is accessed without a default
- Attempting to access reserved keys

## Future Considerations

1. Versioning of artifacts
2. Persistence of context between runs
3. Namespacing of artifacts
