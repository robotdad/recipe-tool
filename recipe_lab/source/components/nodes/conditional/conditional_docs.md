# Conditional Node

**Drawflow version compatibility:** v1.0+

---

## Overview

The `conditional` node lets you create branching logic in your Drawflow editor. It provides:

- A text input for a boolean expression (the _condition_).
- Two output ports labeled **if-true** and **if-false**.
- Persistence of the condition and branch connections across export/import.

When you register this node, users can drag it into the canvas, enter a condition (e.g., `x > 10`), and connect the corresponding outputs to other nodes based on the condition’s outcome.

---

## Installation & Initialization

1. **Import** the module:

   ```js
   import { registerConditional } from './src/nodes/conditional.js';
   ```

2. **Initialize** your Drawflow editor and register the node type:

   ```js
   const editor = new Drawflow(document.getElementById('drawflow'));  
   registerConditional(editor);
   editor.start();
   ```

Upon registration, you’ll see the `