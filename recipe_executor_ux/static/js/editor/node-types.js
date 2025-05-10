/**
 * Node type definitions for the recipe flow editor
 */
export const NodeTypes = {
  // Type definitions with styling and config fields
  types: {
    read_files: {
      color: "#8dd3c7",
      icon: "📁",
      label: "Read Files",
      description: "Read one or more files into the context",
      configFields: [
        {
          key: "path",
          label: "File Path",
          type: "text",
          description: "Path to file(s) to read",
        },
        {
          key: "content_key",
          label: "Content Key",
          type: "text",
          description: "Context key to store content",
        },
        {
          key: "optional",
          label: "Optional",
          type: "boolean",
          description: "Skip missing files",
        },
        {
          key: "merge_mode",
          label: "Merge Mode",
          type: "select",
          description: "How to handle multiple files",
          options: [
            { value: "concat", label: "Concatenate" },
            { value: "dict", label: "Dictionary" },
          ],
        },
      ],
    },
    write_files: {
      color: "#bebada",
      icon: "💾",
      label: "Write Files",
      description: "Write files to disk",
      configFields: [
        {
          key: "files_key",
          label: "Files Key",
          type: "text",
          description: "Context key containing file specs",
        },
        {
          key: "files",
          label: "Files",
          type: "textarea",
          description: "Direct file specifications (JSON)",
        },
        {
          key: "root",
          label: "Root Directory",
          type: "text",
          description: "Base directory for output",
        },
      ],
    },
    set_context: {
      color: "#fb8072",
      icon: "🔄",
      label: "Set Context",
      description: "Set a value in the context",
      configFields: [
        {
          key: "key",
          label: "Context Key",
          type: "text",
          description: "Name of the key to set",
        },
        {
          key: "value",
          label: "Value",
          type: "textarea",
          description: "Value to set (can be template)",
        },
        {
          key: "nested_render",
          label: "Nested Render",
          type: "boolean",
          description: "Render templates recursively",
        },
        {
          key: "if_exists",
          label: "If Exists",
          type: "select",
          description: "How to handle existing keys",
          options: [
            { value: "overwrite", label: "Overwrite" },
            { value: "merge", label: "Merge" },
          ],
        },
      ],
    },
    llm_generate: {
      color: "#80b1d3",
      icon: "🤖",
      label: "LLM Generate",
      description: "Generate content with an LLM",
      configFields: [
        {
          key: "prompt",
          label: "Prompt",
          type: "textarea",
          description: "Prompt to send to the LLM",
        },
        {
          key: "model",
          label: "Model",
          type: "text",
          description: "Model to use (provider/model_name)",
        },
        {
          key: "max_tokens",
          label: "Max Tokens",
          type: "number",
          description: "Maximum tokens in response",
        },
        {
          key: "output_format",
          label: "Output Format",
          type: "select",
          description: "Format of LLM output",
          options: [
            { value: "text", label: "Text" },
            { value: "files", label: "Files" },
          ],
        },
        {
          key: "output_key",
          label: "Output Key",
          type: "text",
          description: "Context key for output",
        },
      ],
    },
    execute_recipe: {
      color: "#fdb462",
      icon: "📋",
      label: "Execute Recipe",
      description: "Run another recipe",
      configFields: [
        {
          key: "recipe_path",
          label: "Recipe Path",
          type: "text",
          description: "Path to recipe file",
        },
        {
          key: "context_overrides",
          label: "Context Overrides",
          type: "textarea",
          description: "Key/value overrides (JSON)",
        },
      ],
    },
    conditional: {
      color: "#b3de69",
      icon: "🔀",
      label: "Conditional",
      description: "Branch based on a condition",
      configFields: [
        {
          key: "condition",
          label: "Condition",
          type: "textarea",
          description: "Condition to evaluate",
        },
        {
          key: "if_true",
          label: "If True",
          type: "textarea",
          description: "Steps to run if true (JSON)",
        },
        {
          key: "if_false",
          label: "If False",
          type: "textarea",
          description: "Steps to run if false (JSON)",
        },
      ],
    },
    loop: {
      color: "#fccde5",
      icon: "🔄",
      label: "Loop",
      description: "Iterate over items",
      configFields: [
        {
          key: "items",
          label: "Items",
          type: "text",
          description: "Collection to iterate over",
        },
        {
          key: "item_key",
          label: "Item Key",
          type: "text",
          description: "Key for current item",
        },
        {
          key: "substeps",
          label: "Substeps",
          type: "textarea",
          description: "Steps to run per item (JSON)",
        },
        {
          key: "result_key",
          label: "Result Key",
          type: "text",
          description: "Key for results",
        },
        {
          key: "max_concurrency",
          label: "Max Concurrency",
          type: "number",
          description: "Maximum concurrent tasks",
        },
        {
          key: "fail_fast",
          label: "Fail Fast",
          type: "boolean",
          description: "Stop on first error",
        },
      ],
    },
    parallel: {
      color: "#d9d9d9",
      icon: "⚡",
      label: "Parallel",
      description: "Run steps in parallel",
      configFields: [
        {
          key: "substeps",
          label: "Substeps",
          type: "textarea",
          description: "Steps to run in parallel (JSON)",
        },
        {
          key: "max_concurrency",
          label: "Max Concurrency",
          type: "number",
          description: "Maximum concurrent tasks",
        },
      ],
    },
    mcp: {
      color: "#bc80bd",
      icon: "🔌",
      label: "MCP",
      description: "Call an MCP tool",
      configFields: [
        {
          key: "server",
          label: "Server",
          type: "textarea",
          description: "Server configuration (JSON)",
        },
        {
          key: "tool_name",
          label: "Tool Name",
          type: "text",
          description: "Name of tool to call",
        },
        {
          key: "arguments",
          label: "Arguments",
          type: "textarea",
          description: "Tool arguments (JSON)",
        },
        {
          key: "result_key",
          label: "Result Key",
          type: "text",
          description: "Key for result",
        },
      ],
    },
  },

  /**
   * Get type info for a step type
   * @param {string} type - Step type
   * @returns {object} - Type info
   */
  getTypeInfo(type) {
    return (
      this.types[type] || {
        color: "#999",
        icon: "❓",
        label: type || "Unknown",
        description: "Unknown step type",
        configFields: [],
      }
    );
  },

  /**
   * Get config fields for a step type
   * @param {string} type - Step type
   * @returns {Array} - Config fields
   */
  getConfigFields(type) {
    const typeInfo = this.getTypeInfo(type);
    const commonFields = [
      {
        key: "label",
        label: "Label",
        type: "text",
        description: "Display label for the node",
      },
    ];
    return [...commonFields, ...(typeInfo.configFields || [])];
  },

  /**
   * Get all available step types
   * @returns {Array} - List of step types
   */
  getAllTypes() {
    return Object.keys(this.types);
  },
};
