// src/nodes/execute_recipe.js
// ES module for Execute Recipe Drawflow node

/**
 * Registers the 'execute_recipe' node type with the Drawflow editor.
 * @param {import('drawflow').Drawflow} editor - Drawflow editor instance
 */
export function registerExecuteRecipe(editor) {
  // HTML template for the node
  const html = `
  <div class="node execute-recipe-node">
    <label>Recipe Path:</label>
    <input type="text" df-recipe_path placeholder="Enter recipe path to sub-recipe.json" />

    <label>Context Overrides (JSON):</label>
    <textarea df-context_overrides placeholder="{}"></textarea>
    <div class="error-message" style="display:none; color: red;">Invalid JSON</div>
  </div>`;

  editor.registerNode('execute_recipe', {
    html,
    onCreate: function(node) {
      const root = node.dom;
      const input = root.querySelector('input[df-recipe_path]');
      const textarea = root.querySelector('textarea[df-context_overrides]');
      const errorDiv = root.querySelector('.error-message');
      
      // Log initial config
      console.debug(
        'onCreate execute_recipe initial config',
        node.data.config.recipe_path,
        node.data.config.context_overrides
      );

      // Initialize values
      input.value = node.data.config.recipe_path || '';
      const initialOverrides = node.data.config.context_overrides || {};
      textarea.value = JSON.stringify(initialOverrides, null, 2);
      let lastValid = initialOverrides;

      // Simple debounce helper
      function debounce(fn, delay) {
        let timer = null;
        return (...args) => {
          clearTimeout(timer);
          timer = setTimeout(() => fn(...args), delay);
        };
      }

      // Handlers
      const onRecipeInput = (e) => {
        const val = e.target.value;
        node.data.config.recipe_path = val;
        console.debug('recipe_path changed:', val);
      };

      const parseOverrides = () => {
        try {
          const text = textarea.value;
          const parsed = JSON.parse(text);
          node.data.config.context_overrides = parsed;
          lastValid = parsed;
          textarea.classList.remove('error');
          errorDiv.style.display = 'none';
          console.debug('context_overrides parsed successfully', parsed);
        } catch (err) {
          console.debug('Failed to parse context_overrides JSON', err);
          textarea.classList.add('error');
          errorDiv.style.display = 'block';
        }
      };

      const debouncedParse = debounce(parseOverrides, 500);

      const onBlur = () => {
        // on blur, if invalid, revert
        if (textarea.classList.contains('error')) {
          textarea.value = JSON.stringify(lastValid, null, 2);
          textarea.classList.remove('error');
          errorDiv.style.display = 'none';
          console.debug('Reverted to last valid context_overrides');
        } else {
          // ensure final parse
          parseOverrides();
        }
      };

      // Attach listeners
      input.addEventListener('input', onRecipeInput);
      textarea.addEventListener('input', debouncedParse);
      textarea.addEventListener('blur', onBlur);

      // Save handlers for cleanup
      root._executeRecipeListeners = { onRecipeInput, debouncedParse, onBlur };
    },

    onUpdate: function(node) {
      const root = node.dom;
      const input = root.querySelector('input[df-recipe_path]');
      const textarea = root.querySelector('textarea[df-context_overrides]');
      const cfg = node.data.config || {};

      input.value = cfg.recipe_path || '';
      const co = cfg.context_overrides || {};
      textarea.value = JSON.stringify(co, null, 2);
    },

    onSelect: function(node) {
      const root = node.dom;
      root.classList.add('selected');
    },

    onDeselect: function(node) {
      const root = node.dom;
      root.classList.remove('selected');
    },

    onDelete: function(node) {
      const root = node.dom;
      const input = root.querySelector('input[df-recipe_path]');
      const textarea = root.querySelector('textarea[df-context_overrides]');
      const { onRecipeInput, debouncedParse, onBlur } = root._executeRecipeListeners || {};

      if (input && onRecipeInput) {
        input.removeEventListener('input', onRecipeInput);
      }
      if (textarea && debouncedParse) {
        textarea.removeEventListener('input', debouncedParse);
      }
      if (textarea && onBlur) {
        textarea.removeEventListener('blur', onBlur);
      }

      delete root._executeRecipeListeners;
    }
  });

  console.info('Registered execute_recipe node type');
}
