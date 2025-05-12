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

    // Keep track of final status to handle delayed logs
    let isFinalStatus = false;
    let logReceiveTimer = null;

    // Create new stream
    this.currentStream = ApiService.createExecutionStream(executionId, {
      onStatus: (event) => {
        const status = event.data;

        if (callbacks.onStatus) {
          callbacks.onStatus(status);
        }

        // Check if this is a final status
        if (["completed", "failed"].includes(status)) {
          isFinalStatus = true;

          // Set a timeout to close the stream, but allow for delayed logs
          if (logReceiveTimer) {
            clearTimeout(logReceiveTimer);
          }

          logReceiveTimer = setTimeout(() => {
            console.log(
              "Closing execution stream after final status and timeout"
            );
            this.closeStream();
          }, 2000); // Wait 2 seconds for any final logs
        }
      },
      onLog: (event) => {
        if (callbacks.onLog) {
          const logs = JSON.parse(event.data);
          callbacks.onLog(logs);

          // If we've received logs after final status, reset the close timer
          if (isFinalStatus && logReceiveTimer) {
            clearTimeout(logReceiveTimer);
            logReceiveTimer = setTimeout(() => {
              console.log(
                "Closing execution stream after receiving delayed logs"
              );
              this.closeStream();
            }, 1000); // Wait 1 second for any more logs
          }
        }
      },
      onError: () => {
        if (callbacks.onError) {
          callbacks.onError("Connection to execution stream lost");
        }
        this.closeStream();
      },
    });
  },
};
