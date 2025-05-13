// src/nodes/llm_generate.js
// Drawflow node for LLM Generate step

export function registerLLMGenerate(editor) {
  const html = `
    <div class="node-box" style="padding:8px;">
      <label style="display:block; font-weight:bold; margin-bottom:4px;">Prompt</label>
      <textarea df-prompt style="width:100%; height:60px; margin-bottom:8px;"></textarea>

      <label style="display:block; font-weight:bold; margin-bottom:4px;">Model</label>
      <input type="text" df-model style="width:100%; margin-bottom:8px;" />

      <label style="display:block; font-weight:bold; margin-bottom:4px;">Max Tokens</label>
      <input type="number" df-max_tokens style="width:100%; margin-bottom:8px;" />

      <label style="display:block; font-weight:bold; margin-bottom:4px;">MCP Servers</label>
      <textarea df-mcp_servers placeholder='[{"url":"https://...","headers":{}}]' style="width:100%; height:60px; margin-bottom:8px;"></textarea>

      <label style="display:block; font-weight:bold; margin-bottom:4px;">Output Format</label>
      <select df-output_format style="width:100%; margin-bottom:8px;">
        <option value="text">text</option>
        <option value="files">files</option>
        <option value="json-schema">json-schema</option>
      </select>

      <label style="display:block; font-weight:bold; margin-bottom:4px;">Output Key</label>
      <input type="text" df-output_key style="width:100%; margin-bottom:8px;" />

      <div class="ports">
        <div class="port in" data-port="input_1"></div>
        <div class="port out" data-port="output_1"></div>
      </div>
    </div>
  `;

  editor.registerNode("llm_generate", {
    html,
    onCreate: function(node) {
      // Initialize default config
      node.data.config = {
        prompt: "",
        model: "openai/gpt-4o",
        max_tokens: null,
        mcp_servers: [],
        output_format: "text",
        output_key: "llm_output"
      };
      // Keep last valid JSON string for MCP servers
      node._lastValidMcp = JSON.stringify(node.data.config.mcp_servers);

      // Helper to find controls
      const root = node.el;
      const promptEl = root.querySelector('[df-prompt]');
      const modelEl = root.querySelector('[df-model]');
      const maxEl = root.querySelector('[df-max_tokens]');
      const mcpEl = root.querySelector('[df-mcp_servers]');
      const formatEl = root.querySelector('[df-output_format]');
      const keyEl = root.querySelector('[df-output_key]');

      // Set initial values
      promptEl.value = node.data.config.prompt;
      modelEl.value = node.data.config.model;
      maxEl.value = node.data.config.max_tokens != null ? node.data.config.max_tokens : '';
      mcpEl.value = node._lastValidMcp;
      formatEl.value = node.data.config.output_format;
      keyEl.value = node.data.config.output_key;

      // Validation helpers
      function showError(el, message) {
        if (!el._errorEl) {
          const err = document.createElement('div');
          err.style.color = 'red';
          err.style.fontSize = '12px';
          el.parentNode.insertBefore(err, el.nextSibling);
          el._errorEl = err;
        }
        el._errorEl.innerText = message;
        el.style.borderColor = 'red';
      }
      function clearError(el) {
        if (el._errorEl) {
          el._errorEl.parentNode.removeChild(el._errorEl);
          delete el._errorEl;
        }
        el.style.borderColor = '';
      }

      // Event listeners
      promptEl.addEventListener('input', () => {
        const v = promptEl.value.trim();
        if (!v) showError(promptEl, 'Required'); else clearError(promptEl);
        node.data.config.prompt = promptEl.value;
        console.debug('llm_generate config updated:', node.data.config);
        editor.trigger('nodeDataChanged', node.id);
      });

      modelEl.addEventListener('input', () => {
        node.data.config.model = modelEl.value;
        console.debug('llm_generate config updated:', node.data.config);
        editor.trigger('nodeDataChanged', node.id);
      });

      maxEl.addEventListener('input', () => {
        const v = maxEl.value;
        if (v === '' || /^\d+$/.test(v)) {
          clearError(maxEl);
          node.data.config.max_tokens = v === '' ? null : parseInt(v, 10);
        } else {
          showError(maxEl, 'Must be integer');
          node.data.config.max_tokens = null;
        }
        console.debug('llm_generate config updated:', node.data.config);
        editor.trigger('nodeDataChanged', node.id);
      });

      mcpEl.addEventListener('blur', () => {
        const text = mcpEl.value;
        try {
          const parsed = JSON.parse(text);
          if (!Array.isArray(parsed)) throw new Error('Must be JSON array');
          clearError(mcpEl);
          node.data.config.mcp_servers = parsed;
          node._lastValidMcp = text;
        } catch (err) {
          showError(mcpEl, 'Invalid JSON');
          mcpEl.value = node._lastValidMcp;
        }
        console.debug('llm_generate config updated:', node.data.config);
        editor.trigger('nodeDataChanged', node.id);
      });

      formatEl.addEventListener('change', () => {
        node.data.config.output_format = formatEl.value;
        console.debug('llm_generate config updated:', node.data.config);
        editor.trigger('nodeDataChanged', node.id);
      });

      keyEl.addEventListener('input', () => {
        node.data.config.output_key = keyEl.value;
        console.debug('llm_generate config updated:', node.data.config);
        editor.trigger('nodeDataChanged', node.id);
      });

      console.debug('llm_generate node created with config:', node.data.config);
    },
    onUpdate: function(node) {
      // Sync UI to config when node is updated/imported
      const root = node.el;
      const promptEl = root.querySelector('[df-prompt]');
      const modelEl = root.querySelector('[df-model]');
      const maxEl = root.querySelector('[df-max_tokens]');
      const mcpEl = root.querySelector('[df-mcp_servers]');
      const formatEl = root.querySelector('[df-output_format]');
      const keyEl = root.querySelector('[df-output_key]');

      promptEl.value = node.data.config.prompt || '';
      modelEl.value = node.data.config.model || '';
      maxEl.value = node.data.config.max_tokens != null ? node.data.config.max_tokens : '';
      const mcpText = JSON.stringify(node.data.config.mcp_servers || []);
      mcpEl.value = mcpText;
      node._lastValidMcp = mcpText;
      formatEl.value = node.data.config.output_format || 'text';
      keyEl.value = node.data.config.output_key || '';

      console.debug('llm_generate config updated:', node.data.config);
    }
  });
}
