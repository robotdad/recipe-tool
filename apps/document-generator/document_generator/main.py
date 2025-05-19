"""
Main entrypoint for the Document Generator App UI.
"""

from document_generator.ui.editor import build_editor


def main() -> None:
    """Launch the Gradio interface for editing and generating documents."""
    build_editor().launch(mcp_server=True, pwa=True)


if __name__ == "__main__":
    main()
