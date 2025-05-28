Goal: Turn a simple text spec into a runnable Python script and save it.

Context variables:

- model (optional): LLM to use, default openai/o4-mini.
- spec_file: Folder with the spec.
- output_root (optional): Where to write files, default output.

Steps:

- Read spec_file.
- Ask the LLM to generate code that satisfies the spec.
- Write the returned file(s) into output_root.
