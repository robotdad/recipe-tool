/**
 * API Service - Core communication with the backend
 */
export const ApiService = {
  /**
   * Get list of recipes
   * @param {string} directory - Optional directory to filter recipes
   * @returns {Promise<object>} - List of recipes
   */
  async getRecipes(directory = "recipes") {
    const url = `/api/recipes?directory=${encodeURIComponent(directory)}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Error fetching recipes: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Get recipe by ID/path
   * @param {string} id - Recipe ID or path
   * @returns {Promise<object>} - Recipe data
   */
  async getRecipe(id) {
    // Make sure the id is properly encoded for URL path segments
    // without double-encoding slashes
    const encodedPath = id
      .split("/")
      .map((segment) => encodeURIComponent(segment))
      .join("/");

    const response = await fetch(`/api/recipes/${encodedPath}`);
    if (!response.ok) {
      throw new Error(`Error loading recipe: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Save recipe
   * @param {object} recipe - Recipe object to save
   * @returns {Promise<object>} - Save result
   */
  async saveRecipe(recipe) {
    const response = await fetch("/api/recipes/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(recipe),
    });

    if (!response.ok) {
      throw new Error(`Error saving recipe: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Execute recipe
   * @param {string} recipePath - Path to recipe
   * @param {object} contextVars - Context variables
   * @returns {Promise<object>} - Execution result
   */
  async executeRecipe(recipePath, contextVars) {
    const response = await fetch("/api/recipes/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipe_path: recipePath,
        context_vars: contextVars,
      }),
    });

    if (!response.ok) {
      throw new Error(`Error executing recipe: ${response.statusText}`);
    }
    return response.json();
  },

  /**
   * Create SSE connection for execution logs
   * @param {string} executionId - Execution ID
   * @param {object} callbacks - Callback functions
   * @returns {object} - Connection controller
   */
  createExecutionStream(executionId, callbacks) {
    const eventSource = new EventSource(`/api/execution/${executionId}/stream`);

    if (callbacks.onStatus) {
      eventSource.addEventListener("status", callbacks.onStatus);
    }

    if (callbacks.onLog) {
      eventSource.addEventListener("log", callbacks.onLog);
    }

    // Keep track of whether we're in a final state
    let receivedFinalStatus = false;

    // Special handling for status events to track final status
    const originalStatusHandler = callbacks.onStatus;
    if (originalStatusHandler) {
      eventSource.removeEventListener("status", originalStatusHandler);
      eventSource.addEventListener("status", (event) => {
        // Check if this is a final status
        if (["completed", "failed"].includes(event.data)) {
          receivedFinalStatus = true;
        }
        originalStatusHandler(event);
      });
    }

    eventSource.onerror = (event) => {
      // Only call the error handler if this wasn't an expected closure after completion
      if (!receivedFinalStatus && callbacks.onError) {
        callbacks.onError(event);
      } else {
        console.log(
          "EventSource connection ended normally after execution completed"
        );
      }
      eventSource.close();
    };

    return {
      close: () => eventSource.close(),
    };
  },

  /**
   * Upload recipe file
   * @param {File} file - File to upload
   * @param {string} directory - Target directory
   * @returns {Promise<object>} - Upload result
   */
  async uploadRecipe(file, directory = "recipes") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("directory", directory);

    const response = await fetch("/api/recipes/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error uploading recipe: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Download recipe as JSON file
   * @param {object} recipe - Recipe to download
   * @param {string} filename - Filename to use
   */
  downloadRecipe(recipe, filename) {
    // Create clean copy of the recipe
    const cleanRecipe = this._cleanRecipeForDownload(recipe);

    // Convert to JSON
    const json = JSON.stringify(cleanRecipe, null, 2);

    // Create blob
    const blob = new Blob([json], { type: "application/json" });

    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "recipe.json";

    // Trigger download
    document.body.appendChild(a);
    a.click();

    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  },

  /**
   * Clean recipe for download
   * @param {object} recipe - Recipe to clean
   * @returns {object} - Cleaned recipe
   * @private
   */
  _cleanRecipeForDownload(recipe) {
    // Make a deep copy
    const cleanedRecipe = JSON.parse(JSON.stringify(recipe));

    // Remove any UI-specific properties
    delete cleanedRecipe.ui;

    // Return only the essential properties
    return {
      steps: cleanedRecipe.steps,
      ...(cleanedRecipe.description && {
        description: cleanedRecipe.description,
      }),
      ...(cleanedRecipe.name && { name: cleanedRecipe.name }),
    };
  },
};
