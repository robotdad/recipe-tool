"""
Main entrypoint for the Document Generator App UI.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
from document_generator_app.ui import build_editor


def check_deployment_status():
    """Check deployment status and recipe configuration."""
    print("\n=== Document Generator Deployment Diagnostic ===")

    # Check current working directory
    cwd = Path.cwd()
    print(f"Current working directory: {cwd}")

    # Check app structure
    app_root = Path(__file__).resolve().parents[1]
    print(f"App root: {app_root}")

    # Check for bundled recipes
    bundled_recipe_path = app_root / "document_generator_app" / "recipes" / "document_generator_recipe.json"
    print(f"Bundled recipe path: {bundled_recipe_path}")
    print(f"Bundled recipe exists: {bundled_recipe_path.exists()}")

    if bundled_recipe_path.exists():
        print("\n=== Bundled Recipe Info ===")
        try:
            with open(bundled_recipe_path) as f:
                recipe_data = json.load(f)
            print(f"Recipe title: {recipe_data.get('title', 'Unknown')}")
            print(f"Recipe description: {recipe_data.get('description', 'Unknown')}")
            print(f"Recipe steps: {len(recipe_data.get('steps', []))}")
        except Exception as e:
            print(f"Error reading recipe: {e}")

    # Check for development recipes
    dev_recipe_path = app_root.parents[1] / "recipes" / "document_generator" / "document_generator_recipe.json"
    print(f"\nDevelopment recipe path: {dev_recipe_path}")
    print(f"Development recipe exists: {dev_recipe_path.exists()}")

    # Check examples
    examples_dir = app_root / "examples"
    print(f"\nExamples directory: {examples_dir}")
    print(f"Examples directory exists: {examples_dir.exists()}")

    if examples_dir.exists():
        docpack_files = list(examples_dir.glob("*.docpack"))
        print(f"Docpack files: {len(docpack_files)}")
        for docpack in docpack_files:
            print(f"  - {docpack.name}")

    # Check environment variables
    print("\n=== Environment Variables ===")
    env_vars = ["PORT", "GRADIO_SERVER_NAME", "GRADIO_SERVER_PORT", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask API keys
            if "API_KEY" in var:
                value = value[:8] + "..." if len(value) > 8 else "SET"
        print(f"  {var}: {value or 'Not set'}")

    print("\n=== Diagnostic Complete ===\n")


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""

    # Load environment variables from .env file
    load_dotenv()

    # Run diagnostic check
    check_deployment_status()

    # Configuration for hosting - Azure App Service uses PORT environment variable
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "8000")))

    print(f"Starting Gradio app on {server_name}:{server_port}")
    build_editor().launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()
