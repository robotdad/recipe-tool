"""
MCP server wrapping the recipe-tool CLI.
Provides two tools: execute_recipe and create_recipe.
"""
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import the CLI functions
import recipe_tool
from recipe_tool import execute_recipe as cli_execute, create_recipe as cli_create

# Load environment variables from .env if present
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("Recipe Tool Server")

@mcp.tool()
async def execute_recipe(
    recipe_path: str,
    context: dict[str, str] | None = None,
    log_dir: str = "logs"
) -> str:
    """
    Execute a recipe JSON file.
    """
    # Convert context dict to CLI-style key=value strings
    context_list = [f"{k}={v}" for k, v in (context or {}).items()]
    # Call the underlying recipe-tool logic
    await cli_execute(recipe_path, context_list, log_dir)
    return f"Recipe executed successfully (logs in {log_dir})"

@mcp.tool()
async def create_recipe(
    idea_path: str,
    context: dict[str, str] | None = None,
    log_dir: str = "logs"
) -> str:
    """
    Create a recipe from an idea file.
    """
    context_list = [f"{k}={v}" for k, v in (context or {}).items()]
    await cli_create(idea_path, context_list, log_dir)
    return f"Recipe created successfully (logs in {log_dir})"

def main() -> None:
    """
    Entry point for the MCP server.
    """
    mcp.run()

if __name__ == "__main__":
    main()