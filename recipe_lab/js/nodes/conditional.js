/**
 * @typedef {Object} ConditionalNodeConfig
 * @property {string} condition - The conditional expression string
 * @property {number[]} if_true - Array of connection IDs for the "true" branch
 * @property {number[]} if_false - Array of connection IDs for the "false" branch
 */

// Error thrown when the condition input element cannot be found
class MissingInputElement extends Error {
  constructor() {
    super('Required <input df-condition> element not found in HTML template');
    this.name = 'MissingInputElement';
  }
}

/**
 * Registers the "conditional" node type in Drawflow.
 * @param {import('drawflow').Drawflow} editor - The Drawflow editor instance
 */
export function registerConditional(editor) {
  // HTML template for the conditional node
  const template = `
    <div class="node-conditional">
      <div class="condition-label">Condition</div>
      <input df-condition type="text" class="condition-input" />
      <div class="connector input" data-port="input"></div>
      <div class="connector output if-true" data-port="if-true"></div>
      <div class="connector output if-false" data-port="if-false"></div>
    </div>
  `;

  // Register the node type with Drawflow
  editor.registerNode('conditional', template, {
    oncreate: (node) => {
      // Initialize config object and defaults
      node.data.config = node.data.config || {};
      const config = node.data.config;
      config.condition = typeof config.condition === 'string' ? config.condition : '';
      config.if_true = Array.isArray(config.if_true) ? config.if_true : [];
      config.if_false = Array.isArray(config.if_false) ? config.if_false : [];

      // Bind the condition input field
      const inputEl = node.html.querySelector('[df-condition]');
      if (!inputEl) {
        throw new MissingInputElement();
      }
      // Initialize input value
      inputEl.value = config.condition;
      inputEl.addEventListener('input', (event) => {
        config.condition = event.target.value;
        console.debug('[conditional] updated config.condition on input change');
      });
      console.debug(`[conditional] bound condition input for node ${node.id}`);
    }
  });

  console.info("[conditional] registered 'conditional' node type");
}
