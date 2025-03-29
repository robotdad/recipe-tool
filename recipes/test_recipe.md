# Test Code Generation Recipe

This recipe demonstrates a simple workflow.

```json
[
  {
    "type": "read_file",
    "path": "specs/sample_spec.txt",
    "artifact": "spec_text"
  },
  {
    "type": "generate",
    "prompt": "Using the following specification, generate a Python script that prints 'Hello, Test!'.\n\nSpecification:\n${spec_text}",
    "artifact": "generated_code"
  },
  {
    "type": "write_file",
    "artifact": "generated_code",
    "root": "output"
  }
]
```
