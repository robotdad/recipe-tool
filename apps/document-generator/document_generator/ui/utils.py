"""
Utility functions for the Document Generator editor brick.
"""

from document_generator.schema.validator import validate_outline


def build_outline_data(title, instr, res_table, secs_table, nested):
    """
    Build the outline dict from editor state: title, instruction, resources table,
    sections table, and nested subsections. Skips fully empty rows.
    """
    title_val = (title or "").strip()
    instr_val = (instr or "").strip()
    # Resources
    resources = []
    for row in res_table or []:
        cells = list(row) if isinstance(row, (list, tuple)) else []
        cells += [""] * (4 - len(cells))
        key, desc, path, mm = [c.strip() for c in cells[:4]]
        if not key and not desc and not path:
            continue
        r = {"key": key, "description": desc, "path": path}
        if mm:
            r["merge_mode"] = mm
        resources.append(r)
    # Sections
    sections = []
    for idx, row in enumerate(secs_table or []):
        cells = list(row) if isinstance(row, (list, tuple)) else []
        cells += [""] * (4 - len(cells))
        title_s, prompt_s, refs_s, rk = [c.strip() for c in cells[:4]]
        subs = nested[idx] if nested and idx < len(nested) else []
        if not title_s and not prompt_s and not refs_s and not rk and not subs:
            continue
        sec = {"title": title_s}
        if prompt_s:
            sec["prompt"] = prompt_s
            refs = [r.strip() for r in refs_s.split(",") if r.strip()]
            sec["refs"] = refs
        elif rk:
            sec["resource_key"] = rk
        if subs:
            sec["sections"] = subs
        sections.append(sec)
    return {
        "title": title_val,
        "general_instruction": instr_val,
        "resources": resources,
        "sections": sections,
    }


def validate_outline_and_get_data(title, instr, res_table, secs_table, nested):
    """
    Build and validate the outline, returning (message, outline_dict).
    """
    outline = build_outline_data(title, instr, res_table, secs_table, nested)
    errors = []
    # Required top-level
    if not outline["title"]:
        errors.append("Title is required.")
    if not outline["general_instruction"]:
        errors.append("General instruction is required.")
    # Resource checks
    valid_keys = [r.get("key", "") for r in outline.get("resources", [])]
    for idx, r in enumerate(outline.get("resources", [])):
        if not r.get("key"):
            errors.append(f"Resource {idx} missing key.")
        if not r.get("description"):
            errors.append(f"Resource {idx} missing description.")
        if not r.get("path"):
            errors.append(f"Resource {idx} missing path.")
    # Sections exist
    if not outline.get("sections", []):
        errors.append("At least one section is required.")
    # Section checks
    for idx, sec in enumerate(outline.get("sections", [])):
        if not sec.get("title"):
            errors.append(f"Section {idx} missing title.")
        has_prompt = "prompt" in sec
        has_rk = "resource_key" in sec
        if has_prompt:
            for ref in sec.get("refs", []):
                if ref not in valid_keys:
                    errors.append(f"Section {idx} references unknown resource '{ref}'.")
        elif has_rk:
            if sec.get("resource_key") not in valid_keys:
                errors.append(f"Section {idx} references unknown resource '{sec.get('resource_key')}'.")
        else:
            errors.append(f"Section {idx} must have either a prompt or a resource key.")
    # Final result
    if errors:
        return "Validation error: " + "; ".join(errors), outline
    try:
        validate_outline(outline)
        return "Outline is valid.", outline
    except Exception as e:
        return f"Validation error: {e}", outline


def make_resource_choices(res_list):
    """
    Generate dropdown choices: resource keys or index if key empty.
    Returns list of strings for gr.Dropdown.
    """
    choices = []
    for idx, r in enumerate(res_list or []):
        key = r.get("key", "") if isinstance(r, dict) else ""
        choices.append(key.strip() or str(idx))
    return choices


def make_section_choices(sec_list):
    """
    Generate dropdown choices: section titles or index if title empty.
    Returns list of strings for gr.Dropdown.
    """
    choices = []
    for idx, s in enumerate(sec_list or []):
        title = s.get("title", "") if isinstance(s, dict) else ""
        choices.append(title.strip() or str(idx))
    return choices
