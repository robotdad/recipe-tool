 # Document Generator App - Initial Plan

 ## 0. Current Status
 The following have been implemented and validated:
 - [x] Models brick (`models/outline.py`): Resource, Section, Outline dataclasses with `to_dict`/`from_dict` (tests)
 - [x] Schema brick (`schema/outline_schema.json`, `validator.py`): JSON Schema with `merge_mode` optional, validation utilities (tests)
 - [x] Executor brick (`executor/runner.py`): `generate_document` wired to recipe executor for headless usage
 - [x] CLI brick (`cli/main.py`, `__main__.py`): Typer-based CLI to run generation from an outline file (tests)
 - [x] Validator UI brick (`ui/editor.py`): minimal Gradio interface for outline validation (tests)
 - [x] Updated dependencies: added `jsonschema`, `typer`, `python-dotenv` as required
 - [x] Blocks-based editor UI (`ui/editor.py`): metadata textboxes, resources DataFrame, flat sections DataFrame, with upload, validate, download, and generate actions
 - [x] Comprehensive test suite under `tests/` covers models, schema, CLI, UI, and executor stubs

 ## 1. Purpose

 This document outlines the current functionality and intended behavior of the Document Generator App, and proposes a clear plan for refining and extending it.

 ## 1. Purpose
 Provide a web-based editor and generator for structured documents using:
 - An outline (title, general instructions, resources, sections), initialized blank or via upload
 - External resources (files or URLs)
 - A headless recipe defined in `recipes/document_generator/document-generator-recipe.json`

 ## 2. Desired Functionality
 1. Start with a blank outline:
    - Empty metadata (title, general instruction)
    - No resources or sections by default
 2. Render an enhanced Gradio Blocks editor:
    - Metadata inputs: title textbox, general instruction textarea
    - Dynamic Resources list:
      - Add/remove resource entries
      - Each entry includes key, description, path/URL or file upload, merge_mode selector
    - Dynamic Sections list:
      - Add/remove top-level sections and nested subsections (infinite nesting)
      - Each section has two modes:
        1. **Prompt Mode**: enter title, prompt textarea, refs picker (choices ← current resource keys)
        2. **Static Resource Mode**: enter title, select a single `resource_key` from the resource list
      - User toggles between modes per section; only the relevant inputs are shown
    - Upload Outline JSON button:
      - Validates against the outline schema (extra properties ignored)
      - Parses and populates editor state dynamically
    - Download Outline JSON button:
      - Exports the current outline state without running generation
    - Generate button:
      - Executes the recipe and displays output
 3. On Generate:
    - Serialize the current outline state
    - Normalize resource paths (download URLs or resolve local)
    - Write a temporary outline.json
    - Invoke the recipe via Executor
    - Read and display the generated Markdown
    - Offer downloads for the final outline JSON and generated document

 ## 3. High-Level Workflow
 1. **Startup**: `main.py` initializes a blank outline and launches the Gradio editor.
 2. **User Interaction**:
    - User enters metadata, adds resources and sections dynamically.
    - User can upload an outline JSON to pre-populate the editor.
 3. **Generation**:
    - Serialize the current editor state into an `Outline` structure.
    - Invoke `generate_document` to run the recipe and retrieve Markdown output.
    - Display the document and provide download links.

 ## 4. Data Model
 - **Resource**: key, path or URL, description, merge_mode ("concat" or "dict")
 - **Section**:
  - title: string
  - prompt: string (optional, when in Prompt Mode)
  - refs: list of resource keys (optional, when in Prompt Mode)
  - resource_key: string (optional, when in Static Resource Mode)
  - sections: list of nested Section objects (supports infinite nesting)
 - **Outline**: title, general_instruction, list of resources, list of sections

 ## 5. UI Layout
 - **Upload Outline JSON**: load and populate editor
 - **Download Outline JSON**: export current outline state
 - **Metadata**: Title (Textbox), General Instruction (Textarea)
 - **Resources**: Accordion per resource (key, description, path/URL or file upload, merge_mode selector)
 - **Sections**: Recursive accordions per section (Prompt/Static modes, nested subsections)
 - **Generate**: Button to run the recipe and display output
 - **Download Generated Document**: button shown after generation

 ## 6. Integration Points
 - **recipe-tool**: uses `recipe_executor.Executor` to run the document-generator recipe
 - **Gradio**: rendering interactive UI components

 ## 7. File Structure
 ```
 apps/document-generator/
 ├── document_generator/   # application code (main.py)
 ├── output/               # sample outputs (OUTLINE.md)
 ├── README.md             # usage instructions
 ├── Makefile              # development tasks (install, test, format)
 ├── pyproject.toml        # packaging and dependencies
 ├── pytest.log            # previous test logs
 ├── uv.lock               # editable dependency lock file
 └── PLAN.md               # this implementation plan
 ```

## 8. Open Questions
 - How should we implement drag & drop reordering for resources and sections?
 - How should errors or progress be reported in the UI (e.g., a log or progress panel)?
 - Do we need live streaming of LLM-generated content in the editor as it arrives?
 - Are any additional merge modes needed beyond "concat" and "dict"?
 - What outline schema validations are required, and should extra properties be ignored?

 ## 9. Next Steps
 1. Review and refine this plan with stakeholders.
 2. Define schema validations and UI constraints.
 3. Implement detailed UI improvements and error handling:
    - Replace sections JSON placeholder with a full Blocks-based section editor (add/remove nested sections, Prompt vs Static Resource modes, refs linked to resource keys)
    - Ensure generate button is disabled until minimum schema requirements are met (e.g., at least one section)
 4. Add tests for core functions (`outline_from_dict`, `generate_document`) and editor components.
 5. Iterate on user experience and deployment.
 6. Sketch and prototype a two-column UI layout with a log/progress panel for generation steps.
 7. Plan for CLI support: accept an outline file and run generation headlessly.
 8. Design a configuration panel/menu for selecting models, environment variables, and advanced settings.
 
## 10. Proposed Modular Architecture
To align with our Implementation and Modular Design philosophies, the app will be organized into self-contained "bricks" with clear contracts. Each brick holds code, tests, and schema (if needed) within its directory.

apps/document-generator/
  document_generator/         # Top-level Python package
    models/                   # Data models and serialization
      outline.py              # Resource, Section, Outline dataclasses and to/from dict
    schema/                   # JSON Schema definitions and validator
      outline_schema.json     # Outline JSON Schema (ignores extra props)
      validator.py            # Schema validation utilities
    ui/                       # Gradio UI bricks
      editor.py               # Constructs the Blocks editor from models
      components.py           # Reusable UI components (resource entry, section entry)
    executor/                 # Headless generation brick
      runner.py               # generate_document logic + recipe invocation
    cli/                      # Command-line interface brick
      main.py                 # CLI entrypoint for headless use cases
    config/                   # Configuration brick for models/env settings
      settings.py             # Load and manage user-configurable settings
  tests/                      # Parallel test bricks for each module
    models/                   # test_outline.py, etc.
    schema/                   # test_validator.py
    ui/                       # test_editor.py, test_components.py
    executor/                 # test_runner.py
    cli/                      # test_cli.py
    config/                   # test_settings.py

Each brick has its own sub-directory and tests. This structure supports isolated development, easy regeneration or replacement of any brick, and clear contracts (studs & sockets) between modules.