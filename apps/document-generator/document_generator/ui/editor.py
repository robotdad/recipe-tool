"""
Editor UI builder for the Document Generator app, using Gradio Blocks.
"""
# flake8: noqa
import json
from pathlib import Path
import gradio as gr

def build_editor() -> gr.Blocks:
    """
    Build and return the full Gradio Blocks interface for editing and generating documents.
    """
    import tempfile

    from document_generator.models.outline import Outline
    from document_generator.schema.validator import validate_outline
    from document_generator.executor.runner import generate_document

    # Initial outline state
    initial_resources = []
    initial_sections = []
    # State for nested subsections (placeholder)
    nested_state = gr.State(initial_sections)

    with gr.Blocks() as demo:
        gr.Markdown("# Document Generator")
        gr.Markdown("## Outline Editor")
        # Metadata inputs
        title_tb = gr.Textbox(label="Title", value="")
        instruction_tb = gr.TextArea(label="General Instruction", value="")

        # Resources table: key, description, path, merge_mode
        # Resources list and editor
        gr.Markdown("## Resources")
        resources_state = gr.State(initial_resources)
        resources_list = gr.Dropdown(choices=[], label="Select Resource", interactive=True)
        add_res_btn = gr.Button("Add Resource")
        remove_res_btn = gr.Button("Remove Resource")
        key_tb = gr.Textbox(label="Key")
        desc_tb = gr.Textbox(label="Description")
        path_tb = gr.Textbox(label="Path or URL")
        file_upload = gr.File(label="Upload File")
        merge_mode_dd = gr.Dropdown(choices=["","concat","dict"], label="Merge Mode")

        # Resource callbacks
        def res_add(res_list):
            res_list = res_list or []
            res_list.append({"key":"","description":"","path":"","merge_mode":""})
            return res_list
        def res_remove(res_list, sel):
            res_list = res_list or []
            idx = int(sel) if sel is not None else None
            if idx is not None and 0 <= idx < len(res_list):
                res_list.pop(idx)
            return res_list
        def res_select(sel, res_list):
            res_list = res_list or []
            idx = int(sel) if sel is not None else None
            if idx is None or idx < 0 or idx >= len(res_list):
                return "", "", None, "", res_list
            r = res_list[idx]
            return r.get("key",""), r.get("description",""), r.get("path",""), None, r.get("merge_mode",""), res_list
        def res_key_change(val, sel, res_list):
            if sel is None: return res_list
            idx = int(sel)
            res_list = res_list or []
            if 0 <= idx < len(res_list): res_list[idx]["key"] = val
            return res_list
        def res_desc_change(val, sel, res_list):
            if sel is None: return res_list
            idx = int(sel)
            res_list = res_list or []
            if 0 <= idx < len(res_list): res_list[idx]["description"] = val
            return res_list
        def res_path_change(val, sel, res_list):
            if sel is None: return res_list
            idx = int(sel)
            res_list = res_list or []
            if 0 <= idx < len(res_list): res_list[idx]["path"] = val
            return res_list
        def res_file_upload(file_obj, sel, res_list):
            if not file_obj or sel is None: return res_list
            idx = int(sel)
            res_list = res_list or []
            if 0 <= idx < len(res_list): res_list[idx]["path"] = file_obj.name
            return res_list
        def res_mm_change(val, sel, res_list):
            if sel is None: return res_list
            idx = int(sel)
            res_list = res_list or []
            if 0 <= idx < len(res_list): res_list[idx]["merge_mode"] = val
            return res_list

        add_res_btn.click(res_add, inputs=[resources_state], outputs=[resources_state, resources_list])
        remove_res_btn.click(res_remove, inputs=[resources_state, resources_list], outputs=[resources_state, resources_list])
        resources_list.change(res_select, inputs=[resources_list, resources_state], outputs=[key_tb, desc_tb, path_tb, file_upload, merge_mode_dd, resources_state])
        key_tb.change(res_key_change, inputs=[key_tb, resources_list, resources_state], outputs=[resources_state])
        desc_tb.change(res_desc_change, inputs=[desc_tb, resources_list, resources_state], outputs=[resources_state])
        path_tb.change(res_path_change, inputs=[path_tb, resources_list, resources_state], outputs=[resources_state])
        file_upload.change(res_file_upload, inputs=[file_upload, resources_list, resources_state], outputs=[resources_state])
        merge_mode_dd.change(res_mm_change, inputs=[merge_mode_dd, resources_list, resources_state], outputs=[resources_state])

        # Sections list and editor
        gr.Markdown("## Sections")
        sections_state = gr.State(initial_sections)
        sections_list = gr.Dropdown(choices=[], label="Select Section", interactive=True)
        add_sec_btn = gr.Button("Add Section")
        remove_sec_btn = gr.Button("Remove Section")
        sec_title_tb = gr.Textbox(label="Section Title")
        mode_radio = gr.Radio(choices=["prompt", "static"], label="Mode")
        sec_prompt_tb = gr.TextArea(label="Prompt")
        sec_refs = gr.CheckboxGroup(choices=[], label="Refs (resource keys)")
        sec_res_dd = gr.Dropdown(choices=[], label="Resource Key")

        # Section callbacks
        def sec_add(sec_list):
            sec_list = sec_list or []
            sec_list.append({"title":"","refs":[],"prompt":"","resource_key":None,"sections":[]})
            return sec_list
        def sec_remove(sec_list, sel):
            sec_list = sec_list or []
            idx = int(sel) if sel is not None else None
            if idx is not None and 0 <= idx < len(sec_list):
                sec_list.pop(idx)
            return sec_list
        def sec_select(sel, sec_list):
            sec_list = sec_list or []
            idx = int(sel) if sel is not None else None
            if idx is None or idx < 0 or idx >= len(sec_list):
                return "", "prompt", [], "", sec_list
            s = sec_list[idx]
            mode = "static" if s.get("resource_key") else "prompt"
            refs = s.get("refs", [])
            return s.get("title",""), mode, s.get("prompt",""), refs, s.get("resource_key",""), sec_list
        def sec_title_change(val, sel, sec_list):
            if sel is None: return sec_list
            idx = int(sel)
            sec_list = sec_list or []
            if 0 <= idx < len(sec_list): sec_list[idx]["title"] = val
            return sec_list
        def sec_mode_change(val, sel, sec_list):
            if sel is None: return sec_list
            idx = int(sel)
            sec_list = sec_list or []
            if 0 <= idx < len(sec_list):
                if val == "prompt":
                    sec_list[idx].pop("resource_key", None)
                else:
                    sec_list[idx].pop("prompt", None)
                    sec_list[idx].pop("refs", None)
            return sec_list
        def sec_prompt_change(val, sel, sec_list):
            if sel is None: return sec_list
            idx = int(sel)
            sec_list = sec_list or []
            if 0 <= idx < len(sec_list): sec_list[idx]["prompt"] = val
            return sec_list
        def sec_refs_change(val, sel, sec_list):
            if sel is None: return sec_list
            idx = int(sel)
            sec_list = sec_list or []
            if 0 <= idx < len(sec_list): sec_list[idx]["refs"] = val
            return sec_list
        def sec_res_change(val, sel, sec_list):
            if sel is None: return sec_list
            idx = int(sel)
            sec_list = sec_list or []
            if 0 <= idx < len(sec_list): sec_list[idx]["resource_key"] = val
            return sec_list

        add_sec_btn.click(sec_add, inputs=[sections_state], outputs=[sections_state, sections_list])
        remove_sec_btn.click(sec_remove, inputs=[sections_state, sections_list], outputs=[sections_state, sections_list])
        sections_list.change(sec_select, inputs=[sections_list, sections_state], outputs=[sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, sections_state])
        sec_title_tb.change(sec_title_change, inputs=[sec_title_tb, sections_list, sections_state], outputs=[sections_state])
        mode_radio.change(sec_mode_change, inputs=[mode_radio, sections_list, sections_state], outputs=[sections_state])
        sec_prompt_tb.change(sec_prompt_change, inputs=[sec_prompt_tb, sections_list, sections_state], outputs=[sections_state])
        sec_refs.change(sec_refs_change, inputs=[sec_refs, sections_list, sections_state], outputs=[sections_state])
        sec_res_dd.change(sec_res_change, inputs=[sec_res_dd, sections_list, sections_state], outputs=[sections_state])

        # Upload existing outline
        upload = gr.File(label="Upload Outline JSON", file_types=[".json"])
        def upload_action(file_obj):
            # Returns title, instruction, resources table, sections table, nested_state
            if not file_obj:
                return ["", "", [], [], []]
            raw = Path(file_obj.name).read_text()
            data = json.loads(raw)
            title = data.get("title", "")
            instr = data.get("general_instruction", "")
            # Resources
            res = [[r.get(k, "") for k in ["key", "description", "path", "merge_mode"]]
                   for r in data.get("resources", [])]
            # Sections
            sections = data.get("sections", [])
            secs_table = []
            nested = []
            for sec in sections:
                title_s = sec.get("title", "")
                prompt_s = sec.get("prompt", "") or ""
                refs_s = ",".join(sec.get("refs", []))
                rk = sec.get("resource_key", "") or ""
                secs_table.append([title_s, prompt_s, refs_s, rk])
                nested.append(sec.get("sections", []))
            return [title, instr, res, secs_table, nested]
        upload.upload(
            upload_action,
            inputs=[upload],
            outputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
        )

        # Validate outline
        validate_btn = gr.Button("Validate Outline")
        validate_output = gr.Textbox(label="Validation Result")
        def on_validate(title, instr, res_table, secs_table, nested):
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
            # Build sections with nested subsections
            sections = []
            for idx, row in enumerate(secs_table or []):
                cells = list(row) if isinstance(row, (list, tuple)) else []
                cells += [""] * (4 - len(cells))
                title_s, prompt_s, refs_s, rk = cells[:4]
                sec = {"title": title_s}
                if prompt_s:
                    sec["prompt"] = prompt_s
                    sec["refs"] = [r.strip() for r in refs_s.split(",") if r.strip()]
                elif rk:
                    sec["resource_key"] = rk
                # attach nested subsections
                if nested and idx < len(nested):
                    if nested[idx]:
                        sec["sections"] = nested[idx]
                sections.append(sec)
            outline = {
                "title": title,
                "general_instruction": instr,
                "resources": resources,
                "sections": sections
            }
            try:
                validate_outline(outline)
                return "Outline is valid."
            except Exception as e:
                return f"Validation error: {e}"
        validate_btn.click(
            on_validate,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[validate_output],
        )

        # Download outline without generating
        download_outline_btn = gr.Button("Download Outline JSON")
        download_outline_file = gr.File(label="Download Outline JSON")
        def download_outline(title, instr, res_table, secs_table, nested):
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
            # Build sections with nested subsections
            sections = []
            for idx, row in enumerate(secs_table or []):
                cells = list(row) if isinstance(row, (list, tuple)) else []
                cells += [""] * (4 - len(cells))
                title_s, prompt_s, refs_s, rk = cells[:4]
                sec = {"title": title_s}
                if prompt_s:
                    sec["prompt"] = prompt_s
                    sec["refs"] = [r.strip() for r in refs_s.split(",") if r.strip()]
                elif rk:
                    sec["resource_key"] = rk
                if nested and idx < len(nested) and nested[idx]:
                    sec["sections"] = nested[idx]
                sections.append(sec)
            outline = {
                "title": title,
                "general_instruction": instr,
                "resources": resources,
                "sections": sections
            }
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
            json.dump(outline, tmp, indent=2)
            tmp.close()
            return tmp.name
        download_outline_btn.click(
            download_outline,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[download_outline_file],
        )

        # Generate document
        generate_btn = gr.Button("Generate Document")
        output_md = gr.Markdown()
        download_doc_file = gr.File(label="Download Generated Document")
        def on_generate(title, instr, res_table, secs_table, nested):
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
            # Build sections with nested subsections
            sections = []
            for idx, row in enumerate(secs_table or []):
                cells = list(row) if isinstance(row, (list, tuple)) else []
                cells += [""] * (4 - len(cells))
                title_s, prompt_s, refs_s, rk = cells[:4]
                sec = {"title": title_s}
                if prompt_s:
                    sec["prompt"] = prompt_s
                    sec["refs"] = [r.strip() for r in refs_s.split(",") if r.strip()]
                elif rk:
                    sec["resource_key"] = rk
                if nested and idx < len(nested) and nested[idx]:
                    sec["sections"] = nested[idx]
                sections.append(sec)
            outline = {
                "title": title,
                "general_instruction": instr,
                "resources": resources,
                "sections": sections
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
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[output_md, download_doc_file],
        )

    return demo