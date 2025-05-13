/**
 * @typedef {import('drawflow').default} DrawflowEditor
 */

/**
 * Initializes and starts a Drawflow editor on the given container element.
 * @param {HTMLElement} containerEl - A valid DOM element attached to the document.
 * @returns {Promise<DrawflowEditor>} A promise resolving to the Drawflow editor instance.
 * @throws {TypeError} If containerEl is not an instance of HTMLElement.
 * @throws {Error} If containerEl is not attached to the document or if initialization fails.
 */
export async function createCanvas(containerEl) {
  // Environment check
  if (typeof window === "undefined" || typeof document === "undefined") {
    throw new Error(
      "Canvas Core: createCanvas can only be run in a browser environment"
    );
  }

  console.debug("Validating provided container element");
  if (!(containerEl instanceof HTMLElement)) {
    throw new TypeError(
      "Invalid container element: expected an instance of HTMLElement"
    );
  }
  console.debug("Container is a valid HTMLElement");

  console.debug("Checking container is attached to the document");
  if (!containerEl.isConnected) {
    throw new Error("Container element is not attached to the document");
  }

  console.debug("Clearing container children");
  while (containerEl.firstChild) {
    containerEl.removeChild(containerEl.firstChild);
  }

  try {
    console.debug("Importing Drawflow library");

    console.debug("Instantiating Drawflow editor");
    const editor = new Drawflow(containerEl);

    console.debug("Calling `editor.start()`");
    editor.start();
    console.debug("Drawflow editor started successfully");

    console.info(
      "Canvas Core: createCanvas completed and editor instance returned"
    );
    return editor;
  } catch (error) {
    console.error(
      "DrawflowInitializationError: Failed to import or initialize Drawflow",
      error
    );
    throw error;
  }
}

/**
 * Convert a clientX/clientY into Drawflow’s canvas coords.
 * @param {Drawflow} editor - the Drawflow instance
 * @param {number} clientX
 * @param {number} clientY
 * @returns {{x: number, y: number}}
 */
export function screenToCanvas(editor, clientX, clientY) {
  const svgGroup = editor.precanvas;
  const pt = svgGroup.createSVGPoint();
  pt.x = clientX;
  pt.y = clientY;
  const ctm = svgGroup.getScreenCTM();
  if (!ctm) return { x: clientX, y: clientY };
  const loc = pt.matrixTransform(ctm.inverse());
  return { x: loc.x, y: loc.y };
}

// For convenience
export default createCanvas;
