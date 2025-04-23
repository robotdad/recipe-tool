# AI Context Files
Date: 4/23/2025, 3:51:20 PM
Files: 14

=== File: recipes/example_complex/README.md ===
# Complex Code Generation Recipe

This recipe demonstrates a multi-step workflow that:

1. Reads two specification files.
2. Uses an LLM step to generate a comprehensive Python module that integrates both core and auxiliary functionalities.
3. Writes the generated module to disk.
4. Executes a sub-recipe to generate an additional utility module.


=== File: recipes/example_complex/complex_example.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/git_collector/PYDANTIC_AI_DOCS.md",
        "content_key": "pydantic_ai_docs"
      }
    },
    {
      "type": "parallel",
      "config": {
        "substeps": [
          {
            "type": "llm_generate",
            "config": {
              "prompt": "You are an expert Python developer. Using the PydanticAI documentation below:\n\n{{pydantic_ai_docs}}\n\nGenerate a module named 'chat_client.py' that implements a simple chat client which connects to an LLM for conversation. The code should be well-structured and include error handling.",
              "model": "openai/gpt-4o",
              "mcp_servers": [
                { "command": "python-code-tools", "args": ["stdio"] }
              ],
              "output_format": "files",
              "output_key": "chat_client_file"
            }
          },
          {
            "type": "llm_generate",
            "config": {
              "prompt": "You are an expert Python developer. Using the PydanticAI documentation below:\n\n{{pydantic_ai_docs}}\n\nGenerate a module named 'chat_server.py' that implements a simple chat server which interacts with an LLM for handling conversations. Ensure the code structure is clear. IMPORTANT: Intentionally include a couple of deliberate syntax errors in the code to test error detection (for example, missing colon, unbalanced parentheses).",
              "model": "openai/gpt-4o",
              "mcp_servers": [
                { "command": "python-code-tools", "args": ["stdio"] }
              ],
              "output_format": "files",
              "output_key": "chat_server_file"
            }
          },
          {
            "type": "llm_generate",
            "config": {
              "prompt": "You are an expert Python developer. Using the PydanticAI documentation below:\n\n{{pydantic_ai_docs}}\n\nGenerate a module named 'linting_tool.py' that creates a function to lint Python code. The module should call an external linting tool, capture its output (lint report), and return both the possibly corrected code files and the lint report. Make sure the output is structured as a list of file specifications.\n",
              "model": "openai/gpt-4o",
              "mcp_servers": [
                { "command": "python-code-tools", "args": ["stdio"] }
              ],
              "output_format": "files",
              "output_key": "linting_result"
            }
          }
        ],
        "max_concurrency": 3,
        "delay": 0
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "You are given three JSON arrays representing file specifications from previous steps:\n\nChat Client Files: {{chat_client_file}}\n\nChat Server Files: {{chat_server_file}}\n\nLinting Result Files: {{linting_result}}\n\nCombine these arrays into a single JSON array of file specifications without modifying the content of the files. Return the result as a JSON array.",
        "model": "openai/gpt-4o",
        "mcp_servers": [{ "command": "python-code-tools", "args": ["stdio"] }],
        "output_format": "files",
        "output_key": "final_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "final_files",
        "root": "output/complex_example"
      }
    }
  ]
}


=== File: recipes/example_complex/prompts/complex_example_idea.md ===
Create a recipe file named `complex_example.json` that generates a recipe file based on the following scenario:

Let's write some code that uses the PydanticAI library (docs for it are located in `ai_context/git_collector/PYDANTIC_AI_DOCS.md`, have the recipe read the content of this file in) to create simple chat client that uses an LLM. Have it create multiple files and use the parallel step to generate them in parallel.

But let's also test the use of MCP servers within the LLM generate steps. Configure the LLM step to use our python code tools MCP server (details below). Then let's ask the LLM to generate some code to use it's linting tool and returning a report from that along with the code files. However, intentionally include some errors in the code in **one** of the modules. Finally write the final code to individual files in `output/complex_example`.

Here are the details for the python code tools MCP server:
command: `python-code-tools`
args: `stdio`


=== File: recipes/example_content_writer/generate_content.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{idea}}",
        "content_key": "idea_content"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{files}}",
        "content_key": "additional_files_content",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{reference_content}}",
        "content_key": "reference_content_text",
        "optional": true
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "You are an expert creative writer. Using the idea provided below, and any additional context if available, generate new content that is engaging and follows the style of the reference content if provided. Output your answer as a JSON object with exactly two keys: 'path' and 'content'. The 'path' must be a filename ending with .md (which will be used as the output file name), and 'content' is the full generated content. Do not include any additional text outside the JSON object.\n\nIdea:\n{{idea_content}}\n\nAdditional Context (if any):\n{{additional_files_content}}\n\nReference Style (optional):\n{{reference_content_text}}",
        "model": "{{model|default:'openai/gpt-4'}}",
        "output_format": "files",
        "output_key": "generated_content"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_content",
        "root": "{{output_root|default:'.'}}"
      }
    }
  ]
}


=== File: recipes/example_content_writer/prompts/content_from_idea.md ===
Create a recipe file named `generate_content.json` that generates new content based on the following scenario:

Input context variables:

- A file that contains the big idea for the new content: `idea` context variable, required.
- Additional files to include in the context for the content: `files` context variable, optional.
- Reference files used to demonstrate the user's voice and style: `reference_content` context variable, optional.
- The model to use for generating the content: `model` context variable, optional.
- The root directory for saving the generated content: `output_root` context variable, optional.

