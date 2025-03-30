# Steps Base Component Specification

## Purpose

The Steps Base component defines the foundational classes and interfaces for implementing steps in the Recipe Executor system. It provides an abstract base class that all concrete step implementations will inherit from, as well as a registry mechanism for looking up step types by name.

## Core Requirements

The Steps Base component should:

1. Define an abstract `BaseStep` class that all steps inherit from
2. Create a `StepConfig` base class for step configuration validation
3. Implement a central registry for step types
4. Support type hints for improved developer experience
5. Provide a clear interface for step execution
6. Follow a minimal design approach with sensible defaults

## Component Structure

The Steps Base component should consist of the following key elements:

### Step Registry

```python
# A shared registry for all steps
STEP_REGISTRY = {}
```

### Base Step Config

```python
class StepConfig(BaseModel):
    """Base class for all step configs. Extend this in each step."""
    pass

# Type variable for generic step configs
ConfigType = TypeVar("ConfigType", bound=StepConfig)
```

### Base Step Class

```python
class BaseStep(Generic[ConfigType]):
    """
    Base class for all steps. Subclasses must implement `execute(context)`.
    Each step receives a config object and a logger.
    """

    def __init__(self, config: ConfigType, logger: Optional[logging.Logger] = None) -> None:
        self.config: ConfigType = config
        self.logger = logger or logging.getLogger("RecipeExecutor")

    def execute(self, context: Context) -> None:
        """
        Execute the step with the given context.

        Args:
            context: Context for execution

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Each step must implement the `execute()` method.")
```

## Step Registration

The Steps Base component should implement a pattern where step classes are registered in the central registry with their type name. Steps should be automatically registered when imported.

Example registration approach:

```python
# In specific step implementation modules
STEP_REGISTRY["read_file"] = ReadFileStep
```

## Integration Points

The Steps Base component integrates with:

1. **Executor**: The executor uses the STEP_REGISTRY to look up step classes by type
2. **Context**: All steps receive and modify the Context during execution
3. **Models**: Step configuration is validated using configuration models
4. **Concrete Step Implementations**: All concrete steps inherit from BaseStep

## Future Considerations

1. Support for asynchronous step execution
2. Advanced step validation
3. Step lifecycle events (pre/post execution hooks)
4. Step composition and nesting
