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
          - Will attempt to coerce to a boolean value.
        if_true: Optional steps to execute when the condition evaluates to true.
        if_false: Optional steps to execute when the condition evaluates to false.
    """
    condition: Any
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
                "recipe_path": "recipes/experimental/blueprint_generator/recipes/split_project.json"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator/recipes/process_single_component.json"
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
