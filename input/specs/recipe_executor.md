# Recipe Executor Specification

This document outlines the specifications for the Recipe Executor tool.

## Overview

The Recipe Executor reads a Markdown recipe file containing a list of JSON-defined steps and executes those steps to generate code or perform automated tasks. The implementation is designed to be simple, modular, and leverages Pydantic for data modeling and Pydantic-AI for LLM integration.

## Design Philosophy

- **Simplicity and Clarity:** Follow a minimalistic approach. Each component should do one thing well with as little complexity as possible. Avoid over-engineering or adding features not currently needed.
- **Direct Integration:** Leverage libraries and frameworks directly rather than introducing needless abstraction layers. For example, use Pydantic models and Pydantic-AI's features as intended, instead of wrapping them in custom code.
- **Type-Safe and Explicit:** Use strong typing (via Pydantic) and structured data models to reduce ambiguity. Make configuration and data flow explicit, which also serves as documentation for the system.
- **Emergent Design:** Trust that a clean, simple design will allow more complex capabilities to emerge. Focus on the current end-to-end flow (reading specs, generating code, writing files) and handle future extensions when they become necessary.

## Requirements

- Use **Pydantic** models for all configuration and results to ensure structured data and validation.
- Use **Pydantic-AI** to interact with an LLM, enforcing a structured JSON output format for code generation results.
- Maintain a shared execution context to pass data between steps. Outputs of steps are stored (keyed by an identifier) so that subsequent steps can reference them. This includes supporting placeholders like `${step_id}` in step parameters to inject previous outputs.
- Support the following step types:
  1. **ReadFile** – Read a file’s content into memory (into the context).
  2. **GenerateCode** – Given a specification (from context), invoke an LLM to generate code. The LLM must return JSON with a `files` list (each entry containing `path` and `content`) and an optional `commentary`.
  3. **WriteFile** – Take a list of file specifications and write each to disk under a specified root directory.
- Provide a command-line interface (in `main.py`) to run a recipe, with options for specifying the root output directory and log directory.
- On each run, create fresh log files (`debug.log`, `info.log`, `error.log`) to record execution details in a structured manner (separating info, debug, and error messages).

## Architecture

The tool is organized into the following modules:

- **main.py:** CLI entry point. Uses Python's `argparse` to parse arguments (the recipe file path, optional `--root` for output directory, and optional `--log-dir` for logs). It initializes logging (creating/clearing log files) and then invokes the executor. It also handles any high-level exceptions, ensuring errors are logged to `error.log`.
- **executor.py:** Core execution orchestrator. Responsible for loading the recipe file (a Markdown file with an embedded JSON array of steps), parsing the JSON into Pydantic models, and running each step in sequence. It manages the shared context (e.g., a dictionary mapping step IDs to their outputs) and coordinates logging for each step.
- **steps.py:** Definitions of each step type. Contains a base `Step` interface (with a method like `execute(context)`) and concrete implementations for:
  - `ReadFileStep`: Reads a file and saves its content into the context under a given identifier.
  - `GenerateCodeStep`: Uses a Pydantic-AI LLM model to generate code based on provided specification text (and possibly additional context).
  - `WriteFileStep`: Writes out one or multiple files to the filesystem.
- **models.py:** Pydantic models defining the structure of the recipe and step configurations/results:
  - `Recipe` model – with a list of steps (each step can be a discriminated union of the specific step types).
  - `ReadFileConfig`, `GenerateCodeConfig`, `WriteFileConfig` – configuration models for each step type (fields such as file path, LLM prompt spec, etc.).
  - `CodeGenResult` – model for the output of a GenerateCode step, containing `files: List[FileSpec]` and `commentary: Optional[str]`. (`FileSpec` itself could be a model with `path: str` and `content: str`.)
- **logger.py:** Logging setup. Configures Python logging to output to three log files (info, debug, error). Provides a helper to initialize the log files (clearing old contents at the start of each run) and utility functions or wrappers for logging within steps (so that each step can easily log messages to the appropriate file/level).
- _(Additional modules like `utils.py` can be added if needed for helper functions or parsing.)_

