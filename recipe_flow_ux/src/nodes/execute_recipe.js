/**
 * Register an 'execute_recipe' node: recipe_path, context_overrides.
 * @param {Drawflow} editor
 */
export function registerExecuteRecipe(editor) {
  // Register Execute Recipe node: recipe_path, context_overrides
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Execute Recipe</div>
    <label>Recipe Path</label><input type="text" df-recipe_path />
    <label>Context Overrides</label><textarea df-context_overrides></textarea>
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('execute_recipe', html);
}