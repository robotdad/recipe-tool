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
        "path": "ai_context/PYDANTIC_AI_DOCS.md",
        "contents_key": "pydantic_ai_docs"
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

Let's write some code that uses the PydanticAI library (docs for it are located in `ai_context/PYDANTIC_AI_DOCS.md`, have the recipe read the contents of this file in) to create simple chat client that uses an LLM. Have it create multiple files and use the parallel step to genearte them in parallel.

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
        "contents_key": "idea_content"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{files}}",
        "contents_key": "additional_files_content",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{reference_content}}",
        "contents_key": "reference_content_text",
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

Read in the contents of the files above and then:

Generate some new content based the combined context of the idea + any additional files and then, if provided, tartget the style of the reference content. The generated content should be saved in a file named `<content_title>.md` in the specified output directory.


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
        "contents_key": "spec_text"
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


