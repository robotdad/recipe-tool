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

# Import app configuration and utilities
from recipe_executor_app.config import settings
from recipe_executor_app.utils import (
    prepare_context, extract_recipe_content, find_recent_json_file,
    handle_recipe_error, resolve_path, parse_recipe_json, get_repo_root
)

# Set up logging
logger = init_logger(settings.log_dir)
# Set logger level from settings
logger.setLevel(settings.log_level.upper())


class RecipeExecutorApp:
    """Gradio app for the Recipe Executor."""

    def __init__(self):
        self.executor = Executor(logger)

    @handle_recipe_error
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
        # Prepare context from variables
        context_dict, context = prepare_context(context_vars)

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
                "debug_context": {}
            }

        # Execute the recipe
        start_time = time.time()
        await self.executor.execute(recipe_source, context)
        execution_time = time.time() - start_time

        # Get all artifacts from context to display in raw tab
        all_artifacts = context.dict()
        
        # Log the full context for debugging
        logger.debug(f"Final context: {json.dumps(all_artifacts, default=str)}")

        # Get only output artifacts for the main results view
        results = {}
        for key, value in all_artifacts.items():
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

    @handle_recipe_error
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

        # Prepare base context
        context_dict, context = prepare_context(context_vars)
        
        # Add additional context variables
        # Add reference files to context if provided
        if reference_files:
            # Join with commas to match CLI format
            context_dict["files"] = ",".join(reference_files)

        # Add the idea path as the input context variable
        context_dict["input"] = idea_source
        
        # Update the context with our new variables
        context = Context(artifacts=context_dict)

        # Path to the recipe creator recipe
        creator_recipe_path = os.path.join(os.path.dirname(__file__), settings.recipe_creator_path)
        creator_recipe_path = os.path.normpath(creator_recipe_path)
        
        logger.info(f"Looking for recipe creator at: {creator_recipe_path}")

        # Make sure the recipe creator recipe exists
        if not os.path.exists(creator_recipe_path):
            # Try a fallback approach - relative to repo root
            repo_root = get_repo_root()
            fallback_path = os.path.join(repo_root, "recipes/recipe_creator/create.json")
            logger.info(f"First path failed, trying fallback: {fallback_path}")
            
            if os.path.exists(fallback_path):
                creator_recipe_path = fallback_path
                logger.info(f"Found recipe creator at fallback path: {creator_recipe_path}")
            else:
                return {
                    "recipe_json": "",
                    "structure_preview": f"### Error\nRecipe creator recipe not found at: {creator_recipe_path} or {fallback_path}",
                    "debug_context": {"error": f"Recipe creator recipe not found: {creator_recipe_path} or {fallback_path}"}
                }

        # Log important paths to help with debugging
        logger.info(f"Recipe Executor paths:")
        logger.info(f"  - Current working directory: {os.getcwd()}")
        logger.info(f"  - Repository root: {get_repo_root()}")
        logger.info(f"  - Recipe creator path: {creator_recipe_path}")
        logger.info(f"  - Context paths:")
        logger.info(f"    - recipe_root: {context.dict().get('recipe_root', 'Not set')}")
        logger.info(f"    - ai_context_root: {context.dict().get('ai_context_root', 'Not set')}")
        logger.info(f"    - output_root: {context.dict().get('output_root', 'Not set')}")
        
        # Execute the recipe creator
        start_time = time.time()
        await self.executor.execute(creator_recipe_path, context)
        execution_time = time.time() - start_time

        # Get the output recipe 
        output_recipe = None
        context_dict = context.dict()
        
        # Log the full context for debugging
        logger.debug(f"Final context after recipe creation: {json.dumps(context_dict, default=str)}")
        
        # Try to extract recipe from context or find in files
        
        # 1. Check if generated_recipe is in context
        if "generated_recipe" in context_dict:
            output_recipe = extract_recipe_content(context_dict["generated_recipe"])
            if output_recipe:
                logger.info(f"Successfully extracted recipe from generated_recipe context variable")
        
        # 2. If not found in context, try looking for target file
        if not output_recipe:
            output_root = context_dict.get("output_root", "output")
            target_file = context_dict.get("target_file", "generated_recipe.json")
            
            # Log what we're looking for
            logger.info(f"Looking for recipe file. output_root={output_root}, target_file={target_file}")
            
            # Check specific target file first
            file_path = resolve_path(target_file, output_root)
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        output_recipe = f.read()
                        logger.info(f"Read recipe from output file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to read output file {file_path}: {e}")
            else:
                logger.warning(f"Output file not found at: {file_path}")
                
            # 3. If still not found, look for recently modified files
            if not output_recipe:
                content, path = find_recent_json_file(output_root)
                if content:
                    output_recipe = content
                    logger.info(f"Using recipe from recent file: {path}")

        # Clean up temporary file if created
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

        # If no recipe found after all attempts
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
            recipe_json = parse_recipe_json(output_recipe)

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
            async def execute_recipe_formatted(file: Optional[str], text: Optional[str], ctx: Optional[str]) -> Tuple[str, str, str]:
                """Format execute_recipe output for Gradio UI."""
                result = await self.execute_recipe(file, text, ctx)
                # Extract the individual fields for Gradio UI
                formatted_results = result.get("formatted_results", "")
                raw_json = result.get("raw_json", "{}")
                # Format debug context as JSON string
                debug_context = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
                return formatted_results, raw_json, debug_context
                
            execute_btn.click(
                fn=execute_recipe_formatted,
                inputs=[recipe_file, recipe_text, context_vars],
                outputs=[result_output, raw_result, debug_context],
                api_name="execute_recipe",
            )

            # Connect components for Create Recipe tab
            async def create_recipe_formatted(text: str, file: Optional[str], refs: Optional[List[str]], ctx: Optional[str]) -> Tuple[str, str, str]:
                """Format create_recipe output for Gradio UI."""
                result = await self.create_recipe(text, file, refs, ctx)
                # Extract the individual fields for Gradio UI
                recipe_json = result.get("recipe_json", "")
                structure_preview = result.get("structure_preview", "")
                # Format debug context as JSON string
                debug_context = json.dumps(result.get("debug_context", {}), indent=2, default=lambda o: str(o))
                return recipe_json, structure_preview, debug_context
                
            create_btn.click(
                fn=create_recipe_formatted,
                inputs=[idea_text, idea_file, reference_files, create_context_vars],
                outputs=[create_output, preview_md, create_debug_context],
                api_name="create_recipe",
            )

            # Example handling logic
            @handle_recipe_error
            async def load_example(example_path: str) -> dict:
                """Load an example recipe from the examples directory.
                
                Args:
                    example_path: Path to the example recipe file
                
                Returns:
                    dict: Contains recipe_content and description keys
                """
                if not example_path:
                    return {"recipe_content": "", "description": "No example selected."}

                try:
                    # Log the original path for debugging
                    logger.info(f"Loading example from path: {example_path}")
                    
                    # Try multiple approaches to find the file
                    
                    # 1. First try using path directly with recipe_root as base
                    repo_root = get_repo_root()
                    recipe_root = os.path.join(repo_root, "recipes")
                    potential_paths = [
                        # 1. Direct interpretation of the path
                        example_path,
                        
                        # 2. Relative to repo root
                        os.path.join(repo_root, example_path.lstrip("../")),
                        
                        # 3. Relative to recipe_root (replacing initial ../../recipes with recipe_root)
                        os.path.join(recipe_root, example_path.replace("../../recipes/", "")),
                        
                        # 4. Relative to recipe_root (replacing initial ../../../recipes with recipe_root)
                        os.path.join(recipe_root, example_path.replace("../../../recipes/", "")),
                        
                        # 5. Direct path in recipes directory
                        os.path.join(recipe_root, os.path.basename(example_path))
                    ]
                    
                    # Try each path until we find one that exists
                    full_path = None
                    for path in potential_paths:
                        if os.path.exists(path):
                            full_path = path
                            logger.info(f"Found example at: {full_path}")
                            break
                    
                    if not full_path:
                        # Log all attempted paths for debugging
                        logger.error(f"Failed to find example recipe. Tried the following paths: {potential_paths}")
                        return {
                            "recipe_content": "", 
                            "description": f"Error: Could not find example recipe. Please check paths: {example_path}"
                        }
                    
                    # Read the content
                    with open(full_path, "r") as f:
                        content = f.read()

                    # Try to find README file with description
                    dir_path = os.path.dirname(full_path)
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
                    logger.error(f"Error loading example: {e}")
                    return {"recipe_content": "", "description": f"Error loading example: {str(e)}"}

            # Format the output for compatibility with the UI
            async def load_example_formatted(path: str) -> Tuple[str, str]:
                """Load an example recipe and format for UI."""
                result = await load_example(path)
                # Ensure we return strings even if result contains None values
                return result.get("recipe_content", ""), result.get("description", "")

            load_example_btn.click(
                fn=load_example_formatted,
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
