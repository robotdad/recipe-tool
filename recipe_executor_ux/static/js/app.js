/**
 * Main application entry point
 */
import { ExecutionPanel } from "./components/execution-panel.js";
import { RecipeList } from "./components/recipe-list.js";
import { FlowEditor } from "./editor/flow-editor.js";
import { RecipeService } from "./services/recipe-service.js";

document.addEventListener("DOMContentLoaded", async () => {
  // Initialize components
  const editor = new FlowEditor("flow-editor");
  const recipeList = new RecipeList("recipe-list-container", loadRecipe);
  const executionPanel = new ExecutionPanel();

  let currentRecipePath = null;

  // Load recipes
  await recipeList.loadRecipes();

  // Load recipe
  async function loadRecipe(path, preloadedRecipe = null) {
    try {
      // If we already have the recipe data, use it
      const recipe = preloadedRecipe || (await RecipeService.loadRecipe(path));

      // Update state
      currentRecipePath = path;
      document.getElementById("recipe-name").value = path
        .split("/")
        .pop()
        .replace(".json", "");

      // Update UI
      editor.loadRecipe(recipe);
      executionPanel.setRecipe(path);
    } catch (error) {
      console.error(`Error loading recipe: ${error}`);
      alert(`Failed to load recipe: ${error.message}`);
    }
  }

  // Save recipe
  async function saveRecipe() {
    if (!currentRecipePath) {
      alert("No recipe selected");
      return;
    }

    try {
      const recipe = editor.exportRecipe();
      recipe.path = currentRecipePath;

      // Validate recipe
      const validation = RecipeService.validateRecipe(recipe);
      if (!validation.valid) {
        alert(`Invalid recipe: ${validation.errors.join(", ")}`);
        return;
      }

      const result = await RecipeService.saveRecipe(recipe);
      if (result.success) {
        alert("Recipe saved successfully");
      } else {
        alert(`Error saving recipe: ${result.error || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error saving recipe:", error);
      alert(`Error saving recipe: ${error.message}`);
    }
  }

  // View recipe JSON
  function viewRecipeJson() {
    const recipe = editor.exportRecipe();
    const jsonEditor = document.getElementById("json-editor");
    jsonEditor.value = JSON.stringify(recipe, null, 2);

    document.getElementById("json-modal").classList.remove("hidden");
  }

  // Apply JSON changes
  function applyJsonChanges() {
    const jsonEditor = document.getElementById("json-editor");
    try {
      const recipe = JSON.parse(jsonEditor.value);

      // Validate recipe
      const validation = RecipeService.validateRecipe(recipe);
      if (!validation.valid) {
        alert(`Invalid recipe: ${validation.errors.join(", ")}`);
        return;
      }

      editor.loadRecipe(recipe);
      document.getElementById("json-modal").classList.add("hidden");
    } catch (error) {
      alert("Invalid JSON: " + error.message);
    }
  }

  // Set up palette drag and drop
  setupPaletteDragDrop(editor);

  // Event listeners
  document.getElementById("save-btn").addEventListener("click", saveRecipe);
  document
    .getElementById("view-json-btn")
    .addEventListener("click", viewRecipeJson);
  document
    .getElementById("apply-json-btn")
    .addEventListener("click", applyJsonChanges);
  document.getElementById("cancel-json-btn").addEventListener("click", () => {
    document.getElementById("json-modal").classList.add("hidden");
  });
  document.querySelector(".close-btn").addEventListener("click", () => {
    document.getElementById("json-modal").classList.add("hidden");
  });
});

/**
 * Setup palette drag and drop
 * @param {FlowEditor} editor - Flow editor instance
 */
function setupPaletteDragDrop(editor) {
  const palette = document.querySelector(".node-palette");
  const paletteHeader = document.querySelector(".palette-header");
  const flowEditorEl = document.getElementById("flow-editor");

  // Make palette draggable
  if (paletteHeader) {
    paletteHeader.addEventListener("mousedown", function (e) {
      let offsetX = e.clientX - palette.getBoundingClientRect().left;
      let offsetY = e.clientY - palette.getBoundingClientRect().top;

      function movePanel(e) {
        palette.style.left = e.clientX - offsetX + "px";
        palette.style.top = e.clientY - offsetY + "px";
      }

      function stopMoving() {
        document.removeEventListener("mousemove", movePanel);
        document.removeEventListener("mouseup", stopMoving);
      }

      document.addEventListener("mousemove", movePanel);
      document.addEventListener("mouseup", stopMoving);
    });
  }

  // Set up item drag
  document.querySelectorAll(".palette-item").forEach((item) => {
    item.setAttribute("draggable", "true");

    // Drag start
    item.addEventListener("dragstart", (e) => {
      console.log("Drag started for", item.textContent);
      e.dataTransfer.setData("text/plain", item.dataset.type);
      e.dataTransfer.setData("application/recipe-type", item.dataset.type);
      e.dataTransfer.effectAllowed = "copy";

      // Create drag image
      const dragIcon = item.cloneNode(true);
      dragIcon.style.width = "150px";
      dragIcon.style.height = "40px";
      dragIcon.style.background = "#fff";
      dragIcon.style.border = "1px solid #ccc";
      dragIcon.style.borderRadius = "4px";
      dragIcon.style.padding = "8px";
      document.body.appendChild(dragIcon);
      dragIcon.style.position = "absolute";
      dragIcon.style.top = "-1000px";
      e.dataTransfer.setDragImage(dragIcon, 75, 20);

      // Clean up
      setTimeout(() => {
        document.body.removeChild(dragIcon);
      }, 0);
    });

    // Click to add
    item.addEventListener("click", () => {
      const type = item.dataset.type;
      const center = {
        x: editor.cy.width() / 2,
        y: editor.cy.height() / 2,
      };
      editor.addNode(type, center);
    });
  });

  // Make editor a drop target
  if (flowEditorEl) {
    // Add style for drag over indication
    const style = document.createElement("style");
    style.textContent = `
      #flow-editor.drag-over {
        outline: 2px dashed #3498db;
        outline-offset: -2px;
      }
    `;
    document.head.appendChild(style);

    flowEditorEl.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
      flowEditorEl.classList.add("drag-over");
    });

    flowEditorEl.addEventListener("dragleave", () => {
      flowEditorEl.classList.remove("drag-over");
    });

    flowEditorEl.addEventListener("drop", (e) => {
      e.preventDefault();
      flowEditorEl.classList.remove("drag-over");

      // Get node type
      const type =
        e.dataTransfer.getData("application/recipe-type") ||
        e.dataTransfer.getData("text/plain");

      if (type) {
        // Calculate position in canvas
        const rect = flowEditorEl.getBoundingClientRect();
        const position = {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        };

        // Add node
        editor.addNode(type, position);
      }
    });
  }
}
