/**
 * Recipe Service - Manages recipe operations
 */
import { ApiService } from "./api.js";

export const RecipeService = {
  /**
   * Load all recipes
   * @param {string} directory - Optional directory path
   * @returns {Promise<Array>} - List of recipes
   */
  async loadRecipes(directory = "recipes") {
    try {
      const data = await ApiService.getRecipes(directory);
      return data.recipes || [];
    } catch (error) {
      console.error("Failed to load recipes:", error);
      return [];
    }
  },

  /**
   * Load recipe by path
   * @param {string} path - Recipe path
   * @returns {Promise<object>} - Recipe data
   */
  async loadRecipe(path) {
    try {
      return await ApiService.getRecipe(path);
    } catch (error) {
      console.error(`Failed to load recipe ${path}:`, error);
      throw error;
    }
  },

  /**
   * Save recipe
   * @param {object} recipe - Recipe object to save
   * @returns {Promise<object>} - Save result
   */
  async saveRecipe(recipe) {
    try {
      // Clean the recipe before saving
      const cleanedRecipe = this.cleanRecipe(recipe);
      return await ApiService.saveRecipe(cleanedRecipe);
    } catch (error) {
      console.error("Failed to save recipe:", error);
      throw error;
    }
  },

  /**
   * Clean recipe data by removing empty values
   * @param {object} recipe - Recipe to clean
   * @returns {object} - Cleaned recipe
   */
  cleanRecipe(recipe) {
    // Create a deep copy to avoid modifying the original
    const cleanedRecipe = JSON.parse(JSON.stringify(recipe));

    // Clean steps
    if (cleanedRecipe.steps && Array.isArray(cleanedRecipe.steps)) {
      cleanedRecipe.steps = cleanedRecipe.steps.map((step) => {
        if (step.config) {
          step.config = this._cleanObject(step.config);
        }
        return step;
      });
    }

    return cleanedRecipe;
  },

  /**
   * Recursively clean an object by removing empty values
   * @param {object} obj - Object to clean
   * @returns {object} - Cleaned object
   * @private
   */
  _cleanObject(obj) {
    const cleaned = {};

    Object.entries(obj).forEach(([key, value]) => {
      // Skip empty strings, null, and undefined
      if (value === "" || value === null || value === undefined) {
        return;
      }

      // Handle objects recursively (but keep arrays as-is)
      if (
        typeof value === "object" &&
        value !== null &&
        !Array.isArray(value)
      ) {
        const cleanedValue = this._cleanObject(value);

        // Only add if the cleaned object has properties
        if (Object.keys(cleanedValue).length > 0) {
          cleaned[key] = cleanedValue;
        }
      } else {
        cleaned[key] = value;
      }
    });

    return cleaned;
  },

  /**
   * Create new recipe
   * @param {string} name - Recipe name
   * @returns {object} - New recipe object
   */
  createNewRecipe(name) {
    return {
      path: `recipes/${name}.json`,
      steps: [],
    };
  },

  /**
   * Validate recipe structure
   * @param {object} recipe - Recipe to validate
   * @returns {object} - Validation result {valid: boolean, errors: Array}
   */
  validateRecipe(recipe) {
    const errors = [];

    // Check for required properties
    if (!recipe.steps) {
      errors.push("Recipe must have a steps array");
    } else if (!Array.isArray(recipe.steps)) {
      errors.push("Recipe steps must be an array");
    } else {
      // Validate each step
      recipe.steps.forEach((step, index) => {
        if (!step.type) {
          errors.push(`Step ${index + 1} is missing a type`);
        }
        if (!step.config) {
          errors.push(`Step ${index + 1} is missing a config object`);
        } else if (typeof step.config !== "object") {
          errors.push(
            `Step ${index + 1} has an invalid config (must be an object)`
          );
        }
      });
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  },

  /**
   * Upload recipe file
   * @param {File} file - File to upload
   * @returns {Promise<object>} - Upload result with recipe data
   */
  async uploadRecipe(file) {
    try {
      const result = await ApiService.uploadRecipe(file);
      return result;
    } catch (error) {
      console.error("Failed to upload recipe:", error);
      throw error;
    }
  },

  /**
   * Download current recipe
   * @param {object} recipe - Recipe object
   * @param {string} filename - Optional filename
   */
  downloadRecipe(recipe, filename) {
    // Generate filename if not provided
    if (!filename) {
      if (recipe.path) {
        // Extract filename from path
        const pathParts = recipe.path.split("/");
        filename = pathParts[pathParts.length - 1];
      } else if (recipe.name) {
        filename = `${recipe.name}.json`;
      } else {
        filename = "recipe.json";
      }
    }

    // Ensure it has .json extension
    if (!filename.toLowerCase().endsWith(".json")) {
      filename += ".json";
    }

    // Download the file
    ApiService.downloadRecipe(recipe, filename);
  },
};
