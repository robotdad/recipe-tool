/**
 * Register a 'loop' node: items, item_key, max_concurrency, delay, fail_fast, substeps, result_key.
 * @param {Drawflow} editor
 */
export function registerLoop(editor) {
  // Register Loop node: items, item_key, max_concurrency, delay, fail_fast, substeps, result_key
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Loop</div>
    <label>Items</label><textarea df-items></textarea>
    <label>Item Key</label><input type="text" df-item_key />
    <label>Max Concurrency</label><input type="number" df-max_concurrency />
    <label>Delay (s)</label><input type="number" step="0.1" df-delay />
    <label>Fail Fast</label><input type="checkbox" df-fail_fast />
    <label>Result Key</label><input type="text" df-result_key />
    <div class="port-label">Substeps →</div>
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('loop', html);
}