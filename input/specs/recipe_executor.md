# Updated Recipe Executor Specification

## Overview

The Recipe Executor is a CLI tool that reads a _recipe_ (a Markdown file containing a JSON array of steps) and executes those steps in sequence to automate code generation tasks. It is designed to be simple and modular, using **Pydantic** for structured data models and **Pydantic-AI** for LLM integration. The typical flow involves reading input files or specs, invoking an LLM to generate code, and writing output files, all coordinated through a shared execution context.

## Design Philosophy

- **Simplicity and Clarity:** Follow a minimalistic approach (KISS/Occam’s Razor). Each component should do one thing well with as little complexity as possible. Avoid over-engineering or adding features not currently needed.
- **Direct Integration:** Leverage libraries and frameworks directly rather than introducing needless abstraction layers. For example, use Pydantic models and Pydantic-AI’s features as intended, instead of wrapping them in custom code.
- **Type-Safe and Explicit:** Use strong typing (via Pydantic models and dataclasses) to enforce structure. All configurations and results are well-defined, reducing ambiguity. Make data flow explicit – the code should clearly document how information moves through the system.
- **Emergent Design:** Focus on the current end-to-end functionality (reading specs, generating code, writing files). Trust that a clean, simple design will allow more complex capabilities to emerge naturally. Do not implement speculative features; handle future requirements when they actually arise.

## Requirements

- Use **Pydantic** models for all step configurations and results to ensure structured data and validation of inputs/outputs.
- Use **Pydantic-AI** (LLM integration) to strictly enforce a JSON output format for generated code. The LLM’s response must be a JSON object with a list of files and optional commentary, and it should contain no extraneous text.
- Maintain a shared execution context (e.g. a dictionary or object) to pass data between steps. Each step’s output is stored in the context under a key, so subsequent steps can reference it. Support placeholders like `${step_id}` or Liquid template variables in step configurations to inject values from prior outputs.
- Support the following step types:
  1. **ReadFile** – Read a file’s content from disk into the context (under a specified key).
  2. **GenerateCode** – Use an LLM to generate code based on a given specification (taken from the context). The LLM returns a JSON with `files` (each with a `path` and `content`) and an optional `commentary`.
  3. **WriteFile** – Write a list of file specifications to the filesystem (under a target output directory), creating directories as needed.
- Provide a command-line interface (in **`main.py`**) to run a recipe. The CLI should accept the recipe file path and optional `--root` output directory and `--log-dir` for logs.
- Each run should produce fresh log files (`debug.log`, `info.log`, `error.log`) in a log directory, separating detailed debug information, high-level info, and error messages respectively.

## Architecture and Components

The tool is organized into a set of clearly defined modules:

- **main.py:** CLI entry point. Uses Python’s `argparse` to parse command-line arguments (the recipe file path, optional `--root` output directory, and optional `--log-dir` for logs). It initializes the logging system (creating/clearing log files) and then delegates to the runner/executor to execute the recipe. It should catch any top-level exceptions and ensure errors are logged to `error.log` before exiting.
- **runner.py:** High-level orchestration module (invoked by main). It sets up the execution **Context** (populating `input_root` and `output_root` from CLI args), loads and parses the recipe file, and then initializes the Executor. It is responsible for injecting any CLI-provided context variables and starting the execution process. This separation keeps CLI concerns (argument parsing) distinct from the core execution logic.
- **executor.py:** Core execution orchestrator. Defines an `Executor` class that takes a parsed **Recipe** and a **Context**, and runs each step in order. The Executor manages the shared context (e.g. a mapping from step identifiers to outputs) and coordinates logging for each step. It iterates through the recipe’s steps, uses the step type to instantiate the appropriate Step object, executes it, and handles any exceptions (logging errors and halting execution if necessary).
- **context.py:** Defines a `Context` dataclass or similar structure to hold execution context. It includes at least `input_root` (base directory for input files) and `output_root` (base directory for output files), plus an internal dictionary for any extra values produced during execution. It provides dictionary-like access (e.g. `context['key']`) to stored values and may offer convenience methods for updating or retrieving context data. This centralized context is passed to each step’s execute method.
- **models.py:** Pydantic models defining the structure of recipes, step configurations, and generated results:
  - A **Recipe** model that contains a list of steps. This can be implemented as a list of a generic step type, or as a discriminated union of specific step config models.
  - **ReadFileConfig**, **GenerateCodeConfig**, **WriteFileConfig** – Pydantic models for the configuration of each step type (e.g. file paths, keys, LLM prompt specs).
  - **FileSpec** – model with `path: str` and `content: str` for a generated file.
  - **CodeGenResult** – model for the output of a GenerateCode step, with a list of `FileSpec` objects in `files` and an optional `commentary: str`.