All modules should aim for high readability and testability. For instance, business logic should be separated from I/O where possible to ease unit testing. The use of Pydantic models means that parsing the recipe and validating fields happens automatically, reducing boilerplate.

## Step Details

**ReadFileStep:**

- **Input:** A file path (string).
- **Behavior:** Opens the file (in text mode) and reads its entire content.
- **Output:** Stores the file content (string) into the context, under a key or identifier for later steps to use. Logs success or any file I/O errors.
- _Note:_ In the current design, a single ReadFile step handles one file. To incorporate multiple files, use multiple ReadFile steps (one per file). A potential future enhancement is to allow one ReadFile step to accept a list of paths and read all of them in one go.

**GenerateCodeStep:**

- **Input:** Specification text (usually loaded from context, e.g., the output of one or more ReadFile steps that gathered requirements and context).
- **Output:** A `CodeGenResult` Pydantic object stored in context (containing a list of generated files and optional commentary).
- **Behavior:** Invokes an LLM (e.g. GPT-4 via Pydantic-AI) to generate code according to the specification. A carefully crafted **system prompt** is used to instruct the LLM to return only a structured JSON output. This system prompt should emphasize:
  - The model should produce a JSON object with a `files` key (list of files to create, each with `path` and `content`) and optionally a `commentary` key.
  - The main specification is authoritative, while any additional context provided should guide implementation style or decisions without contradicting the spec.
  - No extraneous text should be included outside the JSON structure.
- The specification content (and any supporting context documents from previous ReadFile steps) is injected into the LLM prompt (for example, as part of the user prompt or in a structured format) so the model has all information needed.
- The LLM's JSON response is parsed and validated against the `CodeGenResult` Pydantic model. If the response is valid and conforms to the schema, execution continues. If validation fails (e.g., the model returned malformed JSON or missing fields), the executor logs an error (to `error.log`) and stops or handles the failure gracefully.
- The `commentary` field in the result (if present) is not used for further automation logic. However, it can be logged (e.g., to a debug log) or presented to the developer for insight into the code generation process.

**WriteFileStep:**

- **Input:** A list of file specifications (each with a path and content) from context, and a target root directory path.
- **Output:** None directly (this step's effect is writing files to disk).
- **Behavior:** Iterates over each file spec in the list:
  - For each file, combines the given root directory with the file's `path`.
  - Creates any necessary subdirectories in the path if they do not exist.
  - Writes the file content to the resolved path, overwriting the file if it already exists.
- Before writing, if the file content string contains any placeholders of the form `${some_id}`, the executor substitutes them with the corresponding content from context (this allows, for example, inserting generated code from a GenerateCode step directly into templates or other files).
- Logs each file written at the debug level (including the file path, and perhaps a truncated portion of content or content size) and logs a summary (total files written, target directory) at the info level.
- If any file write operation fails (e.g., due to permissions or disk issues), logs an error for that file and continues or aborts as appropriate.

## Logging

Logging is split across three files for clarity and granularity:

- `info.log` – High-level messages about the execution flow (e.g., start and end of each step, summary of results).
- `debug.log` – Detailed information useful for debugging (e.g., content of context entries, detailed step-by-step progress, internal state). This may include sanitized or truncated versions of large data to keep log size reasonable.
- `error.log` – Any errors or exceptions encountered during execution (with tracebacks or error details).
- All log files are re-initialized (cleared) at the start of each run to ensure logs are fresh for that execution.
- Log entries should ideally include identifiers or context about which step is being executed (for example, logging the step `id` or type in each message) to make tracing easier.
- Include timestamps on each log entry (to help sequence events when reviewing logs).

## Example

Consider a simple example recipe that produces a "Hello World" program. The recipe might have steps to read a specification file (containing the requirement for a Hello World script), pass that spec to a GenerateCode step, and then write out the resulting file. After running the Recipe Executor on this recipe, the output would be a new file (e.g., `hello.py`) with the program code, and the log files would record each step's execution details.
