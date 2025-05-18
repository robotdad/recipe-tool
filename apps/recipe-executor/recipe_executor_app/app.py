"""Gradio web app for the Recipe Executor."""

import gradio as gr
import gradio.themes
from typing import List, Optional, Dict, Tuple, Any
import asyncio
import os
import tempfile
import time
import json
import argparse

# Import from the recipe_executor package
from recipe_executor.context import Context
from recipe_executor.executor import Executor
from recipe_executor.logger import init_logger

# Import app configuration
from recipe_executor_app.config import settings

# Set up logging
logger = init_logger(settings.log_dir)
# Set logger level to DEBUG
logger.setLevel("DEBUG")


class RecipeExecutorApp:
    """Gradio app for the Recipe Executor."""

    def __init__(self):
        self.executor = Executor(logger)

    async def execute_recipe(
        self, recipe_file: Optional[str], recipe_text: Optional[str], context_vars: Optional[str]
    ) -> dict:
        """
        Execute a recipe from a file upload or text input.

        Args:
            recipe_file: Optional path to a recipe JSON file
            recipe_text: Optional JSON string containing the recipe
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            dict: Contains formatted_results (markdown) and raw_json keys
        """
        try:
            # Parse context variables from string (format: key1=value1,key2=value2)
            context_dict = {}
            if context_vars:
                for item in context_vars.split(","):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        context_dict[key.strip()] = value.strip()

            # Add standard paths to context
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            context_dict["recipe_root"] = os.path.join(repo_root, "recipes")
            context_dict["ai_context_root"] = os.path.join(repo_root, "ai_context") 
            context_dict["output_root"] = os.path.join(repo_root, "output")
            
            # Ensure output directory exists
            os.makedirs(context_dict["output_root"], exist_ok=True)
            
            # Create context
            context = Context(artifacts=context_dict)

            # Determine recipe source
            recipe_source = None
            if recipe_file:
                recipe_source = recipe_file
                logger.info(f"Executing recipe from file: {recipe_file}")
            elif recipe_text:
                recipe_source = recipe_text
                logger.info("Executing recipe from text input")
            else:
                return {
                    "formatted_results": "### Error\nNo recipe provided. Please upload a file or paste the recipe JSON.",
                    "raw_json": "{}",
                }

            # Execute the recipe
            start_time = time.time()
            await self.executor.execute(recipe_source, context)
            execution_time = time.time() - start_time

            # Get all artifacts from context to display in raw tab
            all_artifacts = context.dict()
            
            # Log the full context for debugging
            logger.debug(f"Final context: {json.dumps(all_artifacts, default=str)}")

            # Prepare formatted results

            # Get only output artifacts for the main results view
            results = {}
            context_dict = context.dict()
            for key, value in context_dict.items():
                # Only include string results or keys that look like outputs
                if isinstance(value, str) and (key.startswith("output") or key.startswith("result")):
                    results[key] = value

            # Format markdown output
            if results:
                markdown_output = (
                    f"### Recipe Execution Successful\n\n**Execution Time**: {execution_time:.2f} seconds\n\n"
                )
                markdown_output += "#### Results\n\n"

                for key, value in results.items():
                    markdown_output += f"**{key}**:\n"
                    # Check if value is JSON
                    try:
                        json_obj = json.loads(value)
                        markdown_output += f"```json\n{json.dumps(json_obj, indent=2)}\n```\n\n"
                    except json.JSONDecodeError:
                        # Not JSON, treat as regular text
                        markdown_output += f"```\n{value}\n```\n\n"
            else:
                markdown_output = f"### Recipe Execution Successful\n\n**Execution Time**: {execution_time:.2f} seconds\n\nNo string results were found in the context."

            # Format raw JSON output using a simple default function to handle non-serializable types
            raw_json = json.dumps(all_artifacts, indent=2, default=lambda o: str(o))

            return {
                "formatted_results": markdown_output, 
                "raw_json": raw_json,
                "debug_context": all_artifacts
            }

        except Exception as e:
            logger.error(f"Recipe execution failed: {e}")
            error_msg = f"### Error\n\n```\n{str(e)}\n```"
            return {
                "formatted_results": error_msg, 
                "raw_json": "{}",
                "debug_context": {"error": str(e)}
            }

    async def create_recipe(
        self,
        idea_text: str,
        idea_file: Optional[str],
        reference_files: Optional[List[str]],
        context_vars: Optional[str],
    ) -> dict:
        """
        Create a recipe from an idea text or file.

        Args:
            idea_text: Text describing the recipe idea
            idea_file: Optional path to a file containing the recipe idea
            reference_files: Optional list of paths to reference files
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            dict: Contains recipe_json and structure_preview keys
        """
        try:
            # Parse context variables
            context_dict = {}
            if context_vars:
                for item in context_vars.split(","):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        context_dict[key.strip()] = value.strip()

            # Determine idea source
            idea_source = None
            temp_file = None

            if idea_file:
                idea_source = idea_file
                logger.info(f"Creating recipe from idea file: {idea_file}")
            elif idea_text:
                # Create a temporary file to store the idea text
                fd, temp_path = tempfile.mkstemp(suffix=".md", prefix="idea_")
                with os.fdopen(fd, "w") as f:
                    f.write(idea_text)
                idea_source = temp_path
                temp_file = temp_path
                logger.info(f"Creating recipe from idea text (saved to {temp_path})")
            else:
                return {
                    "recipe_json": "",
                    "structure_preview": "### Error\nNo idea provided. Please upload a file or enter idea text.",
                    "debug_context": {"error": "No idea provided"}
                }

            # Add reference files to context if provided
            if reference_files:
                # Join with commas to match CLI format
                context_dict["files"] = ",".join(reference_files)

            # Add the idea path as the input context variable
            context_dict["input"] = idea_source

            # Add standard paths to context
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            context_dict["recipe_root"] = os.path.join(repo_root, "recipes")
            context_dict["ai_context_root"] = os.path.join(repo_root, "ai_context") 
            context_dict["output_root"] = os.path.join(repo_root, "output")
            
            # Ensure output directory exists
            os.makedirs(context_dict["output_root"], exist_ok=True)
            
            # Create context and executor
            context = Context(artifacts=context_dict)

            # Path to the recipe creator recipe
            creator_recipe_path = settings.recipe_creator_path

            # Make sure the recipe creator recipe exists
            if not os.path.exists(creator_recipe_path):
                return {
                    "recipe_json": "",
                    "structure_preview": f"### Error\nRecipe creator recipe not found: {creator_recipe_path}",
                    "debug_context": {"error": f"Recipe creator recipe not found: {creator_recipe_path}"}
                }

            # Execute the recipe creator
            start_time = time.time()
            await self.executor.execute(creator_recipe_path, context)
            execution_time = time.time() - start_time

            # Get the output recipe 
            output_recipe = None
            context_dict = context.dict()
            
            # Log the full context for debugging
            logger.debug(f"Final context after recipe creation: {json.dumps(context_dict, default=str)}")
            
            # Check if generated_recipe is in context
            if "generated_recipe" in context_dict:
                generated_recipe = context_dict["generated_recipe"]
                logger.info(f"Found generated_recipe in context: {type(generated_recipe)}")
                
                # Handle different possible formats of generated_recipe
                # Format 1: List with dict containing path and content
                if isinstance(generated_recipe, list) and len(generated_recipe) > 0:
                    item = generated_recipe[0]
                    # Log the item structure for debugging
                    logger.debug(f"First item in generated_recipe list: {item}")
                    
                    if isinstance(item, dict):
                        # Found a dictionary in the list
                        if "content" in item:
                            # Extract the content directly
                            output_recipe = item["content"]
                            logger.info(f"Using recipe from generated_recipe list item with content key: {item.get('path', 'unknown')}")
                
                # Format 2: String containing JSON directly
                elif isinstance(generated_recipe, str):
                    output_recipe = generated_recipe
                    logger.info("Using recipe from generated_recipe string")
                
                # Format 3: Dictionary with path and content
                elif isinstance(generated_recipe, dict):
                    if "content" in generated_recipe:
                        output_recipe = generated_recipe["content"]
                        logger.info(f"Using recipe from generated_recipe dict with content key: {generated_recipe.get('path', 'unknown')}")
                
                # Log the extracted recipe for debugging
                if output_recipe:
                    logger.info(f"Successfully extracted recipe from generated_recipe: {output_recipe[:100]}...")
            
            # If not found in generated_recipe, try looking for target file in output directory
            if not output_recipe:
                output_root = context_dict.get("output_root", "output")
                target_file = context_dict.get("target_file", "generated_recipe.json")
                
                # Log what we're looking for
                logger.info(f"Looking for recipe file. output_root={output_root}, target_file={target_file}")
                
                # Check if it's an absolute path or needs to be joined with output_root
                if not os.path.isabs(target_file):
                    if not os.path.isabs(output_root):
                        # If output_root is relative, make it absolute from the repo root
                        output_root = os.path.join(repo_root, output_root)
                    file_path = os.path.join(output_root, target_file)
                else:
                    file_path = target_file
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r") as f:
                            output_recipe = f.read()
                            logger.info(f"Read recipe from output file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to read output file {file_path}: {e}")
                else:
                    logger.warning(f"Output file not found at: {file_path}")
                    
                # Look for recently modified files in the output directory
                try:
                    if os.path.exists(output_root):
                        json_files = [f for f in os.listdir(output_root) if f.endswith(".json")]
                        if json_files:
                            # Sort by modification time (newest first)
                            json_files_with_paths = [os.path.join(output_root, f) for f in json_files]
                            newest_file = max(json_files_with_paths, key=os.path.getmtime)
                            
                            # Only use if created in the last 30 seconds (to avoid using unrelated files)
                            if time.time() - os.path.getmtime(newest_file) < 30:
                                logger.info(f"Found recent JSON file in output directory: {newest_file}")
                                with open(newest_file, "r") as f:
                                    output_recipe = f.read()
                                    logger.info(f"Read recipe from newest file: {newest_file}")
                            else:
                                time_diff = time.time() - os.path.getmtime(newest_file)
                                logger.warning(f"Most recent JSON file {newest_file} is {time_diff:.2f} seconds old, skipping")
                        else:
                            logger.warning(f"No JSON files found in {output_root}")
                    else:
                        logger.warning(f"Output directory not found: {output_root}")
                except Exception as e:
                    logger.warning(f"Error while searching for recent files: {e}")

            # Clean up temporary file if created
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

            if not output_recipe:
                logger.warning("No output recipe found in any location")
                return {
                    "recipe_json": "",
                    "structure_preview": "### Recipe created successfully\nBut no output recipe was found. Check the output directory for generated files.",
                    "debug_context": context_dict
                }
                
            # Log the recipe content for debugging
            logger.info(f"Output recipe found, length: {len(output_recipe)}")
            logger.debug(f"Recipe content: {output_recipe[:500]}...")
            
            # Make sure it's a string
            if not isinstance(output_recipe, str):
                logger.warning(f"Output recipe is not a string, converting from: {type(output_recipe)}")
                
                # Try to convert to string if it's a dictionary or other JSON-serializable object
                try:
                    if isinstance(output_recipe, (dict, list)):
                        output_recipe = json.dumps(output_recipe, indent=2)
                    else:
                        output_recipe = str(output_recipe)
                except Exception as e:
                    logger.error(f"Failed to convert output_recipe to string: {e}")
                    return {
                        "recipe_json": "",
                        "structure_preview": f"### Error\nFailed to process recipe: {str(e)}",
                        "debug_context": context_dict
                    }

            # Generate a preview for the recipe structure
            try:
                recipe_json = json.loads(output_recipe)

                # Create a markdown preview of the recipe structure
                preview = f"### Recipe Structure\n\n**Execution Time**: {execution_time:.2f} seconds\n\n"

                if "name" in recipe_json:
                    preview += f"**Name**: {recipe_json['name']}\n\n"

                if "description" in recipe_json:
                    preview += f"**Description**: {recipe_json['description']}\n\n"

                if "steps" in recipe_json and isinstance(recipe_json["steps"], list):
                    preview += f"**Steps**: {len(recipe_json['steps'])}\n\n"
                    preview += "| # | Type | Description |\n"
                    preview += "|---|------|-------------|\n"

                    for i, step in enumerate(recipe_json["steps"]):
                        step_type = step.get("type", "unknown")
                        step_desc = ""

                        if "config" in step and "description" in step["config"]:
                            step_desc = step["config"]["description"]
                        elif "description" in step:
                            step_desc = step["description"]

                        preview += f"| {i + 1} | {step_type} | {step_desc} |\n"

                return {
                    "recipe_json": output_recipe, 
                    "structure_preview": preview,
                    "debug_context": context_dict
                }

            except (json.JSONDecodeError, TypeError) as e:
                # In case of any issues with JSON processing
                logger.error(f"Error parsing recipe JSON: {e}")
                logger.error(f"Recipe content causing error: {output_recipe[:500]}...")
                
                return {
                    "recipe_json": output_recipe,
                    "structure_preview": f"### Recipe Created\n\n**Execution Time**: {execution_time:.2f} seconds\n\nWarning: Output is not valid JSON format or contains non-serializable objects. Error: {str(e)}",
                    "debug_context": context_dict
                }

        except Exception as e:
            logger.error(f"Recipe creation failed: {e}")
            error_msg = f"### Error\n\n```\n{str(e)}\n```"
            return {
                "recipe_json": "", 
                "structure_preview": error_msg,
                "debug_context": {"error": str(e)}
            }

    def build_ui(self) -> gr.Blocks:
        """Build the Gradio UI."""
        theme = gradio.themes.Soft() if settings.theme == "soft" else settings.theme
        with gr.Blocks(title=settings.app_title, theme=theme) as app:
            gr.Markdown("# Recipe Executor")
            gr.Markdown("A web interface for executing and creating recipes.")

            with gr.Tabs():
                # Execute Recipe Tab
                with gr.TabItem("Execute Recipe"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### Input")
                            recipe_file = gr.File(label="Recipe JSON File", file_types=[".json"])
                            recipe_text = gr.Code(label="Recipe JSON", language="json", lines=15)

                            with gr.Accordion("Context Variables", open=False):
                                context_vars = gr.Textbox(
                                    label="Context Variables",
                                    placeholder="key1=value1,key2=value2",
                                    info="Add context variables as key=value pairs, separated by commas",
                                )

                            execute_btn = gr.Button("Execute Recipe", variant="primary")

                        with gr.Column(scale=1):
                            gr.Markdown("### Output")
                            with gr.Tabs():
                                with gr.TabItem("Results"):
                                    result_output = gr.Markdown(label="Results")
                                with gr.TabItem("Raw Output"):
                                    raw_result = gr.Code(language="json", label="Raw JSON")
                                with gr.TabItem("Debug Context"):
                                    debug_context = gr.Code(language="json", label="Full Context Variables")

                # Create Recipe Tab
                with gr.TabItem("Create Recipe"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### Input")

                            with gr.Tabs():
                                with gr.TabItem("Text Input"):
                                    idea_text = gr.TextArea(
                                        label="Idea Text", placeholder="Enter your recipe idea here...", lines=10
                                    )

                                with gr.TabItem("File Input"):
                                    idea_file = gr.File(label="Idea File", file_types=[".md", ".txt"])

                            with gr.Accordion("Additional Options", open=False):
                                reference_files = gr.File(
                                    label="Reference Files",
                                    file_types=[".md", ".txt", ".py", ".json"],
                                    file_count="multiple",
                                )
                                create_context_vars = gr.Textbox(
                                    label="Context Variables",
                                    placeholder="key1=value1,key2=value2",
                                    info="Add context variables as key=value pairs, separated by commas",
                                )

                            create_btn = gr.Button("Create Recipe", variant="primary")

                        with gr.Column(scale=1):
                            gr.Markdown("### Output")
                            with gr.Tabs():
                                with gr.TabItem("Generated Recipe"):
                                    create_output = gr.Code(language="json", label="Recipe JSON", lines=20)
                                with gr.TabItem("Preview"):
                                    preview_md = gr.Markdown(label="Recipe Structure")
                                with gr.TabItem("Debug Context"):
                                    create_debug_context = gr.Code(language="json", label="Full Context Variables")

                # Examples Tab
                with gr.TabItem("Examples"):
                    gr.Markdown("### Recipe Examples")
                    example_paths = gr.Dropdown(
                        settings.example_recipes,
                        label="Example Recipes",
                    )
                    load_example_btn = gr.Button("Load Example")

                    with gr.Accordion("Example Description", open=False):
                        example_desc = gr.Markdown()

            # Connect components for Execute Recipe tab
            def execute_recipe_wrapper(file: Optional[str], text: Optional[str], ctx: Optional[str]):
                """Execute a recipe from a file or text input.
                
                Args:
                    file (str, optional): Path to a recipe JSON file to execute
                    text (str, optional): Recipe JSON content as text
                    ctx (str, optional): Context variables as comma-separated key=value pairs (e.g., "key1=value1,key2=value2")
                
                Returns:
                    tuple: (formatted_results, raw_json, debug_context) containing the execution results
                """
                result = asyncio.run(self.execute_recipe(file, text, ctx))
                
                # Format the debug context with nice indentation and better handling of complex objects
                debug_json = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
                
                return result["formatted_results"], result["raw_json"], debug_json

            execute_btn.click(
                fn=execute_recipe_wrapper,
                inputs=[recipe_file, recipe_text, context_vars],
                outputs=[result_output, raw_result, debug_context],
                api_name="execute_recipe",
            )

            # Connect components for Create Recipe tab
            def create_recipe_wrapper(text: str, file: Optional[str], refs: Optional[List[str]], ctx: Optional[str]):
                """Create a new recipe from an idea description.
                
                Args:
                    text (str): Text describing the recipe idea
                    file (str, optional): Path to an idea file (.md or .txt)
                    refs (list, optional): List of reference file paths to include
                    ctx (str, optional): Context variables as comma-separated key=value pairs
                
                Returns:
                    tuple: (recipe_json, structure_preview, debug_context) containing the generated recipe
                """
                result = asyncio.run(self.create_recipe(text, file, refs, ctx))
                
                # Format the debug context with nice indentation and better handling of complex objects
                debug_json = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
                
                return result["recipe_json"], result["structure_preview"], debug_json

            create_btn.click(
                fn=create_recipe_wrapper,
                inputs=[idea_text, idea_file, reference_files, create_context_vars],
                outputs=[create_output, preview_md, create_debug_context],
                api_name="create_recipe",
            )

            # Example handling logic
            async def load_example(example_path: str) -> dict:
                if not example_path:
                    return {"recipe_content": "", "description": "No example selected."}

                try:
                    with open(example_path, "r") as f:
                        content = f.read()

                    # Try to find README file with description
                    dir_path = os.path.dirname(example_path)
                    readme_path = os.path.join(dir_path, "README.md")
                    desc = ""
                    if os.path.exists(readme_path):
                        with open(readme_path, "r") as f:
                            desc = f.read()

                    return {
                        "recipe_content": content,
                        "description": desc or "No description available for this example.",
                    }
                except Exception as e:
                    return {"recipe_content": "", "description": f"Error loading example: {str(e)}"}

            def load_example_wrapper(path: str):
                """Load an example recipe from the examples directory.
                
                Args:
                    path (str): Path to the example recipe file
                
                Returns:
                    tuple: (recipe_content, description) with the recipe JSON and its description
                """
                result = asyncio.run(load_example(path))
                return result["recipe_content"], result["description"]

            load_example_btn.click(
                fn=load_example_wrapper,
                inputs=[example_paths],
                outputs=[recipe_text, example_desc],
                api_name="load_example",
            )

        return app


def create_app() -> gr.Blocks:
    """Create and return the Gradio app."""
    app = RecipeExecutorApp()
    return app.build_ui()


def main() -> None:
    """Entry point for the application."""
    # Parse command line arguments to override settings
    parser = argparse.ArgumentParser(description=settings.app_description)
    parser.add_argument("--host", help=f"Host to listen on (default: {settings.host})")
    parser.add_argument("--port", type=int, help=f"Port to listen on (default: {settings.port})")
    parser.add_argument("--no-mcp", action="store_true", help="Disable MCP server functionality")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Override settings with command line arguments if provided
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    if args.no_mcp:
        settings.mcp_server = False
    if args.debug:
        settings.debug = True

    # Create and launch the app with settings
    app = create_app()

    # Get launch kwargs from settings
    launch_kwargs = settings.to_launch_kwargs()
    app.launch(**launch_kwargs)


if __name__ == "__main__":
    main()
