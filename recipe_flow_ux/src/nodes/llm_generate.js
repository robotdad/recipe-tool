/**
 * Register an 'llm_generate' node: a textarea for prompt configuration.
 * @param {Drawflow} editor
 */
export function registerLlmGenerate(editor) {
  // Register LLM Generate node: Prompt textarea
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">LLM Generate</div>
    <label>Prompt</label><textarea df-prompt></textarea>
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('llm_generate', html);
}