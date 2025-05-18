"""Gradio web app for the Recipe Executor."""

import gradio as gr
import gradio.themes
from typing import List, Optional
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


class RecipeExecutorApp:
    """Gradio app for the Recipe Executor."""

    def __init__(self):
        self.executor = Executor(logger)

    async def execute_recipe(
        self, recipe_file: Optional[str], recipe_text: Optional[str], context_vars: Optional[str]
    ) -> tuple[str, str]:
        """
        Execute a recipe from a file upload or text input.

        Args:
            recipe_file: Optional path to a recipe JSON file
            recipe_text: Optional JSON string containing the recipe
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            tuple[str, str]: Formatted results markdown, Raw JSON results
        """
        try:
            # Parse context variables from string (format: key1=value1,key2=value2)
            context_dict = {}
            if context_vars:
                for item in context_vars.split(","):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        context_dict[key.strip()] = value.strip()

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
                return "### Error\nNo recipe provided. Please upload a file or paste the recipe JSON.", "{}"

            # Execute the recipe
            start_time = time.time()
            await self.executor.execute(recipe_source, context)
            execution_time = time.time() - start_time

            # Get all artifacts from context to display in raw tab
            all_artifacts = context.dict()

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

            return markdown_output, raw_json

        except Exception as e:
            logger.error(f"Recipe execution failed: {e}")
            error_msg = f"### Error\n\n```\n{str(e)}\n```"
            return error_msg, "{}"

    async def create_recipe(
        self,
        idea_text: str,
        idea_file: Optional[str],
        reference_files: Optional[List[str]],
        context_vars: Optional[str],
    ) -> tuple[str, str]:
        """
        Create a recipe from an idea text or file.

        Args:
            idea_text: Text describing the recipe idea
            idea_file: Optional path to a file containing the recipe idea
            reference_files: Optional list of paths to reference files
            context_vars: Optional context variables as comma-separated key=value pairs

        Returns:
            tuple[str, str]: Generated recipe JSON, Recipe structure preview in markdown
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
                return "", "### Error\nNo idea provided. Please upload a file or enter idea text."

            # Add reference files to context if provided
            if reference_files:
                # Join with commas to match CLI format
                context_dict["files"] = ",".join(reference_files)

            # Add the idea path as the input context variable
            context_dict["input"] = idea_source

            # Create context and executor
            context = Context(artifacts=context_dict)

            # Path to the recipe creator recipe
            creator_recipe_path = settings.recipe_creator_path

            # Make sure the recipe creator recipe exists
            if not os.path.exists(creator_recipe_path):
                return "", f"### Error\nRecipe creator recipe not found: {creator_recipe_path}"

            # Execute the recipe creator
            start_time = time.time()
            await self.executor.execute(creator_recipe_path, context)
            execution_time = time.time() - start_time

            # Get the output recipe
            output_recipe = None
            context_dict = context.dict()
            for key, value in context_dict.items():
                if key == "output" and isinstance(value, str):
                    output_recipe = value

            # Clean up temporary file if created
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

            if not output_recipe:
                return "", "### Recipe created successfully\nBut no output was found in the context."

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

                return output_recipe, preview

            except (json.JSONDecodeError, TypeError):
                # In case of any issues with JSON processing 
                return (
                    output_recipe,
                    f"### Recipe Created\n\n**Execution Time**: {execution_time:.2f} seconds\n\nWarning: Output is not valid JSON format or contains non-serializable objects.",
                )

        except Exception as e:
            logger.error(f"Recipe creation failed: {e}")
            error_msg = f"### Error\n\n```\n{str(e)}\n```"
            return "", error_msg

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
            execute_btn.click(
                fn=lambda file, text, ctx: asyncio.run(self.execute_recipe(file, text, ctx)),
                inputs=[recipe_file, recipe_text, context_vars],
                outputs=[result_output, raw_result],
            )

            # Connect components for Create Recipe tab
            create_btn.click(
                fn=lambda text, file, refs, ctx: asyncio.run(self.create_recipe(text, file, refs, ctx)),
                inputs=[idea_text, idea_file, reference_files, create_context_vars],
                outputs=[create_output, preview_md],
            )

            # Example handling logic
            async def load_example(example_path):
                if not example_path:
                    return "", "No example selected."

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

                    return content, desc or "No description available for this example."
                except Exception as e:
                    return "", f"Error loading example: {str(e)}"

            load_example_btn.click(
                fn=lambda path: asyncio.run(load_example(path)),
                inputs=[example_paths],
                outputs=[recipe_text, example_desc],
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
