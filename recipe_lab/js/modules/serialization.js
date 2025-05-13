// src/modules/serialization.js
// Provides conversion between recipe DSL JSON and Drawflow editor JSON

const H_SPACING = 200;
const V_OFFSET = 100;
const KNOWN_META = new Set(["pos_x", "pos_y", "html", "class", "inputs", "outputs", "typenode"]);

function deepClone(obj) {
  if (typeof structuredClone === 'function') {
    return structuredClone(obj);
  }
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Converts a recipe JSON to Drawflow JSON.
 * @param {object} recipeJson
 * @returns {object}
 */
export function recipeToDrawflow(recipeJson) {
  if (typeof recipeJson !== 'object' || recipeJson === null || !Array.isArray(recipeJson.steps)) {
    throw new TypeError("Input to recipeToDrawflow must be a valid recipe object with a 'steps' array");
  }
  console.debug(`Starting recipeToDrawflow: received recipe with ${recipeJson.steps.length} steps`);
  recipeJson.steps.forEach((step, idx) => {
    if (typeof step !== 'object' || step === null || typeof step.type !== 'string' || typeof step.config !== 'object' || step.config === null) {
      throw new TypeError(`Each step must be an object with 'type' (string) and 'config' (object); error at step ${idx}`);
    }
  });

  const cloned = deepClone(recipeJson);
  const drawflow = { drawflow: { Home: { data: {} } } };
  cloned.steps.forEach((step, idx) => {
    const nodeId = idx + 1;
    const pos_x = idx * H_SPACING;
    const pos_y = V_OFFSET;
    const node = {
      id: nodeId,
      name: step.type,
      data: { config: deepClone(step.config) },
      pos_x,
      pos_y,
      inputs: {},
      outputs: {}
    };
    drawflow.drawflow.Home.data[String(nodeId)] = node;
    console.debug(`Mapped recipe step ${idx} of type '${step.type}' to Drawflow node with id ${nodeId}`);
  });
  const nodeCount = Object.keys(drawflow.drawflow.Home.data).length;
  console.debug(`Completed recipeToDrawflow: generated ${nodeCount} nodes under module 'Home'`);
  return drawflow;
}

/**
 * Converts a Drawflow JSON to recipe DSL JSON.
 * @param {object} flowJson
 * @returns {object}
 */
export function drawflowToRecipe(flowJson) {
  if (typeof flowJson !== 'object' || flowJson === null || typeof flowJson.drawflow !== 'object' || flowJson.drawflow === null) {
    throw new TypeError("Input to drawflowToRecipe must be a valid Drawflow object with a 'drawflow' property");
  }
  console.debug(`Starting drawflowToRecipe: received Drawflow JSON with modules ${Object.keys(flowJson.drawflow).length}`);
  const cloned = deepClone(flowJson);
  const steps = [];

  for (const [moduleName, module] of Object.entries(cloned.drawflow)) {
    const data = module.data || {};
    const entries = Object.entries(data).sort((a, b) => Number(a[0]) - Number(b[0]));
    for (const [idStr, node] of entries) {
      for (const key of Object.keys(node)) {
        if (key === 'id' || key === 'name' || key === 'data') continue;
        if (KNOWN_META.has(key)) continue;
        console.warn(`Unknown Drawflow metadata field '${key}' will be discarded.`);
      }
      const name = node.name;
      const nodeId = node.id;
      let baseConfig = {};
      if (node.data && typeof node.data === 'object') {
        if (node.data.config && typeof node.data.config === 'object') {
          baseConfig = deepClone(node.data.config);
        }
        for (const [k, v] of Object.entries(node.data)) {
          if (k === 'config') continue;
          baseConfig[k] = deepClone(v);
        }
      }
      const stepIndex = steps.length;
      console.debug(`Mapped Drawflow node ${nodeId} (name '${name}') to recipe step ${stepIndex}`);
      steps.push({ type: name, config: baseConfig });
    }
  }
  console.debug(`Completed drawflowToRecipe: generated ${steps.length} steps`);
  return { steps };
}
