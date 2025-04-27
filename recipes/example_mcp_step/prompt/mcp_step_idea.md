Create a recipe named `mcp_step_example.json` that demonstrates the use of the MCP step in a recipe. The recipe should:

- Read in a code file from a path provided via the `input` context variable.
- Pass the code file to the MCP step for processing using a specific tool call:

  - MCP Server:

    - Command: `python-code-tools`
    - Args: `stdio`

  - Tool Call:

    ```python
    async def lint_code(code: str, fix: bool = True, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Lint Python code and optionally fix issues.

        Args:
            code: The Python code to lint
            fix: Whether to automatically fix issues when possible
            config: Optional configuration settings for the linter

        Returns:
            A dictionary containing the fixed code, issues found, and fix counts
    ```

- Pass the results of the tool call to an LLM step to generate a report and output as type `files`:

```prompt
Generate a comprehensive report based on the following code analysis results:
{{ code }}
{{ code_analysis }}

Save to: [{{ input }} file name w/o extension] + `_code_analysis.md`.
```

- Write the file to the `output` directory.
