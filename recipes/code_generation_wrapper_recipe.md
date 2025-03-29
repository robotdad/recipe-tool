# Code Generation Wrapper Recipe

This recipe acts as an intermediate layer for code generation. It takes the scenario-specific code generation prompt (provided via context as `scenario_prompt`) and augments it with our common quality guidelines (such as our Implementation Philosophy and LEGO-Inspired Vision). It then generates improved code that meets high-quality standards and writes the output to the designated location. The scenario can optionally specify a target artifact key via context (under `target_artifact`); if not provided, the default key `"final_generated_code"` is used.

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
    "prompt": "You are an expert software architect and code generator. A scenario-specific recipe has provided the following code generation request:\n\n{scenario_prompt}\n\nAdditionally, please consider these guiding documents:\n\n--- Implementation Philosophy ---\n{implementation_philosophy}\n\n--- LEGO-Inspired Vision ---\n{lego_vision}\n\nRefine and enhance the code generation request by incorporating best practices for maintainability, type safety, clarity, and simplicity. Then generate code that meets these high standards. Return a JSON object with two keys: 'files' (a list of file objects with 'path' and 'content') and 'commentary' explaining the main improvements and decisions made.",
    "artifact": "enhanced_code_prompt"
  },
  {
    "type": "generate",
    "prompt": "{enhanced_code_prompt}",
    "artifact": "final_generated_code"
  },
  {
    "type": "write_file",
    "artifact": "{{ target_artifact | default('final_generated_code') }}",
    "root": "output/recipe_executor"
  }
]
```
