# Code Generator Recipe

This recipe reads a primary specification along with supporting context documents, then generates a complete multi-file codebase.

```json
{
  "steps": [
    {
      "type": "ReadFile",
      "config": {
        "file_path": "specs/recipe_executor.md",
        "store_key": "spec_text"
      }
    },
    {
      "type": "ReadFile",
      "config": {
        "file_path": "docs/IMPLEMENTATION_PHILOSOPHY.md",
        "store_key": "impl_philosophy"
      }
    },
    {
      "type": "ReadFile",
      "config": {
        "file_path": "docs/AI_ASSISTANT_GUIDE-general-early-codebase.md",
        "store_key": "assistant_guide"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "codegen_result",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "codegen_result",
        "output_root": ""
      }
    }
  ]
}
```