- **logger.py:** Logging setup module. Configures Python’s logging to use multiple handlers/files. It initializes three log files (`info.log`, `debug.log`, `error.log`) in a given log directory (creating or clearing them at the start of each run). Each log file captures different log levels (e.g. info-level messages to info.log, debug-level to debug.log, errors to error.log). The logger module provides an `init_logger(log_dir)` function to set this up and return a logger instance that the rest of the tool uses. All log messages from steps and executor go through this logger. Logging format includes timestamps and log levels to aid debugging.
- **steps/** (package): Contains the implementations of each step type, as well as a base class and registration mechanism:
  - **base.py:** Defines the abstract base `Step` class (with an interface `execute(context)` that each concrete step must implement). Also provides a decorator (e.g. `@register_step`) to register step classes in a global **STEP_REGISTRY**. The registry maps a step type identifier (string) to a tuple of (StepClass, ConfigModel). This is used to dynamically instantiate steps from the recipe data.
  - \***\*init**.py:\*\* Initializes the step package. It imports or registers all concrete step classes (ensuring they are added to the registry) and exposes a helper function `get_step_instance(step_type: str, config: dict, logger)`. This function looks up the `step_type` in the registry, parses the raw config dict into the corresponding Pydantic config model, and returns an instance of the appropriate Step subclass (initialized with the config and logger). This abstraction decouples the Executor from specific step classes.
  - **read_file.py:** Implementation of **ReadFileStep**. Reads a text file from disk and stores its content in the context.
  - **generate_code.py:** Implementation of **GenerateCodeStep**. Uses a Pydantic-AI agent (LLM model) to generate code according to a specification and context, returning a structured result.
  - **write_file.py:** Implementation of **WriteFileStep**. Writes out files to disk under the specified output directory.
- **utils.py:** Utility functions and helpers. For example, a `render_template(text: str, context: Context) -> str` helper can be provided to process Liquid-style placeholders in strings using the execution context. This allows dynamic insertion of context values (e.g., using {% raw %}`${...}` or `{{ ... }}`{% endraw %} syntax) into file paths, prompts, or other fields before they are used.

All modules should strive for high readability and separation of concerns. Business logic is separated from I/O where possible to facilitate testing (e.g., generating content vs. writing files). The use of Pydantic for models means input parsing and validation are largely handled by the library, reducing boilerplate and potential errors.

## Step Details

**ReadFileStep (`ReadFile`):**

- **Config Inputs:** A `file_path` (path to the file to read, which may include template variables) and a `store_key` (the context key under which to save the content).
- **Behavior:** When executed, this step opens the specified file (relative to an `input_root` if provided in context, unless an absolute path is given) and reads its entire contents as text. It then stores the file content into the shared context, under the given `store_key`. This allows later steps to retrieve that content by referencing the same key. Logging should record the action (e.g. file opened, success or failure). In case of an error (file not found, permission denied, etc.), it logs an error message and raises an exception to halt the recipe (unless error handling is implemented to continue).
- **Output:** The file’s content (string) is added to the context (e.g. `context[store_key] = "<file contents>"`). No direct return value.

_Note:_ In this design, each ReadFile step handles a single file. If multiple files are needed, the recipe can include multiple ReadFile steps. (A future enhancement could allow a list of files in one step, but that is not required now.)

**GenerateCodeStep (`GenerateCode`):**

- **Config Inputs:** An `input_key` (which refers to a key in context containing the specification/prompt text), and an `output_key` (the key under which the generated code result will be stored). Additionally, a `spec` field is used to provide the LLM prompt template – this is typically a JSON string incorporating the primary specification and possibly other context or instructions.
- **Behavior:** When executed, this step will retrieve the specification text from the context using `input_key` (e.g., it might have been placed there by a ReadFile step). It then renders the `spec` template, substituting any placeholders with actual values from the context (using the `render_template` utility and Liquid syntax). The rendered specification (a prompt in JSON format) is sent to the LLM via the Pydantic-AI `Agent`. A carefully crafted system prompt is used when initializing the Agent to ensure the LLM responds with the expected JSON structure and nothing else. The LLM is invoked (e.g. `agent.run_sync(rendered_spec)`), and we await a result.
- **Output:** The LLM’s response is parsed by Pydantic-AI into a `CodeGenResult` object (thanks to the `result_type=CodeGenResult` enforcement). The step validates that this result conforms to the schema (e.g. it has `files` list). If valid, the `CodeGenResult` object is stored in the context under the given `output_key`. If the LLM returns malformed JSON or missing data (validation fails), the step logs an error and raises an exception to halt execution (or could attempt a retry or graceful failure). On successful completion, a log entry is made to indicate code generation succeeded (and possibly debug-log the generated files or any commentary).
- **Note on Prompt Content:** The specification passed to the LLM typically includes the primary requirements or spec (from the context) and may include additional context or guidelines. The system prompt for the LLM emphasizes that the output must be a JSON with `files` and optional `commentary` only – no extra prose. The model should treat the spec as authoritative for what code to generate, using supporting context (like architecture or style guidelines) to inform the implementation style. The `commentary` field in the result, if present, is not used by the automation logic but can be logged or reviewed by developers to understand the AI’s reasoning.

**WriteFileStep (`WriteFile`):**

- **Config Inputs:** An `input_key` (referring to a context key that holds a `CodeGenResult` or similar list of files) and an `output_root` (base directory path where files should be written; if not provided, the context’s `output_root` is used).
- **Behavior:** When executed, this step retrieves the file list from the context (using `input_key`). It then iterates over each file specification in that list. For each file, it determines the output path by joining the `output_root` directory with the file’s relative `path`. Any necessary subdirectories are created. Before writing, it can perform template substitution on the file content or filename if placeholders are present (e.g., if the file content contains `${some_key}`, those are replaced with corresponding context values – this allows generated code from one step to be inserted into templates in another, if needed). Then it writes the content to the target file, overwriting if the file already exists. Each successfully written file is logged (at least at the debug level, including the path, and possibly a snippet or size of content for verification).
- **Output:** This step’s primary effect is side-effecting – writing files to the filesystem. It doesn’t add new context entries (though it could report a summary). After writing all files, it logs an info-level summary (e.g. “N files written to [output_root]”). If any file write fails (due to permission, disk error, etc.), it logs an error and raises an exception or stops accordingly.

## Logging

The Recipe Executor uses a structured logging approach with multiple log files to separate concerns:

- **info.log** – High-level flow messages. This includes the start and end of each step, major actions taken, and a final summary of the execution. It gives an overview of what happened during the run (suitable for understanding the sequence of steps and outcomes).
- **debug.log** – Detailed debug information. This file captures internal state details useful for diagnosing issues. For example, it may log the exact context data, the rendered prompts sent to the LLM, or the content of files being read/written (possibly truncated if very large). It’s meant for developers to trace through the execution in detail.
- **error.log** – Error and exception messages. Any errors encountered during execution (exceptions thrown by steps, validation failures, etc.) are logged here, along with stack traces or additional info if available. It provides a clear record of what went wrong if the recipe fails or if any step encounters an issue.

On each run, the log files are initialized (old content cleared) so that logs are fresh for that execution. All log entries include a timestamp and severity level, and typically include some context about which step or component is logging the message (for easier traceability). For example, steps might prefix messages with the step identifier or type. This logging setup allows users to inspect different levels of output: a quick look at info.log for a summary, debug.log for full details, and error.log for any problems.
