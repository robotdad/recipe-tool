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

    # Initial outline state
    initial_sections = []

    with gr.Blocks() as demo:
        gr.Markdown("# Document Generator")
        gr.Markdown("## Outline Editor")
        # Metadata inputs
        title_tb = gr.Textbox(label="Title", value="")
        instruction_tb = gr.TextArea(label="General Instruction", value="")

        # Resources table: key, description, path, merge_mode
        gr.Markdown("## Resources")
        resources_df = gr.Dataframe(
            headers=["key", "description", "path", "merge_mode"],
            row_count=(1, "dynamic"),
            col_count=(4, "fixed"),
            datatype=["str", "str", "str", "str"],
            value=[],
        )

        # Sections editor (JSON placeholder for now)
        gr.Markdown("## Sections (JSON)")
        sections_json = gr.JSON(value=initial_sections, label="Sections JSON")
        # Buttons to add/remove top-level sections
        add_section_btn = gr.Button("Add Section")
        remove_section_btn = gr.Button("Remove Section")
        def add_section(secs):
            secs = secs or []
            secs.append({
                "title": "",
                "prompt": "",
                "refs": [],
                "resource_key": None,
                "sections": []
            })
            return secs
        def remove_section(secs):
            secs = secs or []
            if secs:
                secs.pop()
            return secs
        add_section_btn.click(add_section, inputs=[sections_json], outputs=[sections_json])
        remove_section_btn.click(remove_section, inputs=[sections_json], outputs=[sections_json])

        # Upload existing outline
        upload = gr.File(label="Upload Outline JSON", file_types=[".json"])
        def upload_action(file_obj):
            if not file_obj:
                return [None, None, None, None]
            raw = Path(file_obj.name).read_text()
            data = json.loads(raw)
            # Extract metadata
            title = data.get("title", "")
            instr = data.get("general_instruction", "")
            # Extract resources
            res = [[r.get(k, "") for k in ["key", "description", "path", "merge_mode"]]
                   for r in data.get("resources", [])]
            # Extract sections
            secs = data.get("sections", [])
            return title, instr, res, secs
        upload.upload(
            upload_action,
            inputs=[upload],
            outputs=[title_tb, instruction_tb, resources_df, sections_json],
        )

        # Validate outline
        validate_btn = gr.Button("Validate Outline")
        validate_output = gr.Textbox(label="Validation Result")
        def on_validate(title, instr, res_table, secs_json):
            # Build resources, include merge_mode only if non-empty
            resources = []
            for row in res_table:
                # Ensure each row has 4 elements: key, description, path, merge_mode
                cells = list(row) if isinstance(row, (list, tuple)) else []
                # Pad with empty strings if missing
                cells += [""] * (4 - len(cells))
                key, desc, path, mm = cells[:4]
                r = {"key": key, "description": desc, "path": path}
                if mm:
                    r["merge_mode"] = mm
                resources.append(r)
            outline = {
                "title": title,
                "general_instruction": instr,
                "resources": resources,
                "sections": secs_json or []
            }
            try:
                validate_outline(outline)
                return "Outline is valid."
            except Exception as e:
                return f"Validation error: {e}"
        validate_btn.click(
            on_validate,
            inputs=[title_tb, instruction_tb, resources_df, sections_json],
            outputs=[validate_output],
        )

        # Download outline without generating
        download_outline_btn = gr.Button("Download Outline JSON")
        download_outline_file = gr.File(label="Download Outline JSON")
        def download_outline(title, instr, res_table, secs_json):
            # Build resources, include merge_mode only if non-empty
            resources = []
            for row in res_table:
                cells = list(row) if isinstance(row, (list, tuple)) else []
                cells += [""] * (4 - len(cells))
                key, desc, path, mm = cells[:4]
                r = {"key": key, "description": desc, "path": path}
                if mm:
                    r["merge_mode"] = mm
                resources.append(r)
            outline = {
                "title": title,
                "general_instruction": instr,
                "resources": resources,
                "sections": secs_json or []
            }
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
            json.dump(outline, tmp, indent=2)
            tmp.close()
            return tmp.name
        download_outline_btn.click(
            download_outline,
            inputs=[title_tb, instruction_tb, resources_df, sections_json],
            outputs=[download_outline_file],
        )

        # Generate document
        generate_btn = gr.Button("Generate Document")
        output_md = gr.Markdown()
        download_doc_file = gr.File(label="Download Generated Document")
        def on_generate(title, instr, res_table, secs_json):
            # Build resources, include merge_mode only if non-empty
            resources = []
            for row in res_table:
                cells = list(row) if isinstance(row, (list, tuple)) else []
                cells += [""] * (4 - len(cells))
                key, desc, path, mm = cells[:4]
                r = {"key": key, "description": desc, "path": path}
                if mm:
                    r["merge_mode"] = mm
                resources.append(r)
            outline = {
                "title": title,
                "general_instruction": instr,
                "resources": resources,
                "sections": secs_json or []
            }
            # Validate outline
            validate_outline(outline)
            obj = Outline.from_dict(outline)
            # Run recipe
            import asyncio
            doc_text = asyncio.run(generate_document(obj))
            # Prepare download
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w")
            tmp.write(doc_text)
            tmp.close()
            return doc_text, tmp.name
        generate_btn.click(
            on_generate,
            inputs=[title_tb, instruction_tb, resources_df, sections_json],
            outputs=[output_md, download_doc_file],
        )

    return demo