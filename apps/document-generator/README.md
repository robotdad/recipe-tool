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

3. In the interactive interface:
   - Edit the outline fields (title, general instructions, sections).
   - For each resource, you can upload a file, specify a local file path, or provide a URL.
     The application will fetch and prepare the resource automatically.
4. Click **Generate**. The recipe executes and the generated document is displayed below the interface.
   The content is loaded from the markdown file produced by the recipe.
