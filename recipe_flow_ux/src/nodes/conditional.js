/**
 * Register a 'conditional' node: condition, if_true, if_false.
 * @param {Drawflow} editor
 */
export function registerConditional(editor) {
  // Register Conditional node: condition, if_true, if_false
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Conditional</div>
    <label>Condition</label><textarea df-condition></textarea>
    <div class="port-label">True →</div>
    <div class="port-label">False →</div>
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('conditional', html);
}