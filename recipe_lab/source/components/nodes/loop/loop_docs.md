# Loop Node

The Loop Node component registers a Drawflow node named `loop` that enables users to configure and execute loop iterations over a collection directly in the Drawflow flow editor. You can customize the source of items, control concurrency and delay, define substeps to perform on each item, and gather results (or errors) under a specified key.

---

## Installation & Import

First, ensure you have Drawflow installed and your editor instance running. Then import and register the Loop Node:

```js
import Drawflow from 'drawflow';
import { registerLoop } from 'src/nodes/loop.js';

const editor = new Drawflow('#drawflow');
editor.start();

// After editor.start(), register the Loop node
registerLoop(editor);
```

---

## Adding a Loop Node

Once registered, the Loop node will appear in your node palette (icon: `fa-repeat`, label: **Loop**). Drag it onto the canvas and connect its **control input** and **control output** ports to other nodes.

```mermaid
sequenceDiagram
    actor User
    participant App
    participant Editor
    participant LoopNode  as Loop
    User->>App: import & start editor
    App->>LoopNode: registerLoop(editor)
    User->>Editor: add Loop node to canvas
    Editor->>LoopNode: onCreate(node)
    LoopNode->>Loop: initialize form fields from config
    User->>Loop: update form inputs
    Loop->>Editor: updateNodeDataFromId(node.id, node.data)
    Editor->>App: export() includes node.data.config
``` 

*Figure: High-level sequence of registering, creating, configuring, and exporting the Loop node.*

---

## Ports

- **Control Input**: Triggers the loop execution when a previous node finishes.
- **Control Output**: Fires once all iterations (and substeps) complete (or abort if `fail_fast=true`).

Drawflow will render one `.input` port on the left and one `.output` port on the right automatically.

---

## Configuration Options

| Field            | Type                | Default     | Description                                                                         |
|------------------|---------------------|-------------|-------------------------------------------------------------------------------------|
| `items`          | String or JSON      | `""`       | A context key path (e.g., `data.users`) or a JSON array literal (`[1,2,3]`).      |
| `item_key`       | String              | `"item"`  | The variable name for each element in iteration, used by substeps.                |
| `max_concurrency`| Number (1–10)       | `1`         | How many items to process in parallel.                                             |
| `delay`          | Number (0–60)       | `0`         | Delay in seconds between starting each batch.                                       |
| `substeps`       | JSON array          | `[]`        | A JSON array of step definitions, each `{ type: string, config: object }`.         |
| `result_key`     | String              | `"result"`| The key under which to store successful iteration results in the exported context.  |
| `fail_fast`      | Boolean             | `true`      | If `true`, abort on first error and propagate; otherwise collect errors and proceed.|

> **Validation notes:**
> - `items` must parse as a valid JSON array or be treated as a context path.
> - `substeps` must be valid JSON and an array of objects with `type` and `config`.
> - `max_concurrency` is clamped to [1,10]; `delay` to [0,60]. Out-of-range values reset with a warning.

---

## Example: Canvas to Exported JSON

1. User drags in a Loop node, sets:
   - `items`: `["a","b","c"]`
   - `item_key`: `letter`
   - `max_concurrency`: `2`
   - `delay`: `1`
   - `substeps`: `[{"type":"log","config":{"message":"Processing {{letter}}"}}]`
   - `result_key`: `letters`
   - `fail_fast`: `false`

2. On export (`editor.export()`), the node appears as:

```json
{
  "id": "7",
  "name": "Loop",
  "data": {
    "config": {
      "items": "[\"a\",\"b\",\"c\"]",
      "item_key": "letter",
      "max_concurrency": 2,
      "delay": 1,
      "substeps": [
        { "type": "log", "config": { "message": "Processing {{letter}}" } }
      ],
      "result_key": "letters",
      "fail_fast": false
    }
  },
  "ports": { "inputs": 1, "outputs": 1 }
}
```

*Your flow runner can then read `data.config` to perform the loop at runtime.*

---

## Integration Tips

- Always call `registerLoop(editor)` **after** `editor.start()`.
- Use Drawflow’s `df-*` attributes to style and bind controls automatically.
- You can connect any node type inside a Loop’s `substeps`; they will receive `{ item_key: currentItem }` in context.

---

## Important Notes & Warnings

- Invalid JSON in **substeps** or **items** will show an inline error and prevent saving until fixed.
- Exceeding numeric bounds for `max_concurrency` or `delay` resets to defaults (1 and 0) with a warning.
- Setting `fail_fast=false` collects errors under `"<result_key>__errors"` instead of stopping.

---

## Further Reading

- **Drawflow docs** for general node creation and df-* bindings: https://github.com/danielstockton/Drawflow
- **Flow runner integration** for consuming `data.config` and executing substeps.