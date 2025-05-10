/**
 * Properties panel component
 */
import { NodeTypes } from "../editor/node-types.js";

export class PropertiesPanel {
  /**
   * Create a properties panel
   * @param {string} containerId - Container element ID
   * @param {function} onPropertiesChanged - Callback when properties are changed
   */
  constructor(containerId, onPropertiesChanged) {
    this.container = document.getElementById(containerId);
    this.onPropertiesChanged = onPropertiesChanged;
    this.currentNode = null;
  }

  /**
   * Show properties for a node
   * @param {object} node - Cytoscape node
   */
  showNodeProperties(node) {
    this.currentNode = node;
    const data = node.data();

    if (!this.container) return;

    // Generate HTML
    let html = this._generatePropertiesHTML(data);

    // Update DOM
    this.container.innerHTML = html;

    // Attach event listeners
    this._attachEventListeners();
  }

  /**
   * Clear properties panel
   */
  clear() {
    this.currentNode = null;
    if (this.container) {
      this.container.innerHTML =
        '<p class="empty-state">Select a node to edit its properties</p>';
    }
  }

  /**
   * Generate HTML for node properties
   * @param {object} data - Node data
   * @returns {string} - HTML string
   * @private
   */
  _generatePropertiesHTML(data) {
    const type = data.type || "unknown";

    let html = `
      <div class="property-group">
        <label>Step Type</label>
        <select id="node-type">
            ${NodeTypes.getAllTypes()
              .map((t) => {
                const typeInfo = NodeTypes.getTypeInfo(t);
                return `<option value="${t}" ${
                  data.type === t ? "selected" : ""
                }>${typeInfo.icon} ${typeInfo.label}</option>`;
              })
              .join("")}
        </select>
      </div>
    `;

    // Add config properties based on type
    const configFields = NodeTypes.getConfigFields(type);
    const config = data.config || {};

    configFields.forEach((field) => {
      html += `
        <div class="property-group">
          <label>${field.label}</label>
          ${this._renderPropertyInput(field, config[field.key] || "")}
          ${
            field.description
              ? `<div class="field-description">${field.description}</div>`
              : ""
          }
        </div>
      `;
    });

    html += `
      <div class="property-actions">
        <button id="apply-properties-btn">Apply</button>
      </div>
    `;

    return html;
  }

  /**
   * Render input field for a property
   * @param {object} field - Field definition
   * @param {any} value - Field value
   * @returns {string} - HTML for input field
   * @private
   */
  _renderPropertyInput(field, value) {
    switch (field.type) {
      case "text":
        return `<input type="text" id="prop-${
          field.key
        }" value="${this._escapeHtml(String(value))}">`;

      case "textarea":
        return `<textarea id="prop-${field.key}" rows="5">${this._escapeHtml(
          String(value)
        )}</textarea>`;

      case "number":
        return `<input type="number" id="prop-${field.key}" value="${
          value || 0
        }">`;

      case "boolean":
        return `<input type="checkbox" id="prop-${field.key}" ${
          value ? "checked" : ""
        }>`;

      case "select":
        if (!field.options || !field.options.length) {
          return `<input type="text" id="prop-${
            field.key
          }" value="${this._escapeHtml(String(value))}">`;
        }

        return `
          <select id="prop-${field.key}">
            ${field.options
              .map(
                (opt) =>
                  `<option value="${opt.value}" ${
                    value === opt.value ? "selected" : ""
                  }>${opt.label}</option>`
              )
              .join("")}
          </select>
        `;

      default:
        return `<input type="text" id="prop-${
          field.key
        }" value="${this._escapeHtml(String(value))}">`;
    }
  }

  /**
   * Escape HTML special characters
   * @param {string} text - Input text
   * @returns {string} - Escaped text
   * @private
   */
  _escapeHtml(text) {
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
  }

  /**
   * Attach event listeners to property inputs
   * @private
   */
  _attachEventListeners() {
    // Node type change
    const nodeTypeSelect = document.getElementById("node-type");
    if (nodeTypeSelect) {
      nodeTypeSelect.addEventListener("change", (e) => {
        const newType = e.target.value;
        this._updateNodeType(newType);
      });
    }

    // Apply button
    const applyBtn = document.getElementById("apply-properties-btn");
    if (applyBtn) {
      applyBtn.addEventListener("click", () => {
        this._applyProperties();
      });
    }
  }

  /**
   * Update node type
   * @param {string} newType - New node type
   * @private
   */
  _updateNodeType(newType) {
    if (!this.currentNode) return;

    const typeInfo = NodeTypes.getTypeInfo(newType);

    // Update node data
    this.currentNode.data({
      type: newType,
      color: typeInfo.color,
      icon: typeInfo.icon,
      label: typeInfo.label,
    });

    // Refresh properties panel
    this.showNodeProperties(this.currentNode);

    // Notify listener
    if (this.onPropertiesChanged) {
      this.onPropertiesChanged(this.currentNode);
    }
  }

  /**
   * Apply properties to node
   * @private
   */
  _applyProperties() {
    if (!this.currentNode) return;

    const type = document.getElementById("node-type").value;
    const config = {};

    // Collect config values
    const configFields = NodeTypes.getConfigFields(type);
    configFields.forEach((field) => {
      const el = document.getElementById(`prop-${field.key}`);
      if (el) {
        let value;

        if (field.type === "boolean") {
          value = el.checked;
        } else if (field.type === "number") {
          value = parseFloat(el.value);
          if (isNaN(value)) value = 0;
        } else if (field.type === "textarea" && field.key.includes("json")) {
          // Try to parse JSON if field key suggests JSON content
          try {
            value = JSON.parse(el.value);
          } catch (e) {
            value = el.value;
          }
        } else {
          value = el.value;
        }

        // Only add non-empty values to config
        if (value !== "" && value !== null && value !== undefined) {
          config[field.key] = value;
        }
      }
    });

    // Update node data
    this.currentNode.data({
      type: type,
      config: config,
      label: config.label || NodeTypes.getTypeInfo(type).label,
    });

    // Notify listener
    if (this.onPropertiesChanged) {
      this.onPropertiesChanged(this.currentNode);
    }
  }
}
