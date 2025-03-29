# Code Generation Recipe

This recipe acts as a system-provided code generator. It takes a scenario-specific code generation prompt provided in context as `scenario_prompt` and augments it with common quality guidelines from our documentation. It then generates improved code that meets high standards for maintainability, type safety, clarity, and simplicity. Rather than writing files to disk, the generated code is stored in the context under a key specified by `target_artifact` (defaulting to `"final_generated_code"` if not provided), so that the caller can decide how to handle the file output.

```json
[
  {
    "type": "read_file",
    "path": "docs/IMPLEMENTATION_PHILOSOPHY.md",
    "artifact": "implementation_philosophy"
  },
  {
    "type": "read_file",
    "path": "docs/Building Software with AI - A LEGO-Inspired Vision.md",
    "artifact": "lego_vision"
  },
  {
    "type": "generate",
    "prompt": "You are an expert software architect and code generator. A scenario-specific request has been provided:\n\n{{scenario_prompt}}\n\nAdditionally, consider these guiding documents:\n\n--- Implementation Philosophy ---\n{{implementation_philosophy}}\n\n--- LEGO-Inspired Vision ---\n{{lego_vision}}\n\nRefine and enhance the code generation request by incorporating best practices for maintainability, type safety, clarity, and simplicity. Then generate code that meets these high standards. Return a JSON object with two keys: 'files' (a list of file objects with 'path' and 'content') and 'commentary' (a summary of improvements made).",
    "artifact": "{{ target_artifact | default: 'final_generated_code' }}"
  }
]
```
