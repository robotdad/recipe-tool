"""
Editor UI builder for the Document Generator app, using Gradio Blocks.
"""
import json
from pathlib import Path
import gradio as gr
from ..schema.validator import validate_outline

def build_editor() -> gr.Blocks:
    """
    Build and return the full Gradio Blocks interface for editing and generating documents.
    """
    import json
    import tempfile
    from pathlib import Path

    from document_generator.models.outline import Outline
    from document_generator.schema.validator import validate_outline
    from document_generator.executor.runner import generate_document

    initial_outline = {
        "title": "",
        "general_instruction": "",
        "resources": [],
        "sections": []
    }

    with gr.Blocks() as demo:
        gr.Markdown("# Document Generator")
        gr.Markdown("## Outline Editor")
        outline_json = gr.JSON(value=initial_outline, label="Outline JSON")

        # Upload existing outline
        upload = gr.File(label="Upload Outline JSON", file_types=[".json"])
        def upload_action(file_obj):
            if not file_obj:
                return initial_outline
            data = json.loads(Path(file_obj.name).read_text())
            return data
        upload.upload(upload_action, inputs=[upload], outputs=[outline_json])

        # Validate outline
        validate_btn = gr.Button("Validate Outline")
        validate_output = gr.Textbox(label="Validation Result")
        def on_validate(data):
            try:
                validate_outline(data)
                return "Outline is valid."
            except Exception as e:
                return f"Validation error: {e}"
        validate_btn.click(on_validate, inputs=[outline_json], outputs=[validate_output])

        # Download outline without generating
        download_outline_btn = gr.Button("Download Outline JSON")
        download_outline_file = gr.File(label="Download Outline JSON")
        def download_outline(data):
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
            json.dump(data, temp, indent=2)
            temp.close()
            return temp.name
        download_outline_btn.click(download_outline, inputs=[outline_json], outputs=[download_outline_file])

        # Generate document
        generate_btn = gr.Button("Generate Document")
        output_md = gr.Markdown()
        download_doc_file = gr.File(label="Download Generated Document")
        def on_generate(data):
            # Validate before generation
            validate_outline(data)
            outline = Outline.from_dict(data)
            # Run recipe
            import asyncio
            doc_text = asyncio.run(generate_document(outline))
            # Prepare download
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w")
            tmp.write(doc_text)
            tmp.close()
            return doc_text, tmp.name
        generate_btn.click(on_generate, inputs=[outline_json], outputs=[output_md, download_doc_file])

    return demo