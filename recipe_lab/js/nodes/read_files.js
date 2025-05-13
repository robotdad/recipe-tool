// src/nodes/read_files.js

/**
 * Register the Read Files Node with Drawflow editor
 * @param {import('drawflow').Drawflow} editor
 */
export function registerReadFiles(editor) {
  console.debug('Registering read_files node');

  const html = `
  <label for="read-files-path">Path</label>
  <input id="read-files-path" data-df-path>
  <label for="read-files-content_key">Key</label>
  <input id="read-files-content_key" data-df-content_key>
  `;

  editor.registerNode('read_files', {
    html,
    onCreate(node) {
      // Ensure config object
      node.data.config = node.data.config || {};
      // Default config values
      node.data.config.path = Array.isArray(node.data.config.path)
        ? node.data.config.path
        : [];
      node.data.config.content_key = node.data.config.content_key || '';

      console.debug(
        'read_files onCreate:',
        'path=', node.data.config.path,
        'content_key=', node.data.config.content_key
      );

      // Root element containing our inputs
      const container = node.html || node.el || node._dom || null;
      if (!container) {
        console.warn('read_files: cannot find container element for binding');
        return;
      }

      const pathInput = container.querySelector('[data-df-path]');
      const keyInput = container.querySelector('[data-df-content_key]');
      if (!pathInput || !keyInput) {
        console.warn('read_files: missing expected input elements');
        return;
      }

      // Initialize input values
      pathInput.value = node.data.config.path.join(', ');
      keyInput.value = node.data.config.content_key;

      // Bind path input changes
      pathInput.addEventListener('input', (e) => {
        const raw = e.target.value;
        const values = raw
          .split(',')
          .map(s => s.trim())
          .filter(Boolean);
        node.data.config.path = values;
        console.debug('read_files path updated:', values);
      });

      // Bind content_key input changes
      keyInput.addEventListener('input', (e) => {
        node.data.config.content_key = e.target.value;
        console.debug('read_files content_key updated:', e.target.value);
      });
    }
  });
}
