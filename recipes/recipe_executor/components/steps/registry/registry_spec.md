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
from recipe_executor.steps.set_context import SetContextStep
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
    "set_context": SetContextStep,
    "write_files": WriteFilesStep,
})
```
