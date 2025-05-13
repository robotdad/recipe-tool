/**
 * Setup toolbox buttons for adding nodes and import/export functionality.
 * @param {Drawflow} editor
 * @param {object} opts - IDs for buttons and textarea
 */
import { drawflowToRecipe, recipeToDrawflow } from '../modules/serialization.js';
/**
 * Setup toolbox buttons for adding nodes and import/export functionality.
 * Exports and imports recipes in JSON format (with `steps` array).
 * @param {Drawflow} editor
 * @param {object} opts - IDs for buttons and textarea
 */
export function setupToolbox(editor, opts) {
  // Add Read Files node
  document.getElementById('add-read-files').addEventListener('click', () => {
    editor.addNode('read_files', 1, 1, 50, 50, 'node', {}, 'read_files', true);
  });
  // Add LLM Generate node
  document.getElementById('add-llm-generate').addEventListener('click', () => {
    editor.addNode('llm_generate', 1, 1, 200, 50, 'node', {}, 'llm_generate', true);
  });
  // Add Set Context node
  document.getElementById('add-set-context').addEventListener('click', () => {
    editor.addNode('set_context', 1, 1, 50, 200, 'node', {}, 'set_context', true);
  });
  // Add Write Files node
  document.getElementById('add-write-files').addEventListener('click', () => {
    editor.addNode('write_files', 1, 1, 200, 200, 'node', {}, 'write_files', true);
  });
  // Add Execute Recipe node
  document.getElementById('add-execute-recipe').addEventListener('click', () => {
    editor.addNode('execute_recipe', 1, 1, 50, 350, 'node', {}, 'execute_recipe', true);
  });
  // Add Conditional node
  document.getElementById('add-conditional').addEventListener('click', () => {
    editor.addNode('conditional', 1, 3, 200, 350, 'node', {}, 'conditional', true);
  });
  // Add Loop node
  document.getElementById('add-loop').addEventListener('click', () => {
    editor.addNode('loop', 1, 2, 50, 500, 'node', {}, 'loop', true);
  });
  // Add Parallel node
  document.getElementById('add-parallel').addEventListener('click', () => {
    editor.addNode('parallel', 1, 2, 200, 500, 'node', {}, 'parallel', true);
  });
  // Add MCP Call node
  document.getElementById('add-mcp').addEventListener('click', () => {
    editor.addNode('mcp', 1, 1, 50, 650, 'node', {}, 'mcp', true);
  });

  const exportBtn = document.getElementById(opts.exportBtnId);
  const textarea = document.getElementById(opts.textareaId);
  // Export recipe JSON
  exportBtn.addEventListener('click', () => {
    const flow = editor.export();
    const recipe = drawflowToRecipe(flow);
    textarea.value = JSON.stringify(recipe, null, 2);
  });

  const importBtn = document.getElementById(opts.importBtnId);
  const importFile = document.getElementById(opts.importFileId);
  importBtn.addEventListener('click', () => importFile.click());
  // Import recipe JSON
  importFile.addEventListener('change', () => {
    const file = importFile.files[0];
    if (!file) return;
    const reader = new FileReader();
      reader.onload = e => {
        try {
          const recipe = JSON.parse(e.target.result);
        // Clear existing canvas
        editor.clear();
        // Add each step as a node, then auto-connect sequentially
        const nodeIds = [];
        const startX = 50, startY = 50, dx = 220, dy = 200;
        recipe.steps.forEach((step, idx) => {
          const x = startX + (idx % 5) * dx;
          const y = startY + Math.floor(idx / 5) * dy;
          // Add node: 1 input, 1 output
          const id = editor.addNode(
            step.type,
            1, 1,
            x, y,
            'node',
            step.config || {},
            step.type,
            true
          );
          nodeIds.push(id);
        });
        // Connect each node's output to next node's input
        for (let i = 0; i + 1 < nodeIds.length; i++) {
          const from = nodeIds[i];
          const to = nodeIds[i + 1];
          try {
            editor.addConnection(from, to, 'output_1', 'input_1');
          } catch (err) {
            console.warn('Auto-connect failed for', from, to, err);
          }
        }
          textarea.value = JSON.stringify(recipe, null, 2);
        } catch (err) {
          console.error('Import error:', err);
          alert('Failed to import recipe JSON');
        }
      };
    reader.readAsText(file);
  });
}