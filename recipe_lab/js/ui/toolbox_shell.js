// src/ui/toolbox_shell.js
import { screenToCanvas } from "../core/canvas.js";

/**
 * Initializes the Toolbox Shell UI in the given container for a Drawflow editor.
 * @param {HTMLElement} containerEl - The container element to render the toolbox into.
 * @param {object} editor - The Drawflow editor instance (must be started).
 * @param {object} [options] - Optional configuration.
 * @param {object} [options.labels] - Text labels: { import, export }.
 * @param {string} [options.classPrefix] - CSS class prefix (default "tb-shell").
 * @param {string} [options.importAccept] - File accept filter (default ".json").
 * @param {function(number):string} [options.exportFileName] - Filename generator.
 * @param {object} [options.logger] - Logger with debug/info (default console).
 * @returns {{ teardown: function() }} teardown function removes UI and listeners.
 */
export function initToolboxShell(containerEl, editor, options = {}) {
  const logger = options.logger || console;
  const prefix = options.classPrefix || "tb-shell";
  const labels = Object.assign(
    { import: "Import JSON", export: "Export JSON" },
    options.labels
  );
  const importAccept = options.importAccept || ".json";
  const exportFileName =
    options.exportFileName || ((ts) => `drawflow-export-${ts}.json`);

  // Validate inputs
  if (!(containerEl instanceof HTMLElement)) {
    const msg = "Toolbox container element not found";
    logger.error(msg);
    throw new Error(`MissingContainerError: ${msg}`);
  }
  if (!editor) {
    const msg = "Drawflow editor instance is required but not provided";
    logger.error(msg);
    throw new Error(`EditorInstanceError: ${msg}`);
  }

  // Track event listeners for teardown
  const listeners = [];
  function addListener(target, type, handler) {
    target.addEventListener(type, handler);
    listeners.push({ target, type, handler });
  }

  // Root element
  const root = document.createElement("div");
  root.classList.add(prefix);
  containerEl.appendChild(root);

  // PALETTE
  const palette = document.createElement("div");
  palette.classList.add(`${prefix}__palette`);
  palette.setAttribute("role", "listbox");
  root.appendChild(palette);

  // Obtain registered node types from editor
  let nodeTypes = [];
  if (typeof editor.getRegisteredNodes === "function") {
    nodeTypes = editor.getRegisteredNodes();
  } else if (editor.module && editor.module.htmlNodes) {
    nodeTypes = Object.keys(editor.module.htmlNodes).map((type) => ({ type }));
  } else if (Array.isArray(options.nodeList)) {
    nodeTypes = options.nodeList;
  }
  logger.debug("Registered node types:", nodeTypes);

  // Group by category
  const groups = {};
  nodeTypes.forEach((nt) => {
    const cat = nt.category || "default";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(nt);
  });

  // Keyboard nav array
  const buttonList = [];

  // Create buttons
  Object.keys(groups).forEach((cat) => {
    const grpEl = document.createElement("div");
    grpEl.classList.add(`${prefix}__group`);
    if (cat !== "default") {
      const title = document.createElement("div");
      title.classList.add(`${prefix}__group-title`);
      title.textContent = cat;
      grpEl.appendChild(title);
    }
    groups[cat].forEach((nt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.classList.add(`${prefix}__button`);
      btn.setAttribute("role", "option");
      btn.setAttribute("aria-label", nt.label || nt.type);
      btn.setAttribute("tabindex", "0");
      btn.textContent = nt.icon || nt.label || nt.type;
      grpEl.appendChild(btn);
      buttonList.push(btn);

      // Click to add
      addListener(btn, "click", (e) => {
        const data =
          typeof editor.getNodeData === "function"
            ? editor.getNodeData(nt.type)
            : {};
        const { x, y } = screenToCanvas(editor, e.clientX, e.clientY);
        editor.addNode(nt.type, data, x, y);
        logger.info(`Added node via click: ${nt.type}`);
      });
      // Drag start
      addListener(btn, "dragstart", (e) => {
        e.dataTransfer.setData("application/x-node-type", nt.type);
        e.dataTransfer.effectAllowed = "copy";
      });
      // Keyboard navigation
      addListener(btn, "keydown", (e) => {
        const idx = buttonList.indexOf(btn);
        let tgt = null;
        if (e.key === "ArrowRight" || e.key === "ArrowDown") {
          tgt = buttonList[(idx + 1) % buttonList.length];
        } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
          tgt = buttonList[(idx - 1 + buttonList.length) % buttonList.length];
        } else if (e.key === "Enter") {
          btn.click();
        }
        if (tgt) {
          tgt.focus();
          e.preventDefault();
        }
      });
    });
    palette.appendChild(grpEl);
  });
  logger.info("Palette rendered");

  // DRAG & DROP onto Drawflow canvas
  const editorContainer =
    editor.container || (editor.getContainer && editor.getContainer());
  function handleCanvasDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  }
  function handleCanvasDrop(e) {
    e.preventDefault();
    const type = e.dataTransfer.getData("application/x-node-type");
    if (!type) return;
    const data =
      typeof editor.getNodeData === "function" ? editor.getNodeData(type) : {};
    const { x, y } = screenToCanvas(editor, e.clientX, e.clientY);
    editor.addNode(type, data, x, y);
    logger.info(`Added node via drop: ${type}`);
  }
  if (editorContainer instanceof HTMLElement) {
    addListener(editorContainer, "dragover", handleCanvasDragOver);
    addListener(editorContainer, "drop", handleCanvasDrop);
  }

  // CONTROLS
  const controls = document.createElement("div");
  controls.classList.add(`${prefix}__controls`);
  root.appendChild(controls);

  // --- Import ---
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = importAccept;
  fileInput.style.display = "none";
  root.appendChild(fileInput);

  function showAlert(msg) {
    alert(msg);
  }

  function handleFileImport(file) {
    if (!file.name.toLowerCase().endsWith(".json")) {
      const msg = "Unsupported file type for import; only .json is allowed";
      showAlert(msg);
      logger.error(msg);
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => {
      const raw = ev.target.result;
      logger.debug("Raw file content:", raw);
      let json;
      try {
        json = JSON.parse(raw);
      } catch (err) {
        const msg = "Failed to parse imported file as JSON";
        showAlert(msg + ": " + err.message);
        logger.error("JSON parse error:", err);
        return;
      }
      if (
        confirm(
          "Are you sure you want to import this flow? This will overwrite the current diagram."
        )
      ) {
        editor.import(json);
        logger.info("Flow imported successfully");
        showAlert("Flow imported successfully");
      }
    };
    reader.readAsText(file);
  }

  addListener(fileInput, "change", () => {
    if (fileInput.files.length) {
      handleFileImport(fileInput.files[0]);
      fileInput.value = "";
    }
  });

  // Drop on palette area
  addListener(root, "dragover", (e) => {
    e.preventDefault();
  });
  addListener(root, "drop", (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
      handleFileImport(e.dataTransfer.files[0]);
    }
  });

  const importBtn = document.createElement("button");
  importBtn.type = "button";
  importBtn.classList.add(`${prefix}__control`);
  importBtn.textContent = labels.import;
  importBtn.setAttribute("aria-label", labels.import);
  addListener(importBtn, "click", () => fileInput.click());
  controls.appendChild(importBtn);

  // --- Export ---
  function showModal(content) {
    const overlay = document.createElement("div");
    overlay.classList.add(`${prefix}__modal-overlay`);
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    const modal = document.createElement("div");
    modal.classList.add(`${prefix}__modal`);
    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.textContent = "Close";
    closeBtn.classList.add(`${prefix}__modal-close`);
    addListener(closeBtn, "click", () => document.body.removeChild(overlay));
    const pre = document.createElement("pre");
    pre.textContent = content;
    modal.appendChild(closeBtn);
    modal.appendChild(pre);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    closeBtn.focus();
  }

  function handleExport() {
    const flow = editor.export();
    logger.debug("Exported flow object:", flow);
    const text = JSON.stringify(flow, null, 2);
    const ts = Date.now();
    const fname = exportFileName(ts);
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fname;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    logger.info(`Flow export triggered: ${fname}`);
    showModal(text);
  }

  const exportBtn = document.createElement("button");
  exportBtn.type = "button";
  exportBtn.classList.add(`${prefix}__control`);
  exportBtn.textContent = labels.export;
  exportBtn.setAttribute("aria-label", labels.export);
  addListener(exportBtn, "click", handleExport);
  controls.appendChild(exportBtn);

  // Teardown
  function teardown() {
    // Remove listeners
    listeners.forEach(({ target, type, handler }) => {
      target.removeEventListener(type, handler);
    });
    // Remove UI
    if (containerEl.contains(root)) {
      containerEl.removeChild(root);
    }
  }

  return { teardown };
}
