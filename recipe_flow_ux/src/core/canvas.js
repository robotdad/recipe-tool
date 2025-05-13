/**
 * Initialize and return a Drawflow editor instance on the given container element.
 * @param {HTMLElement} containerEl
 * @returns {Drawflow} editor
 */
export function createCanvas(containerEl) {
  const editor = new Drawflow(containerEl);
  // Enable reroute for connection curves
  editor.reroute = true;
  editor.start();
  return editor;
}