"""
Editor UI builder for the Document Generator app, using Gradio Blocks.
"""

# flake8: noqa
import json
from pathlib import Path
import gradio as gr  # type: ignore
from document_generator.ui.components import resource_entry, section_entry


def make_resource_choices(res_list):
    """
    Generate dropdown choices: resource keys or index if key empty.
    Returns list of strings for gr.Dropdown.
    """
    choices = []
    for idx, r in enumerate(res_list or []):
        key = r.get("key", "") if isinstance(r, dict) else ""
        label = key.strip() or str(idx)
        choices.append(label)
    return choices


def make_section_choices(sec_list):
    """
    Generate dropdown choices: section titles or index if title empty.
    Returns list of strings for gr.Dropdown.
    """
    choices = []
    for idx, s in enumerate(sec_list or []):
        title = s.get("title", "") if isinstance(s, dict) else ""
        label = title.strip() or str(idx)
        choices.append(label)
    return choices


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
    # nested_state will be initialized inside Blocks to track nested subsections

    with gr.Blocks() as demo:
        gr.Markdown("# Document Generator")
        gr.Markdown("## Outline Editor")
        # Metadata inputs
        title_tb = gr.Textbox(label="Title", value="")
        instruction_tb = gr.TextArea(label="General Instruction", value="")

        # Resources table: key, description, path, merge_mode
        gr.Markdown("## Resources")
        resources_state = gr.State(initial_resources)
        resources_list = gr.Dropdown(choices=[], label="Select Resource", interactive=True)
        add_res_btn = gr.Button("Add Resource")
        remove_res_btn = gr.Button("Remove Resource")
        # Reuse resource_entry component
        key_tb, desc_tb, path_tb, file_upload, merge_mode_dd = resource_entry()

        # Resource callbacks
        def res_add(res_list):
            """Add a new empty resource to the list and update dropdown choices."""
            res_list = res_list or []
            res_list.append({"key": "", "description": "", "path": "", "merge_mode": ""})
            # Prepare dropdown choices: key or index labels
            choices = make_resource_choices(res_list)
            # Return updated list and update dropdown value to last choice
            value = choices[-1] if choices else ""
            return res_list, gr.update(choices=choices, value=value)

        def res_remove(res_list, sel):
            """Remove the selected resource and update dropdown choices."""
            res_list = res_list or []
            try:
                idx = int(sel.split(":", 1)[0])
            except Exception:
                return res_list
            if idx is not None and 0 <= idx < len(res_list):
                res_list.pop(idx)
            # Prepare dropdown choices: key or index labels
            choices = make_resource_choices(res_list)
            value = choices[-1] if choices else ""
            return res_list, gr.update(choices=choices, value=value)

        def res_select(sel, res_list):
            res_list = res_list or []
            # Parse index from "index: key" label
            # Determine selected index from key or numeric string
            idx = None
            if sel is not None:
                # Try matching on resource key
                for i, r in enumerate(res_list):
                    if isinstance(r, dict) and r.get("key", "") == sel:
                        idx = i
                        break
                # Fallback to numeric index
                if idx is None and isinstance(sel, str) and sel.isdigit():
                    idx = int(sel)
            if idx is None or idx < 0 or idx >= len(res_list):
                return "", "", None, "", res_list
            r = res_list[idx]
            return (
                r.get("key", ""),
                r.get("description", ""),
                r.get("path", ""),
                None,
                r.get("merge_mode", ""),
                res_list,
            )

        def res_key_change(val, sel, res_list):
            if sel is None:
                return res_list
            # Determine index from key or numeric
            idx = None
            if sel:
                if isinstance(sel, str) and sel.isdigit():
                    idx = int(sel)
                else:
                    for i, r in enumerate(res_list or []):
                        if r.get("key", "") == sel:
                            idx = i
                            break
            res_list = res_list or []
            if isinstance(idx, int) and 0 <= idx < len(res_list):
                res_list[idx]["key"] = val
            return res_list

        def res_desc_change(val, sel, res_list):
            if sel is None:
                return res_list
            idx = None
            if sel:
                if isinstance(sel, str) and sel.isdigit():
                    idx = int(sel)
                else:
                    for i, r in enumerate(res_list or []):
                        if r.get("key", "") == sel:
                            idx = i
                            break
            res_list = res_list or []
            if isinstance(idx, int) and 0 <= idx < len(res_list):
                res_list[idx]["description"] = val
            return res_list

        def res_path_change(val, sel, res_list):
            if sel is None:
                return res_list
            idx = None
            if sel:
                if isinstance(sel, str) and sel.isdigit():
                    idx = int(sel)
                else:
                    for i, r in enumerate(res_list or []):
                        if r.get("key", "") == sel:
                            idx = i
                            break
            res_list = res_list or []
            if isinstance(idx, int) and 0 <= idx < len(res_list):
                res_list[idx]["path"] = val
            return res_list

        def res_file_upload(file_obj, sel, res_list):
            if not file_obj or sel is None:
                return res_list
            idx = None
            if sel:
                if isinstance(sel, str) and sel.isdigit():
                    idx = int(sel)
                else:
                    for i, r in enumerate(res_list or []):
                        if r.get("key", "") == sel:
                            idx = i
                            break
            res_list = res_list or []
            if isinstance(idx, int) and 0 <= idx < len(res_list):
                res_list[idx]["path"] = file_obj.name
            return res_list

        def res_mm_change(val, sel, res_list):
            if sel is None:
                return res_list
            idx = None
            if sel:
                if isinstance(sel, str) and sel.isdigit():
                    idx = int(sel)
                else:
                    for i, r in enumerate(res_list or []):
                        if r.get("key", "") == sel:
                            idx = i
                            break
            res_list = res_list or []
            if isinstance(idx, int) and 0 <= idx < len(res_list):
                res_list[idx]["merge_mode"] = val
            return res_list

        add_res_btn.click(res_add, inputs=[resources_state], outputs=[resources_state, resources_list])
        remove_res_btn.click(
            res_remove, inputs=[resources_state, resources_list], outputs=[resources_state, resources_list]
        )
        resources_list.change(
            res_select,
            inputs=[resources_list, resources_state],
            outputs=[key_tb, desc_tb, path_tb, file_upload, merge_mode_dd, resources_state],
        )
        key_tb.change(res_key_change, inputs=[key_tb, resources_list, resources_state], outputs=[resources_state])
        desc_tb.change(res_desc_change, inputs=[desc_tb, resources_list, resources_state], outputs=[resources_state])
        path_tb.change(res_path_change, inputs=[path_tb, resources_list, resources_state], outputs=[resources_state])
        file_upload.change(
            res_file_upload, inputs=[file_upload, resources_list, resources_state], outputs=[resources_state]
        )
        merge_mode_dd.change(
            res_mm_change, inputs=[merge_mode_dd, resources_list, resources_state], outputs=[resources_state]
        )

        # State for nested subsections (placeholder)
        nested_state = gr.State(initial_sections)
        # Sections list and editor
        gr.Markdown("## Sections")
        sections_state = gr.State(initial_sections)
        sections_list = gr.Dropdown(choices=[], label="Select Section", interactive=True)
        add_sec_btn = gr.Button("Add Section")
        remove_sec_btn = gr.Button("Remove Section")
        # Reuse section_entry component
        sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, nested_acc = section_entry()

        # Update related dropdowns on resource list changes
        def update_resource_list(res_list):
            # Refresh main resource dropdown choices
            choices = make_resource_choices(res_list)
            # Select last choice by label
            value = choices[-1] if choices else None
            return gr.update(choices=choices, value=value)

        # Sync resource keys into section editors
        def update_section_key_choices(res_list):
            # Extract resource keys from state entries (dict or list)
            keys = []
            for r in res_list or []:
                if isinstance(r, dict):
                    keys.append(r.get("key", ""))
                elif isinstance(r, (list, tuple)) and r:
                    # assume first element is key string
                    keys.append(str(r[0]))
                else:
                    keys.append("")
            # Return updates for refs and resource key dropdown
            return gr.update(choices=keys), gr.update(choices=[""] + keys)

        resources_state.change(
            update_section_key_choices,
            inputs=[resources_state],
            outputs=[sec_refs, sec_res_dd],
        )
        resources_state.change(
            update_resource_list,
            inputs=[resources_state],
            outputs=[resources_list],
        )

        # Section callbacks
        def sec_add(sec_list):
            """Add a new empty section and update Dropdown choices."""
            sec_list = sec_list or []
            sec_list.append({"title": "", "refs": [], "prompt": "", "resource_key": None, "sections": []})
            choices = make_section_choices(sec_list)
            # Return updated list and select last choice by label
            value = choices[-1] if choices else ""
            return sec_list, gr.update(choices=choices, value=value)

        def sec_remove(sec_list, sel):
            """Remove the selected section and update Dropdown choices."""
            sec_list = sec_list or []
            idx = None
            try:
                idx = int(sel)
            except Exception:
                idx = None
            if idx is not None and 0 <= idx < len(sec_list):
                sec_list.pop(idx)
            choices = make_section_choices(sec_list)
            value = choices[-1] if choices else ""
            return sec_list, gr.update(choices=choices, value=value)

        def sec_select(sel, sec_list):
            sec_list = sec_list or []
            # Determine selected index from title or numeric string
            idx = None
            if sel is not None:
                # Try matching on title
                for i, s in enumerate(sec_list):
                    if isinstance(s, dict) and s.get("title", "") == sel:
                        idx = i
                        break
                # Fallback to numeric
                if idx is None and sel.isdigit():
                    idx = int(sel)
            if idx is None or idx < 0 or idx >= len(sec_list):
                return "", "prompt", [], "", "", sec_list
            s = sec_list[idx]
            mode = "static" if s.get("resource_key") else "prompt"
            refs = s.get("refs", [])
            return (
                s.get("title", ""),
                mode,
                s.get("prompt", ""),
                refs,
                s.get("resource_key", ""),
                sec_list,
            )

        def sec_title_change(val, sel, sec_list):
            if sel is None:
                return sec_list
            try:
                idx = int(sel)
            except Exception:
                return sec_list
            sec_list = sec_list or []
            if isinstance(idx, int) and 0 <= idx < len(sec_list):
                sec_list[idx]["title"] = val
            return sec_list

        def sec_mode_change(val, sel, sec_list):
            if sel is None:
                return sec_list
            try:
                idx = int(sel)
            except Exception:
                return sec_list
            sec_list = sec_list or []
            if isinstance(idx, int) and 0 <= idx < len(sec_list):
                if val == "prompt":
                    sec_list[idx].pop("resource_key", None)
                else:
                    sec_list[idx].pop("prompt", None)
                    sec_list[idx].pop("refs", None)
            return sec_list

        def sec_prompt_change(val, sel, sec_list):
            if sel is None:
                return sec_list
            try:
                idx = int(sel)
            except Exception:
                return sec_list
            sec_list = sec_list or []
            if isinstance(idx, int) and 0 <= idx < len(sec_list):
                sec_list[idx]["prompt"] = val
            return sec_list

        def sec_refs_change(val, sel, sec_list):
            if sel is None:
                return sec_list
            try:
                idx = int(sel)
            except Exception:
                return sec_list
            sec_list = sec_list or []
            if isinstance(idx, int) and 0 <= idx < len(sec_list):
                sec_list[idx]["refs"] = val
            return sec_list

        def sec_res_change(val, sel, sec_list):
            if sel is None:
                return sec_list
            try:
                idx = int(sel)
            except Exception:
                return sec_list
            sec_list = sec_list or []
            if isinstance(idx, int) and 0 <= idx < len(sec_list):
                sec_list[idx]["resource_key"] = val
            return sec_list

        add_sec_btn.click(sec_add, inputs=[sections_state], outputs=[sections_state, sections_list])
        remove_sec_btn.click(
            sec_remove, inputs=[sections_state, sections_list], outputs=[sections_state, sections_list]
        )

        # Refresh section list when titles change
        def update_section_list(sec_list):
            choices = make_section_choices(sec_list)
            # Select last choice by label
            value = choices[-1] if choices else None
            return gr.update(choices=choices, value=value)

        sections_state.change(
            update_section_list,
            inputs=[sections_state],
            outputs=[sections_list],
        )
        sections_list.change(
            sec_select,
            inputs=[sections_list, sections_state],
            outputs=[sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, sections_state],
        )
        sec_title_tb.change(
            sec_title_change, inputs=[sec_title_tb, sections_list, sections_state], outputs=[sections_state]
        )
        mode_radio.change(sec_mode_change, inputs=[mode_radio, sections_list, sections_state], outputs=[sections_state])
        sec_prompt_tb.change(
            sec_prompt_change, inputs=[sec_prompt_tb, sections_list, sections_state], outputs=[sections_state]
        )
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
            # Build resource state as list of dicts
            res_list = []
            for r in data.get("resources", []):
                item = {"key": r.get("key", ""), "description": r.get("description", ""), "path": r.get("path", "")}
                if r.get("merge_mode"):
                    item["merge_mode"] = r.get("merge_mode")
                res_list.append(item)
            # Build section state and nested subsections
            sec_list = []
            nested = []
            for sec in data.get("sections", []):
                item = {"title": sec.get("title", "")}
                if sec.get("prompt") is not None:
                    item["prompt"] = sec.get("prompt", "")
                    item["refs"] = list(sec.get("refs", []))
                if sec.get("resource_key") is not None:
                    item["resource_key"] = sec.get("resource_key", "")
                sec_list.append(item)
                nested.append(sec.get("sections", []))
            # Update dropdowns using helper functions
            res_choices = make_resource_choices(res_list)
            sec_choices = make_section_choices(sec_list)
            return [
                title,
                instr,
                res_list,
                sec_list,
                nested,
                gr.update(choices=res_choices, value=res_choices[-1] if res_choices else ""),
                gr.update(choices=sec_choices, value=sec_choices[-1] if sec_choices else ""),
            ]

        upload.upload(
            upload_action,
            inputs=[upload],
            outputs=[
                title_tb,
                instruction_tb,
                resources_state,
                sections_state,
                nested_state,
                resources_list,
                sections_list,
            ],
        )

        # Validate outline
        validate_btn = gr.Button("Validate Outline")
        validate_output = gr.Textbox(label="Validation Result")
        # JSON preview rendered via gr.JSON for interactive inspection
        json_preview = gr.JSON(label="Outline JSON Preview")

        def on_validate(title, instr, res_table, secs_table, nested):
            errors = []
            # Top-level required fields
            title_val = (title or "").strip()
            instr_val = (instr or "").strip()
            if not title_val:
                errors.append("Title is required.")
            if not instr_val:
                errors.append("General instruction is required.")
            # Process resources: list of dicts
            resources = []
            valid_keys = []
            for idx, r in enumerate(res_table or []):
                key = (r.get("key", "") or "").strip()
                desc = (r.get("description", "") or "").strip()
                path = (r.get("path", "") or "").strip()
                mm = (r.get("merge_mode", "") or "").strip()
                # Skip completely empty rows
                if not key and not desc and not path:
                    continue
                if not key:
                    errors.append(f"Resource {idx} missing key.")
                if not desc:
                    errors.append(f"Resource {idx} missing description.")
                if not path:
                    errors.append(f"Resource {idx} missing path.")
                item = {"key": key, "description": desc, "path": path}
                if mm:
                    item["merge_mode"] = mm
                resources.append(item)
                valid_keys.append(key)
            # Process sections: list of dicts, with nested subsections
            sections = []
            for idx, sec in enumerate(secs_table or []):
                title_s = (sec.get("title", "") or "").strip()
                prompt_s = (sec.get("prompt", "") or "").strip()
                refs_list = sec.get("refs", []) or []
                rk = (sec.get("resource_key", "") or "").strip()
                subs = nested[idx] if nested and idx < len(nested) else []
                # Skip completely empty rows
                if not title_s and not prompt_s and not refs_list and not rk and not subs:
                    continue
                if not title_s:
                    errors.append(f"Section {idx} missing title.")
                item = {"title": title_s}
                if prompt_s:
                    item["prompt"] = prompt_s
                    for ref in refs_list:
                        if ref not in valid_keys:
                            errors.append(f"Section {idx} references unknown resource '{ref}'.")
                    item["refs"] = refs_list
                elif rk:
                    if rk not in valid_keys:
                        errors.append(f"Section {idx} references unknown resource '{rk}'.")
                    item["resource_key"] = rk
                else:
                    errors.append(f"Section {idx} must have either a prompt or a resource key.")
                if subs:
                    item["sections"] = subs
                sections.append(item)
            if not sections:
                errors.append("At least one section is required.")
            # Build final outline
            outline = {
                "title": title_val,
                "general_instruction": instr_val,
                "resources": resources,
                "sections": sections,
            }
            if errors:
                return "Validation error: " + "; ".join(errors), outline
            try:
                validate_outline(outline)
                return "Outline is valid.", outline
            except Exception as e:
                return f"Validation error: {e}", outline

        validate_btn.click(
            on_validate,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[validate_output, json_preview],
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
            outline = {"title": title, "general_instruction": instr, "resources": resources, "sections": sections}
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
            outline = {"title": title, "general_instruction": instr, "resources": resources, "sections": sections}
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