Read in the content of the files above and then:

Generate some new content based the combined context of the idea + any additional files and then, if provided, tartget the style of the reference content. The generated content should be saved in a file named `<content_title>.md` in the specified output directory.


=== File: recipes/example_loops/process_test_item.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Transform the following item based on its type:\n- If type is 'string': Convert value to uppercase\n- If type is 'number': Multiply value by 2\n- If type is 'object': Add a 'processed: true' property to the value\n\nItem: {{current_item}}\n\nOutput the transformed item with the same structure (keeping the type field).",
        "model": "openai/o3-mini",
        "output_format": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string"
            },
            "value": {
              "type": ["string", "number", "object"]
            }
          },
          "required": ["type", "value"]
        },
        "output_key": "transformed_item"
      }
    }
  ]
}


=== File: recipes/example_loops/test_loop.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "test_output/initial_collection.json",
        "content_key": "collection_data",
        "merge_mode": "dict"
      }
    },
    {
      "type": "loop",
      "config": {
        "items": "collection_data.test_items",
        "item_key": "current_item",
        "substeps": [
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "process_test_item.json"
            }
          }
        ],
        "result_key": "processed_items"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Verify that the loop processing worked correctly by analyzing these results:\n\nOriginal items: {{collection_data.test_items}}\n\nProcessed items: {{processed_items}}\n\nProvide a detailed analysis of what changed for each item and whether the transformations were applied correctly.",
        "model": "openai/o3-mini",
        "output_format": "text",
        "output_key": "verification_result"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "test_output/loop_test_results.md",
            "content": "# Loop Component Test Results\n\n## Original Items\n```json\n{{collection_data.test_items}}\n```\n\n## Processed Items\n```json\n{{processed_items}}\n```\n\n## Verification\n{{verification_result}}"
          }
        ]
      }
    }
  ]
}


=== File: recipes/example_loops/test_loop_errors.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "test_output/initial_collection.json",
        "contents_key": "collection_data"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Take this collection of items and add one invalid item (with a non-existent type or malformed structure) that might cause an error during processing:\n\n{{collection_data.test_items}}\n\nReturn the modified array with the added error-causing item.",
        "model": "openai/o3-mini",
        "output_format": {
          "type": "array",
          "items": {
            "type": "object"
          }
        },
        "output_key": "test_items_with_error"
      }
    },
    {
      "type": "loop",
      "config": {
        "items": "test_items_with_error",
        "item_key": "current_item",
        "substeps": [
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "process_test_item.json"
            }
          }
        ],
        "result_key": "processed_items",
        "fail_fast": false
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "test_output/error_handling_results.md",
            "content": "# Loop Error Handling Test Results\n\n## Input Items (including error item)\n```json\n{{test_items_with_error}}\n```\n\n## Processed Items (should continue despite errors)\n```json\n{{processed_items}}\n```\n\n## Errors (if any)\n```json\n{{__errors|default:'No errors captured'}}\n```"
          }
        ]
      }
    }
  ]
}


=== File: recipes/example_loops/test_loop_setup.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Create a test collection with different types of data. Output only a JSON array with 5 items: two strings, two numbers, and one object with properties.",
        "model": "openai/o3-mini",
        "output_format": {
          "type": "object",
          "properties": {
            "test_items": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "type": {
                    "type": "string"
                  },
                  "value": {
                    "type": ["string", "number", "object"]
                  }
                },
                "required": ["type", "value"]
              }
            }
          },
          "required": ["test_items"]
        },
        "output_key": "collection_result"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "test_output/initial_collection.json",
            "content_key": "collection_result"
          }
        ]
      }
    }
  ]
}


=== File: recipes/example_mcp_step/mcp_step_example.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{input}}",
        "content_key": "code",
        "optional": false,
        "merge_mode": "concat"
      }
    },
    {
      "type": "mcp",
      "config": {
        "server": {
          "command": "python-code-tools",
          "args": ["stdio"]
        },
        "tool_name": "lint_code",
        "arguments": {
          "code": "{{code}}",
          "fix": true,
          "config": "{}"
        },
        "result_key": "code_analysis"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Generate a comprehensive report based on the following code analysis results:\n{{ code }}\n{{ code_analysis }}\n\nSave to: {{ input | split: '.' | first }}_code_analysis.md",
        "model": "openai/gpt-4o",
        "output_format": "files",
        "output_key": "generated_report"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_report",
        "root": "output"
      }
    }
  ]
}


=== File: recipes/example_mcp_step/prompt/mcp_step_idea.md ===
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


=== File: recipes/example_simple/README.md ===
# Test Code Generation Recipe

This recipe demonstrates a simple workflow that reads a specification file and generates a Python module based on it. The generated module is then written to disk.


=== File: recipes/example_simple/specs/sample_spec.txt ===
Print "Hello, Test!" to the console.


=== File: recipes/example_simple/test_recipe.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "recipes/example_simple/specs/sample_spec.txt",
        "content_key": "spec_text"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "prompt": "Using the following specification, generate a Python script:\n\n{{spec_text}}",
        "model": "{{model|default:'openai/o3-mini'}}",
        "output_format": "files",
        "output_key": "generated_files"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "generated_files",
        "root": "output"
      }
    }
  ]
}


