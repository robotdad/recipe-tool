// src/nodes/mcp.js
// ES module registering the MCP Drawflow node
export function registerMcpNode(editor) {
  console.info('Registered MCP node type');

  // HTML template for the MCP node UI
  const html = `
<div class="drawflow-node mcp-node">
  <div class="mcp-content">
    <label>Transport:
      <select df-transport>
        <option value="http">HTTP SSE</option>
        <option value="stdio">stdio</option>
      </select>
    </label>
    <div df-http-section>
      <label>URL:
        <input type="text" df-url />
      </label>
      <div class="mcp-dynamic-section">
        <span>Headers:</span>
        <button type="button" df-add-header>Add</button>
        <div df-headers-container></div>
      </div>
    </div>
    <div df-stdio-section style="display:none;">
      <label>Command:
        <input type="text" df-command />
      </label>
      <label>Args:
        <textarea df-args></textarea>
      </label>
      <label>Working Dir:
        <input type="text" df-working_dir />
      </label>
      <div class="mcp-dynamic-section">
        <span>Env:</span>
        <button type="button" df-add-env>Add</button>
        <div df-envs-container></div>
      </div>
    </div>
    <label>Tool Name:
      <input type="text" df-tool_name />
      <div class="mcp-warning" df-warn-tool_name></div>
    </label>
    <label>Arguments (JSON):
      <textarea df-arguments></textarea>
      <div class="mcp-warning" df-warn-arguments></div>
    </label>
    <label>Result Key:
      <input type="text" df-result_key />
      <div class="mcp-warning" df-warn-result_key></div>
    </label>
  </div>
</div>
`;

  // Helper to show inline warning
  function showInlineWarning(inputEl, warnEl, msg) {
    inputEl.classList.add('mcp-error');
    warnEl.textContent = msg;
  }
  function clearInlineWarning(inputEl, warnEl) {
    inputEl.classList.remove('mcp-error');
    warnEl.textContent = '';
  }

  function isValidIdentifier(val) {
    return /^[A-Za-z0-9_]+$/.test(val);
  }

  // Bind fields for create/edit/update
  function bindFields(node, el) {
    const config = node.data.config = node.data.config || {};
    // Defaults
    if (!config.transport) config.transport = 'http';
    if (!Array.isArray(config.headers)) config.headers = [];
    if (!Array.isArray(config.env)) config.env = {};

    // Query elements
    const transportEl = el.querySelector('[df-transport]');
    const httpSection = el.querySelector('[df-http-section]');
    const stdioSection = el.querySelector('[df-stdio-section]');
    const urlEl = el.querySelector('[df-url]');
    const commandEl = el.querySelector('[df-command]');
    const argsEl = el.querySelector('[df-args]');
    const workingDirEl = el.querySelector('[df-working_dir]');
    const headersContainer = el.querySelector('[df-headers-container]');
    const addHeaderBtn = el.querySelector('[df-add-header]');
    const envsContainer = el.querySelector('[df-envs-container]');
    const addEnvBtn = el.querySelector('[df-add-env]');
    const toolNameEl = el.querySelector('[df-tool_name]');
    const toolNameWarn = el.querySelector('[df-warn-tool_name]');
    const argumentsEl = el.querySelector('[df-arguments]');
    const argumentsWarn = el.querySelector('[df-warn-arguments]');
    const resultKeyEl = el.querySelector('[df-result_key]');
    const resultKeyWarn = el.querySelector('[df-warn-result_key]');

    // Update editor config and log
    function updateConfig(field, value) {
      config[field] = value;
      editor.updateNodeDataFromId(node.id, { config });
      console.debug(`MCP config update for node=${node.id} field=${field} value=${JSON.stringify(value)}`);
      updateExportButton();
    }

    // Export button toggling
    function isConfigValid() {
      return (
        typeof config.arguments === 'object' && !Array.isArray(config.arguments) &&
        isValidIdentifier(config.tool_name) && isValidIdentifier(config.result_key)
      );
    }
    function updateExportButton() {
      const btn = document.querySelector('.btn-export');
      if (btn) btn.disabled = !isConfigValid();
    }

    // Toggle HTTP vs stdio UI
    function toggleSections(value) {
      if (value === 'http') {
        httpSection.style.display = '';
        stdioSection.style.display = 'none';
      } else {
        httpSection.style.display = 'none';
        stdioSection.style.display = '';
      }
    }

    // Dynamic headers
    function renderHeaders() {
      headersContainer.innerHTML = '';
      (config.headers || []).forEach((h, idx) => {
        const row = document.createElement('div');
        row.innerHTML = `
          <input type="text" df-header-key placeholder="Key" value="${h.key || ''}" />
          <input type="text" df-header-value placeholder="Value" value="${h.value || ''}" />
          <button type="button" class="remove-header">×</button>
        `;
        const keyEl = row.querySelector('[df-header-key]');
        const valEl = row.querySelector('[df-header-value]');
        row.querySelector('.remove-header').addEventListener('click', () => {
          config.headers.splice(idx, 1);
          updateConfig('headers', config.headers);
          renderHeaders();
        });
        keyEl.addEventListener('input', () => {
          config.headers[idx].key = keyEl.value;
          updateConfig('headers', config.headers);
        });
        valEl.addEventListener('input', () => {
          config.headers[idx].value = valEl.value;
          updateConfig('headers', config.headers);
        });
        headersContainer.appendChild(row);
      });
    }
    addHeaderBtn.addEventListener('click', () => {
      config.headers = config.headers || [];
      config.headers.push({ key: '', value: '' });
      updateConfig('headers', config.headers);
      renderHeaders();
    });

    // Dynamic env vars
    function renderEnvs() {
      envsContainer.innerHTML = '';
      Object.entries(config.env || {}).forEach(([k, v], idx) => {
        const row = document.createElement('div');
        row.innerHTML = `
          <input type="text" df-env-key placeholder="Key" value="${k}" />
          <input type="text" df-env-value placeholder="Value" value="${v}" />
          <button type="button" class="remove-env">×</button>
        `;
        const keyEl = row.querySelector('[df-env-key]');
        const valEl = row.querySelector('[df-env-value]');
        row.querySelector('.remove-env').addEventListener('click', () => {
          delete config.env[k];
          updateConfig('env', config.env);
          renderEnvs();
        });
        keyEl.addEventListener('input', () => {
          const oldKey = Object.keys(config.env)[idx];
          const newKey = keyEl.value;
          const val = config.env[oldKey];
          delete config.env[oldKey];
          config.env[newKey] = val;
          updateConfig('env', config.env);
        });
        valEl.addEventListener('input', () => {
          const key = Object.keys(config.env)[idx];
          config.env[key] = valEl.value;
          updateConfig('env', config.env);
        });
        envsContainer.appendChild(row);
      });
    }
    addEnvBtn.addEventListener('click', () => {
      config.env = config.env || {};
      config.env[''] = '';
      updateConfig('env', config.env);
      renderEnvs();
    });

    // JSON arguments handling
    let lastValidArgs = config.args || '';
    argsEl.value = config.args || '';
    argsEl.addEventListener('input', () => {
      try {
        lastValidArgs = argsEl.value;
        updateConfig('args', lastValidArgs);
      } catch (e) {
        console.error('Failed to parse args text', e);
      }
    });

    // Bind field listeners and initial values
    transportEl.value = config.transport;
    toggleSections(config.transport);
    transportEl.addEventListener('change', () => {
      updateConfig('transport', transportEl.value);
      toggleSections(transportEl.value);
    });

    if (config.url) urlEl.value = config.url;
    urlEl.addEventListener('input', () => updateConfig('url', urlEl.value));

    if (config.command) commandEl.value = config.command;
    commandEl.addEventListener('input', () => updateConfig('command', commandEl.value));

    if (config.working_dir) workingDirEl.value = config.working_dir;
    workingDirEl.addEventListener('input', () => updateConfig('working_dir', workingDirEl.value));

    // Tool name validation
    toolNameEl.value = config.tool_name || '';
    toolNameEl.addEventListener('input', () => {
      const v = toolNameEl.value.trim();
      if (!isValidIdentifier(v)) {
        showInlineWarning(toolNameEl, toolNameWarn, "Required; alphanumeric or underscore");
      } else {
        clearInlineWarning(toolNameEl, toolNameWarn);
        updateConfig('tool_name', v);
      }
    });

    // JSON arguments field
    argumentsEl.value = config.arguments ? JSON.stringify(config.arguments) : '';
    argumentsEl.addEventListener('input', () => {
      const txt = argumentsEl.value;
      try {
        const obj = JSON.parse(txt);
        if (typeof obj !== 'object' || Array.isArray(obj)) {
          throw new Error('Top-level JSON must be an object');
        }
        clearInlineWarning(argumentsEl, argumentsWarn);
        updateConfig('arguments', obj);
        console.debug(`Parsed arguments JSON for node=${node.id}`);
      } catch (err) {
        showInlineWarning(argumentsEl, argumentsWarn, 'Invalid JSON object');
      }
    });

    // Result key validation
    resultKeyEl.value = config.result_key || '';
    resultKeyEl.addEventListener('input', () => {
      const v = resultKeyEl.value.trim();
      if (!isValidIdentifier(v)) {
        showInlineWarning(resultKeyEl, resultKeyWarn, "Required; alphanumeric or underscore");
      } else {
        clearInlineWarning(resultKeyEl, resultKeyWarn);
        updateConfig('result_key', v);
      }
    });

    // Initial dynamic renders
    renderHeaders();
    renderEnvs();
    updateExportButton();
  }

  // Register the node with Drawflow
  editor.registerNode('mcp', {
    html: html,
    onCreate: bindFields,
    onEdit: bindFields,
    onUpdate: bindFields,
    width: 220,
    height: 300
  });
}
