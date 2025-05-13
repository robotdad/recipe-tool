/**
 * Register a 'set_context' node: key, value, nested_render, if_exists.
 * @param {Drawflow} editor
 */
export function registerSetContext(editor) {
  // Register Set Context node: key, value, nested_render, if_exists
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Set Context</div>
    <label>Key</label><input type="text" df-key />
    <label>Value</label><textarea df-value></textarea>
    <label>Nested Render</label><input type="checkbox" df-nested_render />
    <label>If Exists</label>
    <select df-if_exists>
      <option value="overwrite">overwrite</option>
      <option value="merge">merge</option>
    </select>
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('set_context', html);
}