/**
 * Convert raw Drawflow JSON to a simple recipe JSON.
 * @param {object} flowJson - The JSON returned by editor.export().
 * @returns {{steps: Array}} recipe JSON
 */
export function drawflowToRecipe(flowJson) {
  const steps = [];
  if (flowJson && flowJson.drawflow) {
    // Flatten across modules in order of node creation ID
    const modules = flowJson.drawflow;
    Object.values(modules).forEach(mod => {
      if (mod.data) {
        Object.values(mod.data).forEach(n => {
          steps.push({ type: n.name, config: n.data || {} });
        });
      }
    });
  }
  return { steps };
}

/**
 * Convert a recipe JSON to Drawflow JSON for import.
 * @param {{steps: Array}} recipe
 * @returns {object} flowJson suitable for editor.import()
 */
export function recipeToDrawflow(recipe) {
  const flow = { drawflow: { Home: { data: {} } } };
  if (recipe && Array.isArray(recipe.steps)) {
    recipe.steps.forEach((step, idx) => {
      flow.drawflow.Home.data[idx] = {
        id: idx,
        name: step.type,
        data: step.config || {},
        class: step.type,
        // Use registered node template
        html: step.type,
        // Default single input/output ports
        inputs: { input_1: { connections: [] } },
        outputs: { output_1: { connections: [] } },
        pos_x: 0,
        pos_y: 0
      };
    });
  }
  return flow;
}