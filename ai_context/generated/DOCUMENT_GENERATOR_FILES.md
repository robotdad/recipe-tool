# recipes/document_generator

[collect-files]

**Search:** ['recipes/document_generator']
**Exclude:** ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc', '*.ruff_cache']
**Include:** []
**Date:** 5/20/2025, 12:10:46 PM
**Files:** 10

=== File: recipes/document_generator/README.md ===
# Instructions for Testing the Document Generator Recipe

## Run the Document Generator Recipe

```bash
# From the repo root, run the document generator recipe to create a readme for the codebase.
recipe-tool --execute recipes/document_generator/document_generator_recipe.json \
   outline_file=recipes/document_generator/examples/readme.json \
   output_root=output/docs \
   model=openai/o4-mini
```


=== File: recipes/document_generator/document_generator_recipe.json ===
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
      "type": "set_context",
      "config": {
        "key": "document_filename",
        "value": "{{ outline_file | default: 'document' | replace: '\\', '/' | split: '/' | last | split: '.' | first | snakecase | upcase }}"
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
        "value": "# {{ outline.title }}\n\n[document-generator]\n\n**Date:** {{ 'now' | date: '%-m/%-d/%Y %I:%M:%S %p' }}"
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


=== File: recipes/document_generator/examples/readme.json ===
{
  "title": "README",
  "general_instruction": "Generate a production-ready README.md for the target codebase. Use only the facts available in the referenced resources (code, docs, configs, tests, etc.). Keep prose short, use bullet lists when helpful, and prefer plain-language explanations over marketing fluff. Assume the audience is a developer seeing the project for the first time.",
  "resources": [
    {
      "key": "codebase_docs",
      "path": "ai_context/generated/RECIPE_EXECUTOR_BLUEPRINT_FILES.md",
      "description": "In-repo design docs, examples, etc."
    },
    {
      "key": "code_files",
      "path": "ai_context/generated/RECIPE_EXECUTOR_CODE_FILES.md",
      "description": "Code files, including scripts and modules."
    }
  ],
  "sections": [
    {
      "title": "Header",
      "prompt": "Produce an H1 title using the repository name. Optionally add shields.io badges for build status, license, or published package version if the information exists.\nWrite a single-sentence summary of what the project does and who it is for, based on the highest-level documentation.",
      "refs": ["codebase_docs", "code_files"]
    },
    {
      "title": "Key Features",
      "prompt": "List the main capabilities or selling points, one bullet per feature, drawing facts from design docs or API specs.",
      "refs": ["codebase_docs", "code_files"]
    },
    {
      "title": "Installation",
      "prompt": "Provide copy-paste installation instructions, including package-manager commands, build steps, and environment variables, using exact data from configuration files.",
      "refs": ["codebase_docs", "code_files"]
    },
    {
      "title": "Usage",
      "prompt": "Show the simplest runnable example pulled from tests, docs, or API specs. If multiple language clients exist, include one example per language.",
      "refs": ["codebase_docs", "code_files"]
    },
    {
      "title": "API Reference",
      "prompt": "If formal API specs exist, generate a short table of endpoints with method, path, and one-line description; otherwise keep the heading with a note indicating N/A.",
      "refs": ["codebase_docs", "code_files"]
    },
    {
      "title": "Architecture Overview",
      "prompt": "Describe the high-level architecture in two or three short paragraphs. If diagrams are available, embed image links and reference major components.",
      "refs": ["codebase_docs", "code_files"]
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
        "path": "{{ output_root }}/{{ document_filename }}.md",
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
            "path": "{{ document_filename }}.md",
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
        "prompt": "Generate a section for the <DOCUMENT> based upon the following prompt:\n<PROMPT>\n{{ rendered_prompt }}\n</PROMPT>\n\nGeneral instruction:\n{{ outline.general_instruction }}\n\nAvailable references:\n<REFERENCE_DOCS>\n{% for ref in section.refs %}{% for resource in resources %}{% if resource.key == ref %}<{{ resource.key | upcase }}><DESCRIPTION>{{ resource.description }}</DESCRIPTION><CONTENT>{{ resource.content }}</CONTENT></{{ resource.key | upcase }}>{% endif %}{% endfor %}{% endfor %}\n</REFERENCE_DOCS>\n\nHere is the content of the <DOCUMENT> so far:\n<DOCUMENT>\n{{ document }}\n</DOCUMENT>\n\nPlease write ONLY THE NEW `{{ section.title }}` SECTION requested in your PROMPT, in the same style as the rest of the document.",
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


