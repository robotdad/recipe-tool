"""
Two-column layout for the Document Generator editor using Gradio Blocks.
"""

import gradio as gr
import gradio.themes

from document_generator.ui.callbacks import (
    add_resource,
    add_section,
    generate_document_callback,
    get_download_outline,
    get_uploaded_outline,
    remove_resource,
    remove_section,
    select_resource,
    select_section,
    update_resource_description,
    update_resource_key,
    update_resource_list,
    update_resource_merge_mode,
    update_resource_path,
    update_section_key_choices,
    update_section_list,
    update_section_mode,
    update_section_prompt,
    update_section_refs,
    update_section_resource_key,
    update_section_title,
    upload_resource_file,
)
from document_generator.ui.components import resource_entry, section_entry
from document_generator.ui.utils import validate_outline_and_get_data


def build_editor() -> gr.Blocks:
    """
    Build and return the full Gradio Blocks interface with a two-column layout.
    """
    with gr.Blocks(title="Document Generator", theme=gradio.themes.Citrus()) as demo:
        # Persistent state for resources and sections
        initial_resources = []
        initial_sections = []
        resources_state = gr.State(initial_resources)
        sections_state = gr.State(initial_sections)
        nested_state = gr.State(initial_sections)

        gr.Markdown("# Document Generator")
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Outline Editor")
                # Metadata
                title_tb = gr.Textbox(label="Title", placeholder="Document title")
                instruction_tb = gr.TextArea(label="General Instruction", placeholder="General instruction")

                # Resources block: selector + editor
                with gr.Accordion("Resources", open=True):
                    resources_list = gr.Dropdown(
                        choices=[], label="Select Resource", interactive=True, allow_custom_value=True
                    )
                    add_res_btn = gr.Button("Add Resource")
                    remove_res_btn = gr.Button("Remove Resource")
                    with gr.Column(visible=False) as resource_detail_panel:
                        key_tb, desc_tb, path_tb, file_upload, merge_mode_dd = resource_entry()

                # Sections block: selector + editor
                with gr.Accordion("Sections", open=True):
                    sections_list = gr.Dropdown(
                        choices=[], label="Select Section", interactive=True, allow_custom_value=True
                    )
                    add_sec_btn = gr.Button("Add Section")
                    remove_sec_btn = gr.Button("Remove Section")
                    with gr.Column(visible=False) as section_detail_panel:
                        sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, nested_acc = section_entry()

            with gr.Column():
                gr.Markdown("## Document Generation")
                # Upload, Validate, Preview, Download Outline
                upload_outline_button = gr.File(label="Upload Outline JSON", file_types=[".json"])
                validate_btn = gr.Button("Validate Outline")
                validate_output = gr.Textbox(label="Validation Result")
                json_preview = gr.JSON(label="Outline JSON Preview")
                download_outline_button = gr.Button("Download Outline JSON")
                download_outline_file = gr.File(label="Download Outline JSON")
                # Generate button after validation
                generate_btn = gr.Button("Generate Document")
                # Generation output controls
                output_md = gr.Markdown(label="Generated Document")
                download_doc_button = gr.File(label="Download Generated Document")

        # Hook up resource callbacks
        add_res_btn.click(add_resource, inputs=[resources_state], outputs=[resources_state, resources_list])
        remove_res_btn.click(
            remove_resource, inputs=[resources_state, resources_list], outputs=[resources_state, resources_list]
        )
        resources_list.change(
            select_resource,
            inputs=[resources_list, resources_state],
            outputs=[key_tb, desc_tb, path_tb, file_upload, merge_mode_dd, resources_state],
        )
        # Show/hide resource detail panel based on selection
        resources_list.change(
            lambda sel: gr.update(visible=bool(sel)),
            inputs=[resources_list],
            outputs=[resource_detail_panel],
        )
        key_tb.change(update_resource_key, inputs=[key_tb, resources_list, resources_state], outputs=[resources_state])
        desc_tb.change(
            update_resource_description, inputs=[desc_tb, resources_list, resources_state], outputs=[resources_state]
        )
        path_tb.change(
            update_resource_path, inputs=[path_tb, resources_list, resources_state], outputs=[resources_state]
        )
        file_upload.change(
            upload_resource_file, inputs=[file_upload, resources_list, resources_state], outputs=[resources_state]
        )
        merge_mode_dd.change(
            update_resource_merge_mode,
            inputs=[merge_mode_dd, resources_list, resources_state],
            outputs=[resources_state],
        )
        resources_state.change(update_resource_list, inputs=[resources_state, resources_list], outputs=[resources_list])
        resources_state.change(update_section_key_choices, inputs=[resources_state, sec_refs, sec_res_dd], outputs=[sec_refs, sec_res_dd])

        # Hook up section callbacks
        add_sec_btn.click(add_section, inputs=[sections_state], outputs=[sections_state, sections_list])
        remove_sec_btn.click(
            remove_section, inputs=[sections_state, sections_list], outputs=[sections_state, sections_list]
        )
        sections_state.change(update_section_list, inputs=[sections_state, sections_list], outputs=[sections_list])
        sections_list.change(
            select_section,
            inputs=[sections_list, sections_state],
            outputs=[sec_title_tb, mode_radio, sec_prompt_tb, sec_refs, sec_res_dd, sections_state],
        )
        # Show/hide section detail panel based on selection
        sections_list.change(
            lambda sel: gr.update(visible=bool(sel)),
            inputs=[sections_list],
            outputs=[section_detail_panel],
        )
        sec_title_tb.change(
            update_section_title, inputs=[sec_title_tb, sections_list, sections_state], outputs=[sections_state]
        )
        mode_radio.change(
            update_section_mode, inputs=[mode_radio, sections_list, sections_state], outputs=[sections_state]
        )
        sec_prompt_tb.change(
            update_section_prompt, inputs=[sec_prompt_tb, sections_list, sections_state], outputs=[sections_state]
        )
        sec_refs.change(update_section_refs, inputs=[sec_refs, sections_list, sections_state], outputs=[sections_state])
        sec_res_dd.change(
            update_section_resource_key, inputs=[sec_res_dd, sections_list, sections_state], outputs=[sections_state]
        )

        # Upload and validation callbacks
        upload_outline_button.upload(
            get_uploaded_outline,
            inputs=[upload_outline_button],
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
        validate_btn.click(
            validate_outline_and_get_data,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[validate_output, json_preview],
        )
        download_outline_button.click(
            get_download_outline,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[download_outline_file],
        )

        # Generate document callback
        generate_btn.click(
            generate_document_callback,
            inputs=[title_tb, instruction_tb, resources_state, sections_state, nested_state],
            outputs=[output_md, download_doc_button],
        )
    return demo
