/**
 * Register a 'parallel' node: substeps, max_concurrency, delay.
 * @param {Drawflow} editor
 */
export function registerParallel(editor) {
  // Register Parallel node: substeps, max_concurrency, delay
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Parallel</div>
    <label>Max Concurrency</label><input type="number" df-max_concurrency />
    <label>Delay (s)</label><input type="number" step="0.1" df-delay />
    <div class="port-label">Substeps →</div>
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('parallel', html);
}