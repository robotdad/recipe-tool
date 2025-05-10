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

    eventSource.onerror = () => {
      eventSource.close();
      if (callbacks.onError) {
        callbacks.onError();
      }
    };

    return {
      close: () => eventSource.close(),
    };
  },
};
