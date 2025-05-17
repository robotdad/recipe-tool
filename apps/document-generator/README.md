# Document Generator App

This application provides a simple Gradio interface for running the
`document_generator` recipe from the main **recipe-tool** project.

## Usage

1. Run `make install` to set up the virtual environment and install
   dependencies (requires network access).
2. Launch the UI with:

   ```bash
   python document_generator/main.py
   ```
3. Edit the outline JSON in the editor and click **Generate**. The recipe
   executes and the generated document is displayed below the editor.

