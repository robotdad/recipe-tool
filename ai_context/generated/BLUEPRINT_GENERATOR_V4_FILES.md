# recipes/experimental/blueprint_generator_v4

[collect-files]

**Search:** ['recipes/experimental/blueprint_generator_v4']
**Exclude:** ['.venv', 'node_modules', '.git', '__pycache__', '*.pyc', '*.ruff_cache']
**Include:** []
**Date:** 5/6/2025, 10:52:16 AM
**Files:** 16

=== File: recipes/experimental/blueprint_generator_v4/README.md ===
# Instructions for Testing the Blueprint Generator v4

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/experimental/blueprint_generator_v4/build.json \
   project_spec=blueprint_test/input/requirements_recipe_tool_ux.md \
   context_docs=blueprint_test/input/vision_recipe_tool_ux.md \
   output_dir=blueprint_test/output/blueprint_generator_v4 \
   model=openai/o4-mini
```

## Youtube Viewer Example with Code Generation

```bash
# Run the Youtube Viewer example
recipe-tool --execute recipes/experimental/blueprint_generator_v4/build.json \
   project_spec=blueprint_test/input/youtube_viewer.md \
   context_docs=blueprint_test/input/videos.json \
   output_dir=blueprint_test/output/youtube_viewer \
   model=openai/o4-mini

# TODO: Handle this in the blueprint generator recipes
# Copy the code generation recipes from the recipe executor
cp recipes/recipe_executor/build.json blueprint_test/output/youtube_viewer/
cp -r recipes/recipe_executor/recipes blueprint_test/output/youtube_viewer/

# Create a simple components.json file
nano blueprint_test/output/youtube_viewer/components.json
# Add single entry:
[
   {
      "id": "main",
      "deps": [],
      "refs": ["blueprint_test/input/videos.json"]
   }
]

# Run the code generation recipe
recipe-tool --execute blueprint_test/output/youtube_viewer/build.json \
   output_root=blueprint_test/output/youtube_viewer/code \
   output_path=youtube_viewer \
   recipe_root=blueprint_test/output/youtube_viewer \
   dev_guide_path=ai_context/DEV_GUIDE_FOR_PYTHON.md,ai_context/DEV_GUIDE_FOR_WEB.md \
   model=openai/o4-mini
