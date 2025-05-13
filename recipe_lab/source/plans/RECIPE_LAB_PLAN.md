# Recipe Lab Implementation Plan

This document outlines a modular, iterative plan for building an interactive UX to create and modify recipe files for the recipe-executor library. It follows the project’s Implementation and Modular Design philosophies: start minimal, deliver vertical slices, and evolve incrementally.

## 1. Project Overview

**What we’re building:**
A minimal, web-embeddable flow-editor UI for composing “recipe” scripts. Users drag‐drop blocks that map to your existing step types (read_files, llm_generate, etc.), configure each block, and save/load the recipe as JSON. The UI lives in plain HTML/ES modules, wraps Drawflow for the canvas, and delegates execution/storage to your backend.

**Key principles:**

- **Pure ES modules & plain JS:** No frameworks (React/TS)
- **Modular folders:** One module per concern (canvas, nodes, UI shell, serialization, integrations)&#x20;
- **Vertical slices:** Deliver end-to-end MVP first, then layer on chat assistant, storage, and execution panels&#x20;
- **JSON round-trip:** Drawflow JSON ↔ recipe DSL via two pure functions

Based on our components manifest in `components.json` , we’ll build:

```
/src
  /core
    canvas.js
  /nodes
    read_files.js
    llm_generate.js
    set_context.js
    conditional.js
    loop.js
    parallel.js
    execute_recipe.js
    mcp.js
  /modules
    serialization.js
  /ui
    toolbox_shell.js
    chat_assistant_panel.js
  /integration
    storage_service.js
    execution_service.js
index.html
```

---

## 2. Module Breakdown & Responsibilities

### 2.1 `/core/canvas.js`

- **Exports:** `createCanvas(containerEl: HTMLElement) → DrawflowInstance`
- **Does:**

  - `import Drawflow from 'drawflow'`
  - `const editor = new Drawflow(el); editor.start()`
  - Return `editor` to caller

**Deliverable:** Plain ES module, no UI, just starts Drawflow on a `<div>`.

---

### 2.2 `/nodes/*.js` (one per step type)

Each file registers one Drawflow node type:

```js
// example: read_files.js
export function registerReadFiles(editor) {
  editor.registerNode("read_files", {
    html: `
      <div class="node">
        <label>Path</label><input df-path />
        <label>Key</label><input df-content_key />
      </div>`,
    onCreate(node) {
      // bind each <input df-*> to node.data.config.*
    },
  });
}
```

- **Exports:** `registerX(editor)`
- **Tasks:**

  - Define the HTML form for the node’s config
  - Wire `df-*` attributes to `node.data.config` on creation/update

- **Test:** Drag each node into the canvas and inspect `editor.export()` JSON

---

### 2.3 `/modules/serialization.js`

- **Exports:**

  ```js
  export function recipeToDrawflow(recipeJson) { … }
  export function drawflowToRecipe(flowJson) { … }
  ```

- **Does:**

  - Strip Drawflow layout metadata
  - Map each node’s `name` + `data.config` ↔ `{ type, config }` in `steps[]`

- **Test:** Unit-test round-trip on sample recipes

---

### 2.4 `/ui/toolbox_shell.js`

- **Mount point:** HTML layout in `index.html`:

  ```html
  <div id="toolbox"></div>
  <div id="drawflow"></div>
  <div id="sidebar"></div>
  ```

- **Responsibilities:**

  - Render a palette of buttons for each node: on click, `editor.addNode(type, …)`
  - Render Import/Export buttons:

    - **Import**: file-picker → JSON → `editor.import(flowJson)`
    - **Export**: `const flow = editor.export()` → show in `<textarea>`

- **Test:** Verify adding nodes and import/export round-trip

---

### 2.5 `/ui/chat_assistant_panel.js`

- **Mount point:** part of `#sidebar`
- **Responsibilities:**

  - Simple chat UI (prompt input + send button)
  - On submit: POST user message to your LLM endpoint → get response
  - Optionally call `editor.addNode('llm_generate', …)` or `editor.updateNode(nodeId, …)`

- **Test:** Chat → ensure nodes appear or update correctly

---

### 2.6 `/integration/storage_service.js`

- **Exports:**

  ```js
  export function saveFlow(id, flowJson) { … }
  export function loadFlow(id) { … }
  ```

- **Implementation:** `fetch('/api/flows/'+id, { method: 'PUT', body: JSON.stringify(flowJson) })` etc.
- **Test:** Save a flow, reload page, load by ID, verify canvas state

---

### 2.7 `/integration/execution_service.js`

- **Exports:**

  ```js
  export function runRecipe(flowJson) { … }
  ```

- **Implementation:** `fetch('/api/execute', { method: 'POST', body: … })`
- **Test:** Execute saved flow, stream or display results in sidebar

---

## 3. Development Roadmap

| Sprint | Deliverables                                                          | Acceptance Criteria                                                               |
| ------ | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **1**  | Canvas core + one node (`read_files`) + Export → console              | Blank grid appears; dragging a Read Files node shows it in `editor.export()` JSON |
| **2**  | Add `llm_generate` node + Import/Export UI + round-trip serialization | Import sample recipe JSON → canvas → Export back to identical JSON                |
| **3**  | All remaining nodes registered + toolbox palette                      | All step types available in palette; configuration persists in JSON               |
| **4**  | Chat assistant panel integrated                                       | Chat input can add or modify an `llm_generate` node                               |
| **5**  | Storage & execution integrations                                      | Save/load flows by ID; Execute flow and display results                           |
| **6**  | Polish, styling, error handling, unit tests for `serialization.js`    | No uncaught JS errors; serialization tests pass; basic CSS for nodes and panels   |

---

## 4. Coding & Testing Guidelines

- **Isolate modules:** One feature per file; import only what you need
- **No global state:** Pass the `editor` instance into each registration or UI module
- **Pure functions:** Serialization should have no side effects
- **Basic styling:** Use scoped CSS classes; avoid large frameworks
- **Error handling:** Validate inputs (e.g., ensure JSON is well-formed before import)
- **Unit tests:** For `serialization.js`, use Jasmine/Mocha in Node or browser

---

## 5. Handoff Checklist

1. **Repository skeleton** with empty module files and `index.html`
2. **This plan document** checked into `/docs/implementation_plan.md`
3. **components.json** in `/src/components.json`&#x20;
4. **NPM dependencies**:

   ```bash
   npm install drawflow
   ```

5. **README** with setup/run instructions:

   ```md
   # Setup

   npm install
   open index.html in browser

   # Dev

   serve . locally (e.g. `npx http-server`)
   ```

Once all sprints complete, you’ll have a fully modular, maintainer-friendly recipe builder UI that meets our “wabi-sabi” simplicity and componentized philosophy.
