/**
 * Recipe list component
 */
import { RecipeService } from "../services/recipe-service.js";

export class RecipeList {
  /**
   * Create a recipe list component
   * @param {string} containerId - Container element ID
   * @param {function} onRecipeSelected - Callback when recipe is selected
   */
  constructor(containerId, onRecipeSelected) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.onRecipeSelected = onRecipeSelected;
    this.recipes = [];
    this.selectedRecipeId = null;

    this._initEventListeners();
  }

  /**
   * Initialize event listeners
   * @private
   */
  _initEventListeners() {
    // New recipe button
    const newRecipeBtn = document.getElementById("new-recipe-btn");
    if (newRecipeBtn) {
      newRecipeBtn.addEventListener("click", () => this._createNewRecipe());
    }

    // Search filter
    const searchInput = document.getElementById("recipe-search");
    if (searchInput) {
      searchInput.addEventListener("input", (e) =>
        this._filterRecipes(e.target.value)
      );
    }
  }

  /**
   * Load recipes from server
   * @returns {Promise<Array>} - List of recipes
   */
  async loadRecipes() {
    try {
      this.recipes = await RecipeService.loadRecipes();
      this._renderRecipeList();
      return this.recipes;
    } catch (error) {
      console.error("Failed to load recipes:", error);
      this._showError("Failed to load recipes");
      return [];
    }
  }

  /**
   * Create new recipe
   * @private
   */
  _createNewRecipe() {
    const name = prompt("Enter recipe name:");
    if (name) {
      const newRecipe = RecipeService.createNewRecipe(name);
      // Notify callback
      if (this.onRecipeSelected) {
        this.onRecipeSelected(newRecipe.path, newRecipe);
      }
    }
  }

  /**
   * Filter recipes by search term
   * @param {string} searchTerm - Search term
   * @private
   */
  _filterRecipes(searchTerm) {
    if (!searchTerm) {
      // Show all recipes
      this.container.querySelectorAll("li").forEach((li) => {
        li.style.display = "block";
      });
      return;
    }

    // Filter by name
    const term = searchTerm.toLowerCase();
    this.container.querySelectorAll("li").forEach((li) => {
      const text = li.textContent.toLowerCase();
      li.style.display = text.includes(term) ? "block" : "none";
    });
  }

  /**
   * Render recipe list
   * @private
   */
  _renderRecipeList() {
    if (!this.container) return;

    this.container.innerHTML = "";

    this.recipes.forEach((recipe) => {
      const li = document.createElement("li");
      li.textContent = recipe.name;
      li.dataset.path = recipe.path;
      li.dataset.id = recipe.id;

      // Add description as tooltip if available
      if (recipe.description) {
        li.title = recipe.description;
      }

      // Mark as selected if this is the current recipe
      if (recipe.path === this.selectedRecipeId) {
        li.classList.add("selected");
      }

      // Select recipe on click
      li.addEventListener("click", () => {
        this._selectRecipe(recipe.path);
      });

      this.container.appendChild(li);
    });
  }

  /**
   * Select a recipe
   * @param {string} path - Recipe path
   * @private
   */
  _selectRecipe(path) {
    // Update UI
    this.container.querySelectorAll("li").forEach((li) => {
      li.classList.toggle("selected", li.dataset.path === path);
    });

    this.selectedRecipeId = path;

    // Notify callback
    if (this.onRecipeSelected) {
      this.onRecipeSelected(path);
    }
  }

  /**
   * Show error message
   * @param {string} message - Error message
   * @private
   */
  _showError(message) {
    console.error(message);
    // Simple alert for now, could be improved with a UI component
    alert(message);
  }
}
