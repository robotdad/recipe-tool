# Document Generator UI

This project provides a FastAPI backend and a static single-page application (SPA) frontend for the Document Generator. It is a separate project that builds on the `recipe-tool` library, allowing users to:

- Upload or load an outline JSON file describing the document structure and resources.
- Visually edit document sections (titles, prompts, resource assignments, nesting).
- Manage reference resources (upload, list, assign, remove).
- Trigger generation of the final Markdown document via the Recipe Executor and download the output.

> Note: You must have the **recipe-tool** project installed (e.g., via `pip install -e ../`) so the backend can import and invoke the Recipe Executor.

## Prerequisites
- Python 3.11 or later
- `uv` for virtual environment and package management:
  ```bash
  pip install uv
  ```
- (Optional) Create and activate a virtual environment using `uv`:
  ```bash
  uv venv
  source .venv/bin/activate
  ```

The `recipe-tool` project installed in editable mode (from the root of the recipe-tool repo):
```bash
cd ../
make
```

## Installation

Install this project and its dependencies in editable mode using `uv`:

```bash
# From within the document_generator_ui directory
uv pip install -e .
```

## Run the Server

Launch the FastAPI backend and serve the SPA using `uv`:

```bash
# From within document_generator_ui/
uv run uvicorn server.main:app --reload
```

Open your browser to:

```
http://127.0.0.1:8000
```

In the browser console, you should see:

```
Document Generator UI loaded (v1)
```

This version (v1) supports loading and saving outline JSON via the API. Use the buttons in the UI to fetch and persist your outline. Later versions will add visual editing, resource management, and recipe execution.
