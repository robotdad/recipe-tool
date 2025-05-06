 # Recipe Tool MCP Server

 This MCP server wraps the `recipe-tool` CLI and exposes its functionality as MCP tools.

 ## Tools

 - execute_recipe(recipe_path: str, context: dict[str, str] | None = None, log_dir: str = "logs") -> str  
   Execute a recipe JSON file.

 - create_recipe(idea_path: str, context: dict[str, str] | None = None, log_dir: str = "logs") -> str  
   Create a recipe from an idea file.

 ## Usage

 Run as a standalone MCP server:

 ```bash
 recipe-tool-mcp-server
 ```

 Or install in Claude Desktop:

 ```bash
 mcp install recipe-tool-mcp-server
 ```