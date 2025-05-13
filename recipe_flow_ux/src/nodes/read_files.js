/**
 * Register a 'read_files' node: two fields for path and content_key.
 * @param {Drawflow} editor
 */
export function registerReadFiles(editor) {
  // Register Read Files node: Path and Key inputs
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Read Files</div>
    <label>Path</label><input type="text" df-path />
    <label>Key</label><input type="text" df-content_key />
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('read_files', html);
}