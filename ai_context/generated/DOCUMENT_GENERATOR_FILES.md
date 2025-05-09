# recipes/document_generator

[collect-files]

**Search:** ['recipes/document_generator']
**Exclude:** ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc', '*.ruff_cache']
**Include:** []
**Date:** 5/7/2025, 3:29:21 PM
**Files:** 10

=== File: recipes/document_generator/README.md ===
# Instructions for Testing the Recipe Docs recipe

## Run the Recipe Docs recipe

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/document_generator/build.json \
   outline_file=recipes/document_generator/recipe-json-authoring-guide.json \
   output_root=output/docs \
   model=openai/o4-mini
```


=== File: recipes/document_generator/build.json ===
{
  "name": "Document Generator",
  "description": "Generates a document from an outline, using LLMs to fill in sections and assemble the final document.",
  "inputs": {
    "outline_file": {
      "description": "Path to outline json file.",
      "type": "string"
    },
    "model": {
      "description": "LLM model to use for generation.",
      "type": "string",
      "default": "openai/gpt-4o"
    },
    "output_root": {
      "description": "Directory to save the generated document.",
      "type": "string",
      "default": "output"
    }
  },
  "steps": [
    {
      "type": "set_context",
      "config": {
        "key": "model",
        "value": "{{ model | default: 'openai/gpt-4o' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "output_root",
        "value": "{{ output_root | default: 'output' }}"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "recipe_root",
        "value": "{{ recipe_root | default: 'recipes/document_generator' }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/load_outline.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/load_resources.json"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document",
        "value": "# {{ outline.title }}"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_document.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_sections.json",
        "context_overrides": {
          "sections": "{{ outline.sections | json: indent: 2 }}"
        }
      }
    }
  ]
}


=== File: recipes/document_generator/recipe-json-authoring-guide.json ===
{
  "title": "Recipe JSON Authoring Guide",
  "resources": [
    {
      "key": "recipe_executor_code",
      "path": "ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md",
      "description": "Code files related to the recipe executor."
    },
    {
      "key": "recipe_executor_recipes",
      "path": "ai_context/generated/RECIPE_EXECUTOR_RECIPE_FILES.md",
      "description": "Recipe files for the recipe executor itself, includes documentation."
    },
    {
      "key": "sample_recipes",
      "path": "ai_context/generated/BLUEPRINT_GENERATOR_V4_FILES.md",
      "description": "Sample recipes and related files for the blueprint generator."
    },
    {
      "key": "liquid_docs",
      "path": "ai_context/git_collector/LIQUID_PYTHON_DOCS.md",
      "description": "Liquid templating documentation."
    }
  ],
  "sections": [
    {
      "title": "Basic Recipe Structure",
      "prompt": "Explain the basic structure of a recipe JSON file. Include details about the main sections, such as 'steps', 'inputs', and 'outputs'. Provide examples of each section.",
      "refs": ["recipe_executor_code"],
      "sections": [
        {
          "title": "Steps Section",
          "prompt": "Describe the 'steps' section in a recipe JSON file. Explain how to define steps, their types, and configurations. Provide examples of different step types.",
          "refs": ["recipe_executor_code"]
        },
        {
          "title": "Source Code",
          "resource_key": "recipe_executor_code"
        }
      ]
    },
    {
      "title": "Working with Objects Between Recipe Steps",
      "prompt": "Describe how to work with objects between recipe steps. Explain the concept of 'context' and how to pass data between steps. Provide examples of how to use context variables in different steps.",
      "refs": ["recipe_executor_code", "recipe_executor_recipes"]
    },
    {
      "title": "Using Liquid Templating for Dynamic Content",
      "prompt": "Explain how to use Liquid templating in recipe JSON files. Provide examples of how to create dynamic content using Liquid syntax. Discuss common use cases for Liquid templating in recipes.",
      "refs": ["liquid_docs", "recipe_executor_code", "recipe_executor_recipes"]
    },
    {
      "title": "Common Step Types and Configuration",
      "prompt": "List and describe common step types used in recipe JSON files. Include details about their configuration options and how to use them effectively. Provide examples of each step type.",
      "refs": ["recipe_executor_code", "recipe_executor_recipes"]
    },
    {
      "title": "Best Practices and Patterns",
      "prompt": "Outline best practices and patterns for writing recipe JSON files. Discuss common pitfalls to avoid and tips for maintaining readability and organization. Provide examples of well-structured recipes.",
      "refs": [
        "recipe_executor_code",
        "recipe_executor_recipes",
        "sample_recipes"
      ]
    },
    {
      "title": "Recipe Cookbook",
      "prompt": "Provide a collection of example recipes that demonstrate various use cases and patterns. Include detailed explanations of each recipe's purpose and how it works. Discuss how to adapt these recipes for different scenarios.",
      "refs": ["sample_recipes"]
    }
  ]
}


=== File: recipes/document_generator/recipes/load_outline.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ outline_file }}",
        "content_key": "outline"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "toc",
        "value": "{% capture toc %}\n## Table of Contents\n\n{% for sec in outline.sections %}\n- {{ sec.title | escape }}\n{% if sec.sections %}\n  {% for child in sec.sections %}\n  - {{ child.title | escape }}\n  {% endfor %}\n{% endif %}\n{% endfor %}\n{% endcapture %}\n{{ toc }}"
      }
    }
  ]
}


=== File: recipes/document_generator/recipes/load_resources.json ===
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "outline.resources",
        "item_key": "resource",
        "result_key": "resources",
        "substeps": [
          {
            "type": "read_files",
            "config": {
              "path": "{{ resource.path }}",
              "content_key": "content",
              "merge_mode": "{{ resource.merge_mode }}"
            }
          },
          {
            "type": "set_context",
            "config": {
              "key": "resource",
              "value": {
                "content": "{{ content }}"
              },
              "if_exists": "merge"
            }
          }
        ]
      }
    }
  ]
}


=== File: recipes/document_generator/recipes/read_document.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ output_root }}/{{ outline.title | snakecase | upcase }}.md",
        "content_key": "document"
      }
    }
  ]
}


=== File: recipes/document_generator/recipes/write_content.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/read_document.json"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document",
        "value": "\n\n{{ section.title }}\n\n{% for resource in resources %}{% if resource.key == section.resource_key %}{{ resource.content }}{% endif %}{% endfor %}",
        "if_exists": "merge"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_document.json"
      }
    }
  ]
}


=== File: recipes/document_generator/recipes/write_document.json ===
{
  "steps": [
    {
      "type": "write_files",
      "config": {
        "files": [
          {
            "path": "{{ outline.title | snakecase | upcase }}.md",
            "content_key": "document"
          }
        ],
        "root": "{{ output_root }}"
      }
    }
  ]
}


=== File: recipes/document_generator/recipes/write_section.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/read_document.json"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "rendered_prompt",
        "value": "{{ section.prompt }}",
        "nested_render": true
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "model": "{{ model }}",
        "prompt": "Generate a section for the <DOCUMENT> based upon the following prompt:\n<PROMPT>\n{{ rendered_prompt }}\n</PROMPT>\n\nAvailable references:\n<REFERENCE_DOCS>\n{% for ref in section.refs %}{% for resource in resources %}{% if resource.key == ref %}{{ resource.content }}{% endif %}{% endfor %}{% endfor %}\n</REFERENCE_DOCS>\n\nHere is the content of the <DOCUMENT> so far:\n<DOCUMENT>\n{{ document }}\n</DOCUMENT>\n\nPlease write ONLY THE NEW SECTION requested in your PROMPT, in the same style as the rest of the document.",
        "output_format": {
          "type": "object",
          "properties": {
            "content": {
              "type": "string",
              "description": "The generated content for the section."
            }
          }
        },
        "output_key": "generated"
      }
    },
    {
      "type": "set_context",
      "config": {
        "key": "document",
        "value": "\n\n{{ generated.content }}",
        "if_exists": "merge"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "{{ recipe_root }}/recipes/write_document.json"
      }
    }
  ]
}


=== File: recipes/document_generator/recipes/write_sections.json ===
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "sections",
        "item_key": "section",
        "result_key": "section.content",
        "substeps": [
          {
            "type": "conditional",
            "config": {
              "condition": "{% if section.resource_key %}true{% else %}false{% endif %}",
              "if_true": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root }}/recipes/write_content.json"
                    }
                  }
                ]
              },
              "if_false": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root }}/recipes/write_section.json"
                    }
                  }
                ]
              }
            }
          },
          {
            "type": "conditional",
            "config": {
              "condition": "{% assign has_children = section | has: 'sections' %}{% if has_children %}true{% else %}false{% endif %}",
              "if_true": {
                "steps": [
                  {
                    "type": "execute_recipe",
                    "config": {
                      "recipe_path": "{{ recipe_root }}/recipes/write_sections.json",
                      "context_overrides": {
                        "sections": "{{ section.sections | json: indent: 2 }}"
                      }
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  ]
}


