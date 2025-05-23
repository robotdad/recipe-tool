# Document Generator App

This application provides a simple Gradio interface for running the
`document_generator` recipe from the main **recipe-tool** project.

## Usage

1. Run `make install` to set up the virtual environment and install
   dependencies (requires network access).
2. Launch the UI with:

   ```bash
   document-generator-app
   ```

3. (Optional) Upload your own outline JSON file to populate the interface fields.
4. Edit the outline fields (title, general instructions, sections).
   For each resource, you can upload a file, specify a local file path, or provide a URL.
   The application will fetch and prepare the resource automatically.
5. Click **Generate**. The recipe executes and the generated document is displayed below the interface.
   The content is loaded from the markdown file produced by the recipe.
6. Use the **Download Outline JSON** and **Download Generated Document** buttons
   to save the updated outline or the generated output to your local machine.
