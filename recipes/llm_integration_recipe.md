# LLM Integration Module Recipe

This recipe generates a Python module that defines the LLM integration for the recipe_executor tool. The module (to be written as `output/recipe_executor/llm.py`) should:

- Import necessary modules (e.g., logging and Pydantic-AI components).
- Initialize an LLM agent (for example, using GPT-4) with a system prompt that instructs the LLM to produce a JSON object with two keys: `files` (a list of file objects with `path` and `content`) and `commentary`.
- Define a function `call_llm(prompt: str)` that:
  - Uses the LLM agent to generate a response based on the provided prompt.
  - Returns the structured output (with keys `files` and `commentary`).
  - Handles errors by logging detailed information and, if needed, returns a dummy `FileGenerationResult` (e.g., a default file with a simple "Hello, Test!" message).
- Include proper type annotations, clear docstrings, and error handling.

The final output must be a JSON object with two keys:

- `files`: a list of file objects (each with `path` and `content`).
- `commentary`: a string with additional commentary on the generation.

```json
[
  {
    "type": "read_file",
    "path": "docs/pydantic-ai/pydantic_ai_files.md",
    "artifact": "pydantic_ai_files"
  },
  {
    "type": "execute_recipe",
    "recipe_path": "recipes/code_generation_recipe.md",
    "context_overrides": {
      "scenario_prompt": "Generate a Python module named 'llm.py' that integrates with an LLM for code generation. The module should:\n\n- Import necessary modules including logging and components from Pydantic AI.\n- Attempt to initialize an LLM agent (e.g., using GPT-4o) with a system prompt that instructs it to generate a JSON object with exactly two keys: 'files' (a list of file objects with 'path' and 'content') and 'commentary'.\n- Define a function 'call_llm(prompt: str)' that sends the provided prompt to the LLM agent and returns the resulting structured output. If the agent is not initialized or if the call fails, the function should log the error and return a dummy FileGenerationResult with a default file (e.g., a file at 'generated/hello.py' with content 'print(\"Hello, Test!\")').\n\nInclude proper type annotations, clear docstrings, and robust error handling. The final output should be a JSON object with 'files' (a list of file objects with 'path' and 'content') and 'commentary' (a string with additional comments).\n\n--- Pydantic AI Documentation ---\n{{pydantic_ai_files}}",
      "target_artifact": "generated_llm_integration_module"
    }
  },
  {
    "type": "write_file",
    "artifact": "generated_llm_integration_module",
    "root": "output/recipe_executor"
  }
]
```
