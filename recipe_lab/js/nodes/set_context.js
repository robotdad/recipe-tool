import { editor } from 'drawflow';

// Custom error types
class ValidationError extends Error {}
class JSONParseError extends Error {}

// HTML template for the Set Context node
const html = `
<div class="drawflow-node set-context">
  <div class="title-box">Set Context</div>
  <div class="box">
    <div class="form-group">
      <label>Context Key</label>
      <input type="text" df-key />
      <div class="error-message" style="display:none;"></div>
    </div>
    <div class="form-group">
      <label>Value</label>
      <textarea rows="3" df-value></textarea>
      <div class="error-message" style="display:none;"></div>
    </div>
    <div class="form-group">
      <label><input type="checkbox" df-nested_render /> Nested Render</label>
    </div>
    <div class="form-group">
      <label>If Exists</label>
      <select df-if_exists>
        <option value="overwrite">overwrite</option>
        <option value="merge">merge</option>
      </select>
    </div>
  </div>
</div>
`;

// Register the node with Drawflow
editor.registerNode('set_context', {
  html,
  onCreate(nodeElement, data) {
    // Default configuration
    const defaultConfig = {
      key: '',
      value: '',
      nested_render: false,
      if_exists: 'overwrite'
    };
    // Merge any existing config (for updates) with defaults
    data.config = Object.assign({}, defaultConfig, data.config || {});
    console.debug(`Node ${data.id} default config:`, data.config);

    // Prepare listener registry for cleanup
    const listeners = [];
    function addListener(el, event, handler) {
      el.addEventListener(event, handler);
      listeners.push({ el, event, handler });
    }
    nodeElement._listeners = listeners;

    // Query controls
    const keyInput = nodeElement.querySelector('input[df-key]');
    const keyError = nodeElement.querySelector('.form-group input[df-key] + .error-message');
    const valueTextarea = nodeElement.querySelector('textarea[df-value]');
    const valueError = nodeElement.querySelector('textarea[df-value] + .error-message');
    const nestedCheckbox = nodeElement.querySelector('input[df-nested_render]');
    const ifExistsSelect = nodeElement.querySelector('select[df-if_exists]');

    // Initialize UI to reflect config
    keyInput.value = data.config.key;
    valueTextarea.value = data.config.value;
    nestedCheckbox.checked = data.config.nested_render;
    ifExistsSelect.value = data.config.if_exists;

    // Validation for context key
    function validateKey() {
      if (!keyInput.value.trim()) {
        data.config.key = '';
        keyInput.classList.add('invalid');
        keyError.textContent = 'Context key is required';
        keyError.style.display = 'block';
        // disable other controls
        [valueTextarea, nestedCheckbox, ifExistsSelect].forEach(el => el.disabled = true);
        throw new ValidationError('Context key is required');
      } else {
        data.config.key = keyInput.value;
        keyInput.classList.remove('invalid');
        keyError.style.display = 'none';
        [valueTextarea, nestedCheckbox, ifExistsSelect].forEach(el => el.disabled = false);
      }
    }

    // Key input listeners
    addListener(keyInput, 'input', e => {
      data.config.key = e.target.value;
      console.debug(`Node ${data.id} update field key:`, data.config.key);
    });
    addListener(keyInput, 'blur', () => {
      try {
        validateKey();
      } catch (err) {
        // swallow, error already displayed
      }
    });

    // Value textarea listeners
    addListener(valueTextarea, 'input', e => {
      data.config.value = e.target.value;
      console.debug(`Node ${data.id} update field value:`, data.config.value);
    });
    addListener(valueTextarea, 'blur', () => {
      if (nestedCheckbox.checked) {
        try {
          JSON.parse(valueTextarea.value);
          valueTextarea.classList.remove('invalid');
          valueError.style.display = 'none';
        } catch (err) {
          // JSON parse error
          valueTextarea.classList.add('invalid');
          valueError.textContent = 'Value field contains invalid JSON';
          valueError.style.display = 'block';
          // offer a raw-string toggle if not present
          if (!nodeElement.querySelector('#raw-toggle-label')) {
            const toggleLabel = document.createElement('label');
            toggleLabel.id = 'raw-toggle-label';
            toggleLabel.style.display = 'block';
            toggleLabel.style.fontSize = '12px';
            toggleLabel.style.marginTop = '4px';
            toggleLabel.innerHTML = `
              <input type="checkbox" id="raw-toggle" /> Treat as raw string
            `;
            valueError.insertAdjacentElement('afterend', toggleLabel);
            const rawInput = toggleLabel.querySelector('#raw-toggle');
            addListener(rawInput, 'change', ev => {
              if (ev.target.checked) {
                // accept raw text
                data.config.value = valueTextarea.value;
                console.debug(`Node ${data.id} raw-string accepted`);
                valueTextarea.classList.remove('invalid');
                valueError.style.display = 'none';
              }
            });
          }
          throw new JSONParseError('Invalid JSON in value field');
        }
      }
    });

    // Nested render checkbox listener
    addListener(nestedCheckbox, 'change', e => {
      data.config.nested_render = e.target.checked;
      console.debug(`Node ${data.id} update field nested_render:`, data.config.nested_render);
    });

    // If-exists select listener
    addListener(ifExistsSelect, 'change', e => {
      data.config.if_exists = e.target.value;
      console.debug(`Node ${data.id} update field if_exists:`, data.config.if_exists);
    });
  },

  onUpdate(nodeElement, data) {
    // Mirror updated data back into UI
    const keyInput = nodeElement.querySelector('input[df-key]');
    const valueTextarea = nodeElement.querySelector('textarea[df-value]');
    const nestedCheckbox = nodeElement.querySelector('input[df-nested_render]');
    const ifExistsSelect = nodeElement.querySelector('select[df-if_exists]');
    keyInput.value = data.config.key;
    valueTextarea.value = data.config.value;
    nestedCheckbox.checked = data.config.nested_render;
    ifExistsSelect.value = data.config.if_exists;
  },

  onDestroy(nodeElement, data) {
    // Clean up all listeners
    const listeners = nodeElement._listeners || [];
    listeners.forEach(({ el, event, handler }) => {
      el.removeEventListener(event, handler);
    });
    delete nodeElement._listeners;
  }
});
