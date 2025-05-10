# Document Generator UI: Implementation Plan

This document outlines a modular, iterative plan for building an interactive UX around the existing Document Generator recipe. It follows the project’s Implementation and Modular Design philosophies: start minimal, deliver vertical slices, and evolve incrementally.

## 1. Overview

Create a standalone FastAPI-backed service serving a static HTML/JS SPA. Users can:

- Create, upload, or load an _outline JSON_ describing the document structure and resources.
- Visually edit sections (titles, prompts, resource assignments, nesting).
- Manage reference resources (upload, list, assign to sections).
- Trigger document generation via the existing `recipe_executor` lib, then download the Markdown output.

## 2. Outline JSON Schema

Enhance the existing outline format so it fully captures UI state:

- `title`: string
- `general_instruction`: string
- `resources`: array of `{ key, path, description }`      # `path` used by recipes to read content; UI displays filename via path basename
- `sections`: array of section objects where each section has:
  - `id`: unique string
  - `title`: string
  - `prompt`: string (LLM prompt for this section)
  - `resource_key?`: string (optional key of a resource whose raw `content` field is used directly for this section; not to be confused with `content_key`, which is the name of the field used in recipe steps during file loading)
  - `refs?`: array of strings (optional keys of resources provided as references for LLM-based content generation)
  - `sections`: array of nested sections

All UI-only metadata (e.g. section `id`, upload-only fields) is preserved in the JSON so loading a file fully rehydrates the interface.

## 3. Backend Service (FastAPI)

Create `ui/server/main.py` that implements:

- Static files mount for the SPA (`/` → `ui/static/`).
- Outline endpoints:
  - `GET  /api/outline` → return current outline JSON
  - `POST /api/outline` → save outline JSON
- Resource endpoints:
  - `GET  /api/resources` → return the current `outline.resources` array
  - `POST /api/resource` → upload file multipart; save in `document_generator_ui/uploads` and append `{ key, path, description }` to `outline.json`
  - `DELETE /api/resource/{key}` → delete the file and remove its entry from `outline.json`
- Generation endpoint:
  - `POST /api/run` → invoke the Recipe Executor library directly (no CLI shell-out) using `recipes/document_generator/build.json` with the current outline JSON as input.
  - Stream the full execution log to the client (e.g. via SSE or WebSocket), surface concise status updates in the SPA, but keep the full log accessible in a collapsible panel.
  - After completion (success or failure), return the final execution context (all artifacts) and a download link for the generated `<TITLE>.md`. On error, include error details and the final context to aid debugging.

## 4. Front-end SPA (Vanilla JS)

 Place under `ui/static/`:

- **Outline Tree View**: drag/drop, add/delete/nest sections
- **Section Editor**: form for `title`, `prompt`, `resource_key` (direct content), and `refs` (multi-select reference resources)
- **Resource Manager**: upload, list, delete resources; edit resource descriptions
- **Global Controls**:
  - Create outline
  - Load outline
  - Save outline
  - Generate document → show progress → Download link

All operations talk to the FastAPI API. Client state is in-memory until “Save” or “Generate.”

## 5. Bundling & Distribution

*This section is superseded by v7 in the roadmap (Packaging & Distribution).*  
Refer to v7 under the Iterative Implementation Roadmap for full details.

## 6. Iterative Implementation Roadmap

We will deliver vertical slices with working end-to-end behavior at each stage:

**v0: Static SPA + Serve** (✅ Done)

- Scaffolded FastAPI app serving `index.html` and a “Hello, world” JS console log.
- Created `document_generator_ui/server/main.py` and `document_generator_ui/static/index.html`.
- Mounted static SPA with FastAPI’s `StaticFiles`, serving `index.html` at `/`.
- Added `<script>console.log("Hello, world from Document Generator UI!");</script>` for verification.

**v1: Outline Load/Save**

- Implement `/api/outline` GET/POST.
- In SPA, add “Load” and “Save” buttons that fetch/post JSON and render it raw in a textarea.

**v2: Basic Section Tree**

- Parse outline JSON into a simple collapsible tree.
- Allow adding/removing top-level sections.
- Sync changes back into the in-memory outline.

**v3: Section Editor Form**

- When selecting a section in the tree, display form fields (`title`, `prompt`, `resource_key`).
- Save form updates to outline structure.

**v4: Resource Management & Reference Assignment**

- Implement `/api/resource` endpoints.
- SPA: Upload files, list resources, delete.
- Section Editor: populate both a single-select `resource_key` dropdown (for direct content) and a multi-select `refs` control for reference resources.

**v5: Run & Download**

- Implement `/api/run` to call the Recipe Executor library directly (no CLI shell-out).
- Ensure `recipe_root` context var is passed so sub-recipes resolve correctly (use absolute path or change working directory to project root).
- SPA: “Generate” button streams status and logs, then presents a “Download” link for the generated `.md`.

**v6: Real-time Log Streaming** (Live via SSE/WebSocket)

- Implement an SSE or WebSocket endpoint (`/api/run/logs`) to push recipe executor logs to the client during generation, replacing the current post-mortem log panel.

**v7: Packaging & Distribution**

- Finalize `pyinstaller.spec` (or equivalent) and build instructions.
- Add `pyproject.toml` script entry for `ui.server:app` and `make ui-run`, `make ui-build` targets.
- Validate standalone builds on Windows, macOS, and Linux.

**v8: UX Polish**

- Remove the raw JSON textarea; drive all outline editing via the form controls and tree view.
- Add drag-&-drop support for section reordering and nesting.
- Improve styling, form validation, and mobile responsiveness.

Each version is a complete vertical slice: e.g. v1 should let non-technical users load a JSON and save it back, v2 lets them edit sections, etc. We’ll refactor only when necessary and keep abstractions minimal per the implementation philosophy.
