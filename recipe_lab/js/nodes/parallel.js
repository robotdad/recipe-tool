// src/nodes/parallel.js
// ES module exporting registerParallel to register a "parallel" node in Drawflow
export function registerParallel(editor) {
  // HTML template for the Parallel node
  const html = `
<div>
  <label>Substeps (JSON):</label><br>
  <textarea df-substeps rows="4" style="width:100%;"></textarea>
</div>
<div>
  <label>Max Concurrency:</label><br>
  <input type="number" df-max_concurrency min="0" step="1" style="width:100%;">
</div>
<div>
  <label>Delay (s):</label><br>
  <input type="number" df-delay min="0" step="0.1" style="width:100%;">
</div>
`;  

  // Register the node with Drawflow
  editor.registerNode('parallel', {
    html,
    // Called when a node instance is created
    onCreate(node) {
      // Initialize default config and backup
      node.data.config = {
        substeps: [],
        max_concurrency: 0,
        delay: 0.0
      };
      node.data._previousValidSubsteps = JSON.stringify(node.data.config.substeps);
      console.info('Parallel node created with default config');

      // Bind DOM fields
      const textarea = node.html.querySelector('[df-substeps]');
      const inputMax = node.html.querySelector('[df-max_concurrency]');
      const inputDelay = node.html.querySelector('[df-delay]');

      // Initialize field values
      textarea.value = node.data._previousValidSubsteps;
      inputMax.value = node.data.config.max_concurrency;
      inputDelay.value = node.data.config.delay;

      // Handle max_concurrency input
      inputMax.addEventListener('input', () => {
        let val = parseInt(inputMax.value, 10);
        if (isNaN(val) || val < 0) val = 0;
        node.data.config.max_concurrency = val;
        console.debug(`Updated max_concurrency: ${val}`);
        console.info('Parallel node configuration updated');
      });

      // Handle delay input
      inputDelay.addEventListener('input', () => {
        let val = parseFloat(inputDelay.value);
        if (isNaN(val) || val < 0) val = 0.0;
        node.data.config.delay = val;
        console.debug(`Updated delay: ${val}`);
        console.info('Parallel node configuration updated');
      });

      // Handle substeps JSON input on blur/change
      const parseSubsteps = () => {
        const text = textarea.value;
        try {
          const parsed = JSON.parse(text);
          if (!Array.isArray(parsed)) {
            throw new Error('Parsed value is not an array');
          }
          node.data.config.substeps = parsed;
          node.data._previousValidSubsteps = text;
          console.debug(`Parsed substeps JSON: ${text}`);
          console.info('Parallel node configuration updated');
        } catch (err) {
          // Error handling per spec
          alert('Invalid JSON in Substeps field');
          console.warn('JSONParseError: Invalid JSON in Substeps field', err);
          // Revert to last valid
          textarea.value = node.data._previousValidSubsteps;
        }
      };
      textarea.addEventListener('blur', parseSubsteps);
      textarea.addEventListener('change', parseSubsteps);
    }
  });
}
