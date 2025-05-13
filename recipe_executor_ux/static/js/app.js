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

  // Download current recipe
  function downloadRecipe() {
    if (!currentRecipePath) {
      alert("No recipe selected");
      return;
    }

    const recipe = editor.exportRecipe();
    recipe.path = currentRecipePath;

    RecipeService.downloadRecipe(recipe);
  }

  // Handle file upload
  function setupFileUpload() {
    // Create hidden file input
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".json";
    fileInput.style.display = "none";
    document.body.appendChild(fileInput);

    // Handle file selection
    fileInput.addEventListener("change", async (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        try {
          // Show loading indicator
          const uploadBtn = document.getElementById("upload-btn");
          if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.textContent = "Uploading...";
          }

          // Upload the file
          const result = await RecipeService.uploadRecipe(file);

          // Reset file input
          fileInput.value = "";

          // Reset button
          if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.textContent = "Upload";
          }

          if (result.success) {
            // Reload the recipe list
            await recipeList.loadRecipes();

            // Load the uploaded recipe
            await loadRecipe(result.path, result.recipe);

            // Show success message
            alert(`Recipe "${result.filename}" uploaded successfully`);
          } else {
            alert(`Error uploading recipe: ${result.error || "Unknown error"}`);
          }
        } catch (error) {
          console.error("Error uploading file:", error);
          alert(`Error uploading file: ${error.message}`);

          // Reset button
          const uploadBtn = document.getElementById("upload-btn");
          if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.textContent = "Upload";
          }
        }
      }
    });

    // Create the upload button
    const uploadBtn = document.getElementById("upload-btn");
    if (uploadBtn) {
      uploadBtn.addEventListener("click", () => {
        fileInput.click();
      });
    }

    // Create the download button
    const downloadBtn = document.getElementById("download-btn");
    if (downloadBtn) {
      downloadBtn.addEventListener("click", downloadRecipe);
    }
  }

  // Set up palette drag and drop
  setupPaletteDragDrop(editor);

  // Set up file upload/download
  setupFileUpload();

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
