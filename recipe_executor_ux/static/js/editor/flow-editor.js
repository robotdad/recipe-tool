/**
 * Flow Editor for recipe steps
 */
import { PropertiesPanel } from "../components/properties-panel.js";
import { NodeTypes } from "./node-types.js";

export class FlowEditor {
  /**
   * Create a flow editor
   * @param {string} containerId - Container element ID
   */
  constructor(containerId) {
    this.containerId = containerId;
    this.cy = null;
    this.selectedNode = null;
    this.edgeHandles = null;

    // Initialize properties panel
    this.propertiesPanel = new PropertiesPanel("node-properties", (node) => {
      this.updateNodeAppearance(node);
    });

    this.initCytoscape();
    this.initEdgeHandling();
    this.attachEventListeners();
  }

  /**
   * Initialize Cytoscape instance
   */
  initCytoscape() {
    // Register the dagre layout extension if needed
    if (cytoscape.use) {
      cytoscape.use(cytoscapeDagre);
    }

    this.cy = cytoscape({
      container: document.getElementById(this.containerId),
      style: [
        {
          // Default node style
          selector: "node",
          style: {
            shape: "roundrectangle",
            width: "160px",
            height: "60px",
            "text-wrap": "wrap",
            "font-size": "12px",
            "text-valign": "center",
            "text-halign": "center",
            "background-color": "#f5f5f5",
            "border-width": 1,
            "border-color": "#ddd",
          },
        },
        {
          // Style for nodes with label data
          selector: "node[label]",
          style: {
            label: "data(label)",
          },
        },
        {
          // Style for nodes with color data
          selector: "node[color]",
          style: {
            "background-color": "data(color)",
          },
        },
        {
          // Edge style
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#ccc",
            "target-arrow-color": "#ccc",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "arrow-scale": 1.2,
          },
        },
        {
          // Selected element style
          selector: ":selected",
          style: {
            "border-width": 3,
            "border-color": "#333",
            "line-color": "#333",
            "target-arrow-color": "#333",
          },
        },
      ],
      layout: {
        name: "dagre",
        rankDir: "TB",
        nodeSep: 50,
        rankSep: 100,
        fit: true,
        padding: 50,
      },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: true,
      maxZoom: 3,
      minZoom: 0.2,
      wheelSensitivity: 0.3,
    });
  }

  /**
   * Initialize edge handling
   */
  initEdgeHandling() {
    if (!this.cy.edgehandles) {
      console.warn("EdgeHandles extension not available");
      return;
    }

    // Initialize edge creation extension
    this.edgeHandles = this.cy.edgehandles({
      handleNodes: "node", // Allow edge creation from any node
      handleSize: 10,
      handleColor: "#ff0000",
      handleHitThreshold: 6,
      handleLineWidth: 1,
      handleLineColor: "#ff0000",
      handleOutlineColor: "#ffffff",
      handleOutlineWidth: 2,
      edgeType: function () {
        return "bezier";
      },
      complete: (sourceNode, targetNode, addedEles) => {
        console.log("Edge created:", sourceNode.id(), "to", targetNode.id());
      },
    });

    // Add right-click context menu for starting edge creation
    this.cy.on("cxttap", "node", (evt) => {
      // Make sure node has required data
      const node = evt.target;

      // Add any missing data
      this._ensureNodeData(node);

      // Start edge creation
      this.edgeHandles.start(node);
    });
  }

  /**
   * Attach event listeners to Cytoscape instance
   */
  attachEventListeners() {
    // Node selection
    this.cy.on("select", "node", (evt) => {
      this.selectedNode = evt.target;
      this.propertiesPanel.showNodeProperties(this.selectedNode);
    });

    // Node deselection
    this.cy.on("unselect", "node", () => {
      this.selectedNode = null;
      this.propertiesPanel.clear();
    });

    // Delete key to remove elements
    document.addEventListener("keydown", (e) => {
      if (e.key === "Delete" && this.cy.$(":selected").length > 0) {
        this.cy.$(":selected").remove();
      }
    });
  }

  /**
   * Update node appearance based on its data
   * @param {object} node - Cytoscape node
   * @returns {object} - The updated node
   */
  updateNodeAppearance(node) {
    const data = node.data();
    const typeInfo = NodeTypes.getTypeInfo(data.type);

    // Update node style
    node.style({
      "background-color": data.color || typeInfo.color || "#ccc",
      shape: "roundrectangle",
      width: 160,
      height: 60,
      label: data.label || typeInfo.label || data.type,
      "text-valign": "center",
      "text-halign": "center",
      "text-wrap": "wrap",
    });

    return node;
  }

  /**
   * Add a new node to the graph
   * @param {string} type - Node type
   * @param {object} position - Position {x, y}
   * @returns {object} - The new node
   */
  addNode(type, position) {
    const typeInfo = NodeTypes.getTypeInfo(type);
    const id = "node-" + Date.now();

    // Create node with minimum required data
    const node = this.cy.add({
      group: "nodes",
      data: {
        id: id,
        type: type,
        label: typeInfo.label || type,
        color: typeInfo.color,
        icon: typeInfo.icon,
        config: {},
      },
      position: position,
    });

    // Select the new node
    node.select();

    return node;
  }

  /**
   * Clear the editor
   */
  clear() {
    this.cy.elements().remove();
    this.propertiesPanel.clear();
  }

  /**
   * Load a recipe into the editor
   * @param {object} recipe - Recipe object
   */
  loadRecipe(recipe) {
    this.clear();

    if (!recipe || !recipe.steps || !Array.isArray(recipe.steps)) {
      console.error("Invalid recipe format");
      return;
    }

    const steps = recipe.steps;
    const nodes = [];

    // Add nodes
    steps.forEach((step, index) => {
      const typeInfo = NodeTypes.getTypeInfo(step.type);

      const node = this.cy.add({
        group: "nodes",
        data: {
          id: "step-" + index,
          type: step.type,
          label: step.config?.label || typeInfo.label || step.type,
          color: typeInfo.color,
          icon: typeInfo.icon,
          config: step.config || {},
        },
      });

      nodes.push(node);
    });

    // Add edges
    for (let i = 0; i < nodes.length - 1; i++) {
      this.cy.add({
        group: "edges",
        data: {
          source: nodes[i].id(),
          target: nodes[i + 1].id(),
        },
      });
    }

    // Run layout
    this.cy
      .layout({
        name: "dagre",
        rankDir: "TB",
        padding: 50,
        fit: true,
      })
      .run();
  }

  /**
   * Export the current graph as a recipe
   * @returns {object} - Recipe object
   */
  exportRecipe() {
    const nodes = this._getSortedNodes();

    const steps = nodes.map((node) => {
      const data = node.data();
      const config = this._cleanConfig(data.config || {});

      return {
        type: data.type,
        config: config,
      };
    });

    return {
      steps: steps,
    };
  }

  /**
   * Clean config object by removing empty values
   * @param {object} config - Config object to clean
   * @returns {object} - Cleaned config object
   * @private
   */
  _cleanConfig(config) {
    const cleanedConfig = {};

    for (const [key, value] of Object.entries(config)) {
      // Skip empty strings, null, and undefined values
      if (value === "" || value === null || value === undefined) {
        continue;
      }

      // Handle objects recursively (but keep arrays as-is)
      if (
        typeof value === "object" &&
        value !== null &&
        !Array.isArray(value)
      ) {
        const cleanedSubConfig = this._cleanConfig(value);

        // Only add non-empty objects
        if (Object.keys(cleanedSubConfig).length > 0) {
          cleanedConfig[key] = cleanedSubConfig;
        }
      } else {
        cleanedConfig[key] = value;
      }
    }

    return cleanedConfig;
  }

  /**
   * Get nodes sorted by position or connectivity
   * @returns {Array} - Sorted nodes
   * @private
   */
  _getSortedNodes() {
    // First try to sort by connectivity (following edges)
    const connectedNodes = this._getConnectedNodes();
    if (connectedNodes.length > 0) {
      return connectedNodes;
    }

    // Fall back to position-based sort
    return this.cy.nodes().sort((a, b) => {
      const aPos = a.position();
      const bPos = b.position();
      return aPos.y - bPos.y || aPos.x - bPos.x;
    });
  }

  /**
   * Get nodes ordered by connectivity
   * @returns {Array} - Ordered nodes
   * @private
   */
  _getConnectedNodes() {
    const orderedNodes = [];
    const allNodes = this.cy.nodes();

    // Find root nodes (nodes with no incoming edges)
    const rootNodes = allNodes.filter((node) => {
      return node.incomers("edge").length === 0;
    });

    // If no root nodes, return empty array
    if (rootNodes.length === 0) {
      return [];
    }

    // For each root node, traverse the graph
    rootNodes.forEach((rootNode) => {
      this._traverseFromNode(rootNode, orderedNodes, new Set());
    });

    // Add any remaining nodes
    allNodes.forEach((node) => {
      if (!orderedNodes.includes(node)) {
        orderedNodes.push(node);
      }
    });

    return orderedNodes;
  }

  /**
   * Traverse graph from a node
   * @param {object} node - Starting node
   * @param {Array} result - Result array
   * @param {Set} visited - Set of visited node IDs
   * @private
   */
  _traverseFromNode(node, result, visited) {
    const nodeId = node.id();

    // Skip if already visited
    if (visited.has(nodeId)) {
      return;
    }

    // Add to result and mark as visited
    result.push(node);
    visited.add(nodeId);

    // Get outgoing edges
    const outEdges = node.outgoers("edge");

    // Process targets
    outEdges.forEach((edge) => {
      const target = edge.target();
      this._traverseFromNode(target, result, visited);
    });
  }

  /**
   * Ensure a node has all required data fields
   * @param {object} node - Cytoscape node
   * @private
   */
  _ensureNodeData(node) {
    const data = node.data();
    const type = data.type || "unknown";
    const typeInfo = NodeTypes.getTypeInfo(type);

    // Ensure required fields are present
    if (!data.label) {
      node.data("label", typeInfo.label || type);
    }

    if (!data.color) {
      node.data("color", typeInfo.color || "#ccc");
    }

    if (!data.icon) {
      node.data("icon", typeInfo.icon || "❓");
    }

    if (!data.config) {
      node.data("config", {});
    }
  }
}
