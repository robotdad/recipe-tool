# Directory Structure

```
recipe_executor/
├── __init__.py                 # Exports public API
├── main.py                     # Main RecipeExecutor class and CLI
├── constants.py                # Enums and constants
├── models/                     # Data models
│   ├── __init__.py             # Exports models
│   ├── base.py                 # Basic models (RecipeMetadata, etc.)
│   ├── recipe.py               # Recipe model
│   ├── step.py                 # RecipeStep model
│   ├── config/                 # Configuration models
│   │   ├── __init__.py         # Exports configs
│   │   ├── model.py            # ModelConfig
│   │   ├── file.py             # FileInputConfig, FileOutputConfig
│   │   ├── llm.py              # LLMGenerateConfig
│   │   ├── template.py         # TemplateSubstituteConfig
│   │   ├── json.py             # JsonProcessConfig
│   │   ├── python.py           # PythonExecuteConfig
│   │   ├── conditional.py      # ConditionalConfig
│   │   ├── chain.py            # ChainConfig
│   │   ├── parallel.py         # ParallelConfig
│   │   ├── validator.py        # ValidatorConfig
│   │   ├── input.py            # WaitForInputConfig
│   │   └── api.py              # ApiCallConfig
│   ├── execution.py            # ExecutionStatus, StepStatus, RecipeResult
│   ├── events.py               # Event models
│   └── validation.py           # ValidationIssue, ValidationResult
├── context/                    # Execution context
│   ├── __init__.py
│   └── execution_context.py    # ExecutionContext class
├── events/                     # Event system
│   ├── __init__.py
│   ├── event_system.py         # EventListener protocol
│   └── listeners/              # Event listeners
│       ├── __init__.py
│       └── console.py          # ConsoleEventListener
├── executors/                  # Step executors
│   ├── __init__.py             # Exports executor interfaces
│   ├── base.py                 # StepExecutor protocol
│   └── implementations/        # Executor implementations
│       ├── __init__.py         # Exports implementations
│       ├── llm.py              # LLMGenerateExecutor
│       ├── file.py             # FileReadExecutor, FileWriteExecutor
│       ├── template.py         # TemplateSubstituteExecutor
│       ├── json.py             # JsonProcessExecutor
│       ├── python.py           # PythonExecuteExecutor
│       ├── conditional.py      # ConditionalExecutor
│       ├── chain.py            # ChainExecutor
│       ├── parallel.py         # ParallelExecutor
│       ├── validator.py        # ValidatorExecutor
│       ├── input.py            # WaitForInputExecutor
│       └── api.py              # ApiCallExecutor
└── utils/                      # Utility functions
    ├── __init__.py
    ├── validation.py           # Validation utilities
    ├── interpolation.py        # Variable interpolation utilities
    └── parsing.py              # Recipe parsing utilities
```
