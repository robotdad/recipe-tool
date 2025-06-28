"""
Main entrypoint for the Document Generator App UI.
"""

import os

from dotenv import load_dotenv
from document_generator_app.ui import build_editor


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""

    # Load environment variables from .env file
    load_dotenv()

    # Configuration for hosting - Azure App Service uses PORT environment variable
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "8000")))

    print(f"Starting Gradio app on {server_name}:{server_port}")
    build_editor().launch(server_name=server_name, server_port=server_port, mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()
