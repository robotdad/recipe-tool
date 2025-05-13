import { createCanvas } from './core/canvas.js';
import { registerReadFiles } from './nodes/read_files.js';
import { registerLlmGenerate } from './nodes/llm_generate.js';
import { registerSetContext } from './nodes/set_context.js';
import { registerWriteFiles } from './nodes/write_files.js';
import { registerExecuteRecipe } from './nodes/execute_recipe.js';
import { registerConditional } from './nodes/conditional.js';
import { registerLoop } from './nodes/loop.js';
import { registerParallel } from './nodes/parallel.js';
import { registerMcp } from './nodes/mcp.js';
import { setupToolbox } from './ui/toolbox_shell.js';

// Initialize Drawflow editor
const container = document.getElementById('drawflow');
const editor = createCanvas(container);

// Register node types
registerReadFiles(editor);
registerLlmGenerate(editor);
registerSetContext(editor);
registerWriteFiles(editor);
registerExecuteRecipe(editor);
registerConditional(editor);
registerLoop(editor);
registerParallel(editor);
registerMcp(editor);

// Setup toolbox UI for adding nodes and import/export
setupToolbox(editor, {
  exportBtnId: 'export-btn',
  importBtnId: 'import-btn',
  importFileId: 'import-file',
  textareaId: 'flow-json'
});

// Generic binding for df-* attributes: sync node.data with input elements
editor.on('nodeCreated', (id) => {
  const nodeEl = document.getElementById('node-' + id);
  if (!nodeEl) return;
  const content = nodeEl.querySelector('.drawflow_content');
  if (!content) return;
  // Fetch config object for this node
  const mod = editor.drawflow.drawflow[editor.module];
  const nodeData = mod && mod.data && mod.data[id] && mod.data[id].data;
  if (!nodeData) return;
  // Bind all elements with df- attributes
  content.querySelectorAll('*').forEach((el) => {
    Array.from(el.attributes).forEach((attr) => {
      if (attr.name.startsWith('df-')) {
        const prop = attr.name.slice(3);
        // Initialize value
        let val = nodeData[prop];
        if (el.tagName === 'INPUT') {
          if (el.type === 'checkbox') {
            el.checked = !!val;
            el.addEventListener('change', () => { nodeData[prop] = el.checked; });
          } else if (el.type === 'number') {
            el.value = val != null ? val : '';
            el.addEventListener('input', () => { nodeData[prop] = parseFloat(el.value) || 0; });
          } else {
            el.value = val != null ? val : '';
            el.addEventListener('input', () => { nodeData[prop] = el.value; });
          }
        } else if (el.tagName === 'TEXTAREA') {
          el.value = val != null && typeof val !== 'string' ? JSON.stringify(val, null, 2) : (val != null ? val : '');
          el.addEventListener('input', () => {
            try { nodeData[prop] = JSON.parse(el.value); }
            catch { nodeData[prop] = el.value; }
          });
        } else if (el.tagName === 'SELECT') {
          el.value = val != null ? val : '';
          el.addEventListener('change', () => { nodeData[prop] = el.value; });
        }
      }
    });
  });
});