/**
 * Register an 'mcp' node: server, tool_name, arguments, result_key.
 * @param {Drawflow} editor
 */
export function registerMcp(editor) {
  // Register MCP node: server, tool_name, arguments, result_key
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">MCP Call</div>
    <label>Server</label><textarea df-server></textarea>
    <label>Tool Name</label><input type="text" df-tool_name />
    <label>Arguments</label><textarea df-arguments></textarea>
    <label>Result Key</label><input type="text" df-result_key />
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('mcp', html);
}