```


=== File: recipes/experimental/blueprint_generator_v4/build.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/read_resources.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/analyze_project.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/orchestrate_flow.json"
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/analyze_project.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists(\"{{ output_dir }}/analysis/analysis_result.json\")",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ output_dir }}/analysis/analysis_result.json",
                "content_key": "analysis_result",
                "merge_mode": "dict"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "prompt": "System: You are an expert software architect.\nAnalyze the high-level project specification, vision/context documents, reference docs, and design philosophies.\n<PROJECT_SPEC>\n{{ project_spec_content }}\n</PROJECT_SPEC>\n<CONTEXT_DOCS>\n{% if context_docs_content %}{% for path in context_docs_content %}[{{ path }}]\n{{ context_docs_content[path] }}\n{% endfor %}{% endif %}\n</CONTEXT_DOCS>\n<REFERENCE_DOCS>\n{% if ref_docs_content %}{% for path in ref_docs_content %}[{{ path }}]\n{{ ref_docs_content[path] }}\n{% endfor %}{% endif %}\n</REFERENCE_DOCS>\n<PHILOSOPHY_GUIDES>\n[IMPLEMENTATION] {{ implementation_philosophy }}\n[MODULAR] {{ modular_design_philosophy }}\n[DOCS_GUIDE] {{ component_docs_spec_guide }}\n</PHILOSOPHY_GUIDES>\nPlease output a JSON object with properties:\n- needs_splitting (boolean)\n- components (array of component IDs as strings)\nEnsure the response is valid JSON only.",
                "model": "{{ model }}",
                "output_format": {
                  "type": "object",
                  "properties": {
                    "needs_splitting": {
                      "type": "boolean"
                    },
                    "reason": {
                      "type": "string"
                    },
                    "components": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": { "type": "string" },
                          "name": { "type": "string" },
                          "description": { "type": "string" }
                        },
                        "required": ["id", "name", "description"]
                      }
                    }
                  },
                  "required": ["needs_splitting", "reason", "components"]
                },
                "output_key": "analysis_result"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "analysis_result.json",
                    "content_key": "analysis_result"
                  }
                ],
                "root": "{{ output_dir }}/analysis"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/evaluate_refined_spec.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ output_dir }}/components/{{ component.id }}/approval_result.json')",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ output_dir }}/components/{{ component.id }}/approval_result.json",
                "content_key": "approval_result",
                "merge_model": "dict"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "model": "{{ model }}",
                "prompt": "Evaluate the refined spec for completeness and alignment with our component docs and spec guide. Consider the fact that this is a JSON representation of what will later be converted to a markdown file, so go easy on things like formatting and focus more on determining if this data is comprehensive enough to convert it to a comprehensive docs/spec pair in a future step.\n<REFINED_SPEC>\n{{ refined_spec }}\n</REFINED_SPEC>\n\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{ component_docs_spec_guide }}\n</COMPONENT_DOCS_SPEC_GUIDE>",
                "output_format": {
                  "type": "object",
                  "properties": {
                    "approved": { "type": "boolean" },
                    "notes": { "type": "string" }
                  },
                  "required": ["approved"]
                },
                "output_key": "approval_result"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "{{ component.id }}/approval_result.json",
                    "content_key": "approval_result"
                  }
                ],
                "root": "{{ output_dir }}/components"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_blueprint.json ===
{
  "steps": [
    {
      "type": "llm_generate",
      "config": {
        "model": "{{ model }}",
        "prompt": "Generate the docs file for the component '{{ component.id }}' based on the refined spec and provided diagrams.\nWhere appropriate, include any of the diagrams that would be important for consumers/users of this component, but not the ones only needed by implementers of the component.\n<REFINED_SPEC>\n{{ refined_spec }}\n</REFINED_SPEC>\n<COMPONENT>\n{{ component }}\n</COMPONENT>\n<DIAGRAMS>\n{{ diagrams }}\n</DIAGRAMS>\n<PHILOSOPHY_GUIDES>\n[IMPLEMENTATION] {{ implementation_philosophy }}\n[MODULAR] {{ modular_design_philosophy }}\n[DOCS_GUIDE] {{ component_docs_spec_guide }}\n</PHILOSOPHY_GUIDES>\nSave as '{{ component.id }}_docs.md'.",
        "output_format": "files",
        "output_key": "docs_file"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "docs_file",
        "root": "{{ output_dir }}/components/{{ component.id }}"
      }
    },
    {
      "type": "llm_generate",
      "config": {
        "model": "{{ model }}",
        "prompt": "Generate the spec file for the component '{{ component.id }}' based on the refined spec, component docs, and provided diagrams.\nInclude any of the diagrams that were not used by the docs file for this component, so that they are available to the implementer who will get both the docs and spec file for their context.\n<REFINED_SPEC>\n{{ refined_spec }}\n</REFINED_SPEC>\n<COMPONENT>\n{{ component }}\n</COMPONENT>\n<DIAGRAMS>\n{{ diagrams }}\n</DIAGRAMS>\n<COMPONENT_DOCS>\n{{ docs_file[0].content }}\n</COMPONENT_DOCS>\n<PHILOSOPHY_GUIDES>\n[IMPLEMENTATION] {{ implementation_philosophy }}\n[MODULAR] {{ modular_design_philosophy }}\n[DOCS_GUIDE] {{ component_docs_spec_guide }}\n</PHILOSOPHY_GUIDES>\nEmpty arrays should be rendered as the string **None** under their respective sections. Save as '{{ component.id }}_spec.md'.",
        "output_format": "files",
        "output_key": "spec_file"
      }
    },
    {
      "type": "write_files",
      "config": {
        "files_key": "spec_file",
        "root": "{{ output_dir }}/components/{{ component.id }}"
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_candidate_spec.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ output_dir }}/components/{{ component.id }}/candidate_spec.json')",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ output_dir }}/components/{{ component.id }}/candidate_spec.json",
                "content_key": "candidate_spec",
                "merge_model": "dict"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "model": "{{ model }}",
                "prompt": "You are an expert software architect.\nGenerate a standalone specification for component '{{ component.id }}' given the project spec, context docs, reference docs, and design philosophies.\n<COMPONENT>\n{{ component }}\n</COMPONENT>\n<PROJECT_SPEC>\n{{ project_spec_content }}\n</PROJECT_SPEC>\n<CONTEXT_DOCS>\n{% if context_docs_content %}{% for path in context_docs_content %}[{{ path }}]\n{{ context_docs_content[path] }}\n{% endfor %}{% endif %}\n</CONTEXT_DOCS>\n<REFERENCE_DOCS>\n{% if ref_docs_content %}{% for path in ref_docs_content %}[{{ path }}]\n{{ ref_docs_content[path] }}\n{% endfor %}{% endif %}\n</REFERENCE_DOCS>\n<PHILOSOPHY_GUIDES>\n[IMPLEMENTATION] {{ implementation_philosophy }}\n[MODULAR] {{ modular_design_philosophy }}\n[DOCS_GUIDE] {{ component_docs_spec_guide }}\n</PHILOSOPHY_GUIDES>\nFor any lists that would result in **None**, return an empty array.",
                "output_format": {
                  "type": "object",
                  "properties": {
                    "component_title": { "type": "string" },
                    "purpose_statement": { "type": "string" },
                    "core_requirements": {
                      "type": "array",
                      "items": { "type": "string" }
                    },
                    "implementation_considerations": {
                      "type": "array",
                      "items": { "type": "string" }
                    },
                    "component_dependencies": {
                      "type": "object",
                      "properties": {
                        "internal_components": {
                          "type": "array",
                          "items": { "type": "string" }
                        },
                        "external_libraries": {
                          "type": "array",
                          "items": { "type": "string" }
                        },
                        "configuration_dependencies": {
                          "type": "array",
                          "items": { "type": "string" }
                        }
                      },
                      "required": [
                        "internal_components",
                        "external_libraries",
                        "configuration_dependencies"
                      ]
                    },
                    "output_files": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "path": { "type": "string" },
                          "description": { "type": "string" }
                        },
                        "required": ["path", "description"]
                      }
                    },
                    "logging_requirements": {
                      "type": "object",
                      "properties": {
                        "debug": {
                          "type": "array",
                          "items": { "type": "string" }
                        },
                        "info": {
                          "type": "array",
                          "items": { "type": "string" }
                        }
                      },
                      "required": ["debug", "info"]
                    },
                    "error_handling": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "error_type": { "type": "string" },
                          "error_message": { "type": "string" },
                          "recovery_action": { "type": "string" }
                        },
                        "required": [
                          "error_type",
                          "error_message",
                          "recovery_action"
                        ]
                      }
                    },
                    "dependency_integration_considerations": {
                      "type": "array",
                      "items": { "type": "string" }
                    }
                  },
                  "required": [
                    "component_title",
                    "purpose_statement",
                    "core_requirements",
                    "implementation_considerations",
                    "component_dependencies",
                    "output_files",
                    "logging_requirements",
                    "error_handling",
                    "dependency_integration_considerations"
                  ]
                },
                "output_key": "candidate_spec"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "{{ component.id }}/candidate_spec.json",
                    "content_key": "candidate_spec"
                  }
                ],
                "root": "{{ output_dir }}/components"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_clarification_questions.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ output_dir }}/components/{{ component.id }}/clarification_questions.json')",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ output_dir }}/components/{{ component.id }}/clarification_questions.json",
                "content_key": "clarification_questions",
                "merge_model": "dict"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "model": "{{ model }}",
                "prompt": "Review the following candidate spec and generate any clarification questions that would be needed to create the spec and docs files as defined within the attached guide.\n<CANDIDATE_SPEC>\n{{ candidate_spec }}\n</CANDIDATE_SPEC>\nRespond with a JSON array of strings (questions).\n\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{ component_docs_spec_guide }}\n</COMPONENT_DOCS_SPEC_GUIDE>",
                "output_format": [{ "type": "string" }],
                "output_key": "clarification_questions"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "{{ component.id }}/clarification_questions.json",
                    "content_key": "clarification_questions"
                  }
                ],
                "root": "{{ output_dir }}/components"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_diagrams.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ output_dir }}/components/{{ component.id }}/diagrams.json')",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ output_dir }}/components/{{ component.id }}/diagrams.json",
                "content_key": "diagrams",
                "merge_model": "dict"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "model": "{{ model }}",
                "prompt": "Create mermaid versions of the useful UML diagrams for this component '{{ component.id }}' based on the refined spec.\n<COMPONENT>\n{{ component }}\n</COMPONENT>\n<REFINED_SPEC>\n{{ refined_spec }}\n</REFINED_SPEC>\n<UML_MERMAID_GUIDE>\n{{ uml_mermaid_guide }}\n</UML_MERMAID_GUIDE>. For the mermaid code, do not use parentheses in labels",
                "output_format": [
                  {
                    "type": "object",
                    "properties": {
                      "name": { "type": "string" },
                      "description": { "type": "string" },
                      "mermaid_code": { "type": "string" }
                    }
                  }
                ],
                "output_key": "diagrams"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "{{ component.id }}/diagrams.json",
                    "content_key": "diagrams"
                  }
                ],
                "root": "{{ output_dir }}/components"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_refined_spec.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ output_dir }}/components/{{ component.id }}/refined_spec.json')",
        "if_true": {
          "steps": [
            {
              "type": "read_files",
              "config": {
                "path": "{{ output_dir }}/components/{{ component.id }}/refined_spec.json",
                "content_key": "refined_spec",
                "merge_model": "dict"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "model": "{{ model }}",
                "prompt": "Generate a refined spec for the component based on the candidate spec and the clarification questions.\n<CANDIDATE_SPEC>\n{{ candidate_spec }}\n</CANDIDATE_SPEC>\n<QUESTIONS>\n{{ clarification_questions }}\n</QUESTIONS>\n\nAdditional Context:\n\n<PROJECT_SPEC>\n{{ project_spec_content }}\n</PROJECT_SPEC>\n<CONTEXT_DOCS>\n{% if context_docs_content %}{% for path in context_docs_content %}[{{ path }}]\n{{ context_docs_content[path] }}\n{% endfor %}{% endif %}\n</CONTEXT_DOCS>\n<REFERENCE_DOCS>\n{% if ref_docs_content %}{% for path in ref_docs_content %}[{{ path }}]\n{{ ref_docs_content[path] }}\n{% endfor %}{% endif %}\n</REFERENCE_DOCS>\n<PHILOSOPHY_GUIDES>\n[IMPLEMENTATION] {{ implementation_philosophy }}\n[MODULAR] {{ modular_design_philosophy }}\n[DOCS_GUIDE] {{ component_docs_spec_guide }}\n</PHILOSOPHY_GUIDES>For any lists that would result in **None**, return an empty array.",
                "output_format": {
                  "type": "object",
                  "properties": {
                    "component_title": { "type": "string" },
                    "purpose_statement": { "type": "string" },
                    "core_requirements": {
                      "type": "array",
                      "items": { "type": "string" }
                    },
                    "implementation_considerations": {
                      "type": "array",
                      "items": { "type": "string" }
                    },
                    "component_dependencies": {
                      "type": "object",
                      "properties": {
                        "internal_components": {
                          "type": "array",
                          "items": { "type": "string" }
                        },
                        "external_libraries": {
                          "type": "array",
                          "items": { "type": "string" }
                        },
                        "configuration_dependencies": {
                          "type": "array",
                          "items": { "type": "string" }
                        }
                      },
                      "required": [
                        "internal_components",
                        "external_libraries",
                        "configuration_dependencies"
                      ]
                    },
                    "output_files": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "path": { "type": "string" },
                          "description": { "type": "string" }
                        },
                        "required": ["path", "description"]
                      }
                    },
                    "logging_requirements": {
                      "type": "object",
                      "properties": {
                        "debug": {
                          "type": "array",
                          "items": { "type": "string" }
                        },
                        "info": {
                          "type": "array",
                          "items": { "type": "string" }
                        }
                      },
                      "required": ["debug", "info"]
                    },
                    "error_handling": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "error_type": { "type": "string" },
                          "error_message": { "type": "string" },
                          "recovery_action": { "type": "string" }
                        },
                        "required": [
                          "error_type",
                          "error_message",
                          "recovery_action"
                        ]
                      }
                    },
                    "dependency_integration_considerations": {
                      "type": "array",
                      "items": { "type": "string" }
                    }
                  },
                  "required": [
                    "component_title",
                    "purpose_statement",
                    "core_requirements",
                    "implementation_considerations",
                    "component_dependencies",
                    "output_files",
                    "logging_requirements",
                    "error_handling",
                    "dependency_integration_considerations"
                  ]
                },
                "output_key": "refined_spec"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "{{ component.id }}/refined_spec.json",
                    "content_key": "refined_spec"
                  }
                ],
                "root": "{{ output_dir }}/components"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/human_review_needed.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "file_exists('{{ output_dir }}/{{ component.id }}_review_needed.md')",
        "if_false": {
          "steps": [
            {
              "type": "llm_generate",
              "config": {
                "model": "{{ model }}",
                "prompt": "Write up a brief summary of why the specification for this component needs human review, based upon the approval result.\n<REFINED_SPEC>\n{{ refined_spec }}\n</REFINED_SPEC>\n\n<COMPONENT_DOCS_SPEC_GUIDE>\n{{ component_docs_spec_guide }}\n</COMPONENT_DOCS_SPEC_GUIDE>\n\n<APPROVAL_RESULT>\n{{ approval_result }}\n</APPROVAL_RESULT>",
                "output_format": "text",
                "output_key": "human_review_needed"
              }
            },
            {
              "type": "write_files",
              "config": {
                "files": [
                  {
                    "path": "{{ component.id }}_review_needed.md",
                    "content_key": "human_review_needed"
                  }
                ],
                "root": "{{ output_dir }}"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/process_component.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_candidate_spec.json"
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/refine_cycle.json",
        "context_overrides": {
          "candidate_spec": "{{ candidate_spec }}",
          "retry_count": 0,
          "max_retries": 2
        }
      }
    },
    {
      "type": "conditional",
      "config": {
        "condition": "{{ approval_result.approved }}",
        "if_false": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/human_review_needed.json"
              }
            }
          ]
        },
        "if_true": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_diagrams.json"
              }
            },
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_blueprint.json"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/component_processor/refine_cycle.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_clarification_questions.json",
        "context_overrides": {
          "candidate_spec": "{% assign rc = retry_count | default: 0 | plus: 0 %}{% if rc > 0 %}{{ refined_spec }}{% else %}{{ candidate_spec }}{% endif %}",
          "force_generate": "{% assign rc = retry_count | default: 0 | plus: 0 %}{% if rc > 0 %}true{% else %}false{% endif %}"
        }
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/generate_refined_spec.json",
        "context_overrides": {
          "force_generate": "{% assign rc = retry_count | default: 0 | plus: 0 %}{% if rc > 0 %}true{% else %}false{% endif %}"
        }
      }
    },
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/evaluate_refined_spec.json"
      }
    },
    {
      "type": "conditional",
      "config": {
        "condition": "and(not({{ approval_result.approved | default: false }}), {{ retry_count }} < {{ max_retries }})",
        "if_true": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/refine_cycle.json",
                "context_overrides": {
                  "candidate_spec": "{{ refined_spec }}",
                  "force_generate": true,
                  "retry_count": "{{ retry_count | plus: 1 }}"
                }
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/generate_single_component.json ===
{
  "steps": [
    {
      "type": "execute_recipe",
      "config": {
        "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/process_component.json",
        "context_overrides": {
          "component": {
            "id": "main",
            "name": "Main Component",
            "description": "This is the main component of this single-component project."
          }
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/orchestrate_flow.json ===
{
  "steps": [
    {
      "type": "conditional",
      "config": {
        "condition": "{{ analysis_result.needs_splitting }}",
        "if_true": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/process_components.json"
              }
            }
          ]
        },
        "if_false": {
          "steps": [
            {
              "type": "execute_recipe",
              "config": {
                "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/generate_single_component.json"
              }
            }
          ]
        }
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/process_components.json ===
{
  "steps": [
    {
      "type": "loop",
      "config": {
        "items": "analysis_result.components",
        "item_key": "component",
        "max_concurrency": 0,
        "delay": 0.1,
        "substeps": [
          {
            "type": "execute_recipe",
            "config": {
              "recipe_path": "recipes/experimental/blueprint_generator_v4/recipes/component_processor/process_component.json"
            }
          }
        ],
        "result_key": "processed_components"
      }
    }
  ]
}


=== File: recipes/experimental/blueprint_generator_v4/recipes/read_resources.json ===
{
  "steps": [
    {
      "type": "read_files",
      "config": {
        "path": "{{ project_spec }}",
        "content_key": "project_spec_content"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ ref_docs }}",
        "content_key": "ref_docs_content",
        "merge_mode": "dict",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "{{ context_docs }}",
        "content_key": "context_docs_content",
        "merge_mode": "dict",
        "optional": true
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/UML_MERMAID_GUIDE.md",
        "content_key": "uml_mermaid_guide"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/IMPLEMENTATION_PHILOSOPHY.md",
        "content_key": "implementation_philosophy"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/MODULAR_DESIGN_PHILOSOPHY.md",
        "content_key": "modular_design_philosophy"
      }
    },
    {
      "type": "read_files",
      "config": {
        "path": "ai_context/COMPONENT_DOCS_SPEC_GUIDE.md",
        "content_key": "component_docs_spec_guide"
      }
    }
  ]
}


