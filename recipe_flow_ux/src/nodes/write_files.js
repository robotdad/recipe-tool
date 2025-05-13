/**
 * Register a 'write_files' node: files_key, explicit files, root.
 * @param {Drawflow} editor
 */
export function registerWriteFiles(editor) {
  // Register Write Files node: files_key, files, root
  const html = document.createElement('div');
  html.innerHTML = `
    <div class="node-title">Write Files</div>
    <label>Files Key</label><input type="text" df-files_key />
    <label>Files (JSON array)</label><textarea df-files></textarea>
    <label>Root</label><input type="text" df-root />
    <div class="port-label">Next →</div>
  `;
  editor.registerNode('write_files', html);
}