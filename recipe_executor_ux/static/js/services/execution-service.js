/**
 * Execution Service - Manages recipe execution
 */
import { ApiService } from "./api.js";

export const ExecutionService = {
  // Current execution stream if any
  currentStream: null,

  /**
   * Execute recipe
   * @param {string} recipePath - Path to recipe
   * @param {string} contextVarsText - Context variables as text
   * @param {object} callbacks - Callback functions
   * @returns {Promise<string>} - Execution ID
   */
  async executeRecipe(recipePath, contextVarsText, callbacks) {
    try {
      // Parse context variables
      const contextVars = this._parseContextVars(contextVarsText);

      // Execute recipe
      const result = await ApiService.executeRecipe(recipePath, contextVars);

      // Setup streaming if execution started successfully
      if (result.execution_id) {
        this._setupStreaming(result.execution_id, callbacks);
        return result.execution_id;
      }

      return null;
    } catch (error) {
      console.error("Failed to execute recipe:", error);
      if (callbacks.onError) {
        callbacks.onError(error.message);
      }
      return null;
    }
  },

  /**
   * Close current execution stream
   */
  closeStream() {
    if (this.currentStream) {
      this.currentStream.close();
      this.currentStream = null;
    }
  },

  /**
   * Parse context variables from text
   * @param {string} text - Context variables as text
   * @returns {object} - Context variables as object
   * @private
   */
  _parseContextVars(text) {
    const vars = {};
    if (!text) return vars;

    text.split("\n").forEach((line) => {
      const parts = line.split("=");
      if (parts.length >= 2) {
        const key = parts[0].trim();
        // Join with = in case there are = in the value
        const value = parts.slice(1).join("=").trim();
        if (key) {
          vars[key] = value;
        }
      }
    });
    return vars;
  },

  /**
   * Setup streaming for execution
   * @param {string} executionId - Execution ID
   * @param {object} callbacks - Callback functions
   * @private
   */
  _setupStreaming(executionId, callbacks) {
    // Close existing stream if any
    this.closeStream();

    // Create new stream
    this.currentStream = ApiService.createExecutionStream(executionId, {
      onStatus: (event) => {
        if (callbacks.onStatus) {
          callbacks.onStatus(event.data);
        }

        // Auto-close stream on completion
        if (["completed", "failed"].includes(event.data)) {
          this.closeStream();
        }
      },
      onLog: (event) => {
        if (callbacks.onLog) {
          const logs = JSON.parse(event.data);
          callbacks.onLog(logs);
        }
      },
      onError: () => {
        if (callbacks.onError) {
          callbacks.onError("Connection to execution stream lost");
        }
      },
    });
  },
};
