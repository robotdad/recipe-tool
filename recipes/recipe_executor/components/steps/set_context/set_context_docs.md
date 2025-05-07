# SetContextStep Component Usage

## Importing

```python
from recipe_executor.steps.set_context import SetContextStep, SetContextConfig
```

## Configuration

`SetContextStep` is configured with a simple `SetContextConfig`:

```python
class SetContextConfig(StepConfig):
    """
    Config for SetContextStep.

    Fields:
        key: Name of the artifact in the Context.
        value: String, list, dict **or** Liquid template string rendered against
               the current context.
        if_exists: Strategy when the key already exists:
                   • "overwrite" (default) – replace the existing value
                   • "merge" – combine the existing and new values
    """
    key: str
    value: Union[str, list, dict]
    if_exists: Literal["overwrite", "merge"] = "overwrite"
```

### Merge semantics (when `if_exists: "merge"`)

| Existing type      | New type       | Result                                                      |
| ------------------ | -------------- | ----------------------------------------------------------- |
| `str`              | `str`          | `old + new` (simple concatenation)                          |
| `list`             | `list` or item | `old + new` (append)                                        |
| `dict`             | `dict`         | Shallow merge – keys in `new` overwrite duplicates in `old` |
| Other / mismatched | any            | `[old, new]` (both preserved in a list)                     |

## Step Registration

Register once (typically in `recipe_executor/steps/__init__.py`):

```python
from recipe_executor.steps.registry import STEP_REGISTRY
from recipe_executor.steps.set_context import SetContextStep

STEP_REGISTRY["set_context"] = SetContextStep
```

The executor will then recognise the `"set_context"` step type during recipe execution.

## Basic Usage in Recipes

**Create or append to a document artifact**

```json
{
  "type": "set_context",
  "config": {
    "key": "document",
    "value": "{{ content }}",
    "if_exists": "merge"
  }
}
```

**Pull a section from another artifact**

```json
{
  "type": "set_context",
  "config": {
    "key": "section_md",
    "value": "{{ context[section.content_key] }}"
  }
}
```

After execution, the target keys (`document`, `section_md`) are available for any downstream steps in the same recipe run, just like artifacts produced by `read_files`, `llm_generate`, or other core steps.

## Important Notes

- `value` strings are rendered with the same Liquid templating engine used throughout the toolchain, so you can interpolate any current context values before they are stored.
- `if_exists` defaults to `"overwrite"` to preserve backward-compatible behaviour with existing recipes.
- Merging is intentionally **shallow** for dictionaries to keep the step lightweight; if you need deep-merge semantics, perform that in a custom step or LLM call.
