# Multi-step Code Generation Recipe

This recipe breaks down the code generation of the Recipe Executor into multiple focused steps. It reads the updated specification and context documents, generates each component of the tool separately, and then writes all the files to a new output directory for review.

```json
{
  "steps": [
    {
      "type": "ReadFile",
      "config": {
        "file_path": "specs/recipe_executor.md",
        "store_key": "spec_text"
      }
    },
    {
      "type": "ReadFile",
      "config": {
        "file_path": "docs/IMPLEMENTATION_PHILOSOPHY.md",
        "store_key": "impl_philosophy"
      }
    },
    {
      "type": "ReadFile",
      "config": {
        "file_path": "docs/AI_ASSISTANT_GUIDE-general-early-codebase.md",
        "store_key": "assistant_guide"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "context_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"context.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "logger_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"logger.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "models_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"models.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "utils_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"utils.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "base_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"steps/base.py and steps/__init__.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "readfile_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"steps/read_file.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "gencode_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"steps/generate_code.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "writefile_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"steps/write_file.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "executor_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"executor.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "runner_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"runner.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "GenerateCode",
      "config": {
        "input_key": "spec_text",
        "output_key": "main_code",
        "spec": "{\n  \"primary_spec\": \"${spec_text}\",\n  \"target_module\": \"main.py\",\n  \"supporting_context\": [\n    {\"path\": \"docs/IMPLEMENTATION_PHILOSOPHY.md\", \"content\": \"${impl_philosophy}\", \"rationale\": \"These implementation principles must be followed strictly.\"},\n    {\"path\": \"docs/AI_ASSISTANT_GUIDE-general-early-codebase.md\", \"content\": \"${assistant_guide}\", \"rationale\": \"Use these best practices when generating code.\"}\n  ]\n}"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "context_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "logger_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "models_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "utils_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "base_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "readfile_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "gencode_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "writefile_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "executor_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "runner_code",
        "output_root": "new_recipe_executor"
      }
    },
    {
      "type": "WriteFile",
      "config": {
        "input_key": "main_code",
        "output_root": "new_recipe_executor"
      }
    }
  ]
}
```
