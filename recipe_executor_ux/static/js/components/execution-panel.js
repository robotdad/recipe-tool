/**
 * Execution panel component
 */
import { ExecutionService } from "../services/execution-service.js";

export class ExecutionPanel {
  /**
   * Create an execution panel
   */
  constructor() {
    // Get UI elements
    this.statusEl = document.getElementById("execution-status");
    this.statusTextEl = document.getElementById("status-text");
    this.logsEl = document.getElementById("execution-logs");
    this.logsContentEl = document.getElementById("logs-content");
    this.contextVarsEl = document.getElementById("context-vars");

    this.currentRecipePath = null;
    this.currentExecutionId = null;

    // Init execute button
    const executeBtn = document.getElementById("execute-btn");
    if (executeBtn) {
      executeBtn.addEventListener("click", () => this.executeRecipe());
    }
  }

  /**
   * Set the current recipe
   * @param {string} recipePath - Recipe path
   */
  setRecipe(recipePath) {
    this.currentRecipePath = recipePath;
  }

  /**
   * Execute the current recipe
   */
  async executeRecipe() {
    if (!this.currentRecipePath) {
      this._showError("No recipe selected");
      return;
    }

    // Reset UI
    this._resetUI();

    // Get context variables
    const contextVarsText = this.contextVarsEl.value;

    // Execute recipe
    try {
      this.currentExecutionId = await ExecutionService.executeRecipe(
        this.currentRecipePath,
        contextVarsText,
        {
          onStatus: (status) => this._updateStatus(status),
          onLog: (logs) => this._appendLogs(logs),
          onError: (error) => this._showError(error || "Execution failed"),
        }
      );
    } catch (error) {
      this._showError(`Failed to start execution: ${error.message}`);
    }
  }

  /**
   * Reset UI state
   * @private
   */
  _resetUI() {
    // Show execution panels
    this.statusEl.classList.remove("hidden");
    this.logsEl.classList.remove("hidden");

    // Reset status
    this.statusTextEl.textContent = "pending";
    this.statusTextEl.className = "status-pending";

    // Clear logs
    this.logsContentEl.textContent = "";
  }

  /**
   * Update execution status
   * @param {string} status - Status value
   * @private
   */
  _updateStatus(status) {
    this.statusTextEl.textContent = status;
    this.statusTextEl.className = `status-${status}`;
  }

  /**
   * Append logs
   * @param {Array} logs - Log entries
   * @private
   */
  _appendLogs(logs) {
    if (Array.isArray(logs)) {
      this.logsContentEl.textContent += logs.join("\n") + "\n";
      this.logsContentEl.scrollTop = this.logsContentEl.scrollHeight;
    }
  }

  /**
   * Show error
   * @param {string} message - Error message
   * @private
   */
  _showError(message) {
    this.statusEl.classList.remove("hidden");
    this.statusTextEl.textContent = "error";
    this.statusTextEl.className = "status-failed";

    // Add to logs if visible
    if (!this.logsEl.classList.contains("hidden")) {
      this.logsContentEl.textContent += `ERROR: ${message}\n`;
      this.logsContentEl.scrollTop = this.logsContentEl.scrollHeight;
    } else {
      // Show logs panel
      this.logsEl.classList.remove("hidden");
      this.logsContentEl.textContent = `ERROR: ${message}\n`;
    }

    console.error("Execution error:", message);
  }
}
