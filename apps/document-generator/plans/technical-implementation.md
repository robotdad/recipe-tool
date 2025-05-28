# Document Generator - Technical Implementation Plan

## Overview

This document provides the technical blueprint for implementing the simplified Document Generator UI, following our "bricks & studs" modular philosophy and ruthless simplicity principles.

## Architecture

### Directory Structure
```
# First, preserve old UI
mv document_generator_app/ui/ document_generator_app/ui_old/

# Then create new simplified structure
document_generator_app/
└── ui/                       # New simplified UI
    ├── __init__.py
    ├── components.py         # All UI components
    ├── callbacks.py          # ~5 callback handlers
    ├── layout.py            # Main Blocks app
    └── utils.py             # Reuse existing utilities
```

## Core Components

### 1. State Management (Inline in callbacks.py)

```python
# No separate state class needed - just track in Gradio State
def create_initial_state():
    """Create initial app state."""
    return {
        "outline": Outline(),
        "selected_type": None,     # "resource" or "section"
        "selected_id": None,        # e.g., "resource_0" or "section_1_2"
    }

def get_section_at_path(sections, path):
    """Navigate to a section by index path."""
    current = sections
    for idx in path:
        if int(idx) < len(current):
            if len(path) == 1:
                return current[int(idx)]
            current = current[int(idx)].sections
    return None
```

### 2. UI Components (`components.py`)

```python
"""All UI components for the simplified document generator."""
import gradio as gr

def create_resource_list():
    """Create the resource list UI."""
    with gr.Column():
        gr.Markdown("### 📚 Resources")
        with gr.Row():
            add_btn = gr.Button("➕ Add", size="sm")
            remove_btn = gr.Button("➖ Remove", size="sm")
        
        # Container for dynamic resource buttons
        resource_container = gr.Column()
            
    return add_btn, remove_btn, resource_container

def create_section_list():
    """Create the section list UI with subsection support."""
    with gr.Column():
        gr.Markdown("### 📑 Sections")
        with gr.Row():
            add_btn = gr.Button("➕ Add", size="sm")
            add_sub_btn = gr.Button("➕ Sub", size="sm")
            remove_btn = gr.Button("➖ Remove", size="sm")
        
        # Container for dynamic section buttons
        section_container = gr.Column()
            
    return add_btn, add_sub_btn, remove_btn, section_container

@gr.render(inputs=[gr.State()])
def render_resource_items(state):
    """Dynamically render resource list items."""
    if not state or not state.outline.resources:
        gr.Markdown("*No resources yet*", elem_classes=["empty-state"])
        return
        
    for i, resource in enumerate(state.outline.resources):
        resource_id = f"resource_{i}"
        is_selected = (state.selected_type == "resource" and 
                      state.selected_id == resource_id)
        
        btn = gr.Button(
            value=f"📄 {resource.key or f'Resource {i+1}'}",
            variant="primary" if is_selected else "secondary",
            size="sm",
            elem_id=resource_id
        )
        btn.click(
            fn=select_item,
            inputs=[gr.State(resource_id), gr.State("resource")],
            outputs=[state_component, editor_container]
        )

def render_section_items(state, container):
    """Render section list items with nesting (max 4 levels)."""
    if not state or not state["outline"].sections:
        with container:
            gr.Markdown("*No sections yet*")
        return
    
    def render_sections(sections, path=[], container=container):
        for i, section in enumerate(sections):
            if len(path) >= 4:  # Limit nesting to 4 levels
                continue
                
            current_path = path + [str(i)]
            section_id = f"section_{'_'.join(current_path)}"
            is_selected = (state["selected_type"] == "section" and
                          state["selected_id"] == section_id)
            
            # Simple indentation
            indent = "　" * len(path)
            
            with container:
                btn = gr.Button(
                    value=f"{indent}📑 {section.title or f'Section {'.'.join(current_path)}'}",
                    variant="primary" if is_selected else "secondary",
                    size="sm"
                )
            
            # Render subsections
            if section.sections and len(path) < 3:
                render_sections(section.sections, current_path, container)
    
    render_sections(state["outline"].sections)
```

def create_resource_editor():
    """Resource editor form."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### 📄 Resource Details")
        
        key = gr.Textbox(label="Resource Key", placeholder="unique_key")
        description = gr.TextArea(label="Description", lines=2)
        path = gr.Textbox(label="Path or URL", placeholder="https://... or /path/to/file")
        file_upload = gr.File(label="Or Upload File")
        merge_mode = gr.Dropdown(["concat", "dict"], label="Merge Mode", value="concat")
        
        save_btn = gr.Button("💾 Save", variant="primary")
    
    return {
        "container": container,
        "key": key,
        "description": description,
        "path": path,
        "file": file_upload,
        "merge_mode": merge_mode,
        "save": save_btn
    }

def create_section_editor():
    """Section editor form."""
    with gr.Column(visible=False) as container:
        gr.Markdown("### 📑 Section Details")
        
        title = gr.Textbox(label="Section Title")
        mode = gr.Radio(["Prompt", "Static"], label="Mode", value="Prompt")
        
        # Prompt mode
        with gr.Column() as prompt_container:
            prompt = gr.TextArea(label="Generation Prompt", lines=4)
            refs = gr.CheckboxGroup(label="Reference Resources", choices=[])
        
        # Static mode
        with gr.Column(visible=False) as static_container:
            resource_key = gr.Dropdown(label="Source Resource", choices=[])
        
        save_btn = gr.Button("💾 Save", variant="primary")
    
    return {
        "container": container,
        "title": title,
        "mode": mode,
        "prompt": prompt,
        "refs": refs,
        "resource_key": resource_key,
        "prompt_container": prompt_container,
        "static_container": static_container,
        "save": save_btn
    }
```

### 4. Main Application (`app.py`)

```python
"""Simplified Document Generator UI."""
import gradio as gr
from document_generator_app.ui_v2.state import AppState
from document_generator_app.ui_v2.components import lists, editors
from document_generator_app.ui_v2.callbacks import create_callbacks
from document_generator_app.models.outline import Outline

def create_app() -> gr.Blocks:
    """Create the main Gradio Blocks application."""
    
    with gr.Blocks(title="Document Generator", theme="soft") as app:
        # Initialize state
        state = gr.State(AppState(outline=Outline()))
        
        gr.Markdown("# 📄 Document Generator")
        gr.Markdown("Create structured documents with AI assistance")
        
        with gr.Row():
            # Left Column - Lists
            with gr.Column(scale=2, min_width=300):
                # Document metadata
                title = gr.Textbox(
                    label="Document Title",
                    placeholder="Enter your document title..."
                )
                instructions = gr.TextArea(
                    label="General Instructions",
                    placeholder="Overall guidance for document generation...",
                    lines=3
                )
                
                # Resources section
                resource_list, add_resource, remove_resource = lists.create_resource_list()
                
                # Sections section  
                section_list, add_section, remove_section = lists.create_section_list()
                
                # Action buttons
                with gr.Row():
                    upload_btn = gr.UploadButton(
                        "📤 Upload Outline",
                        file_types=[".json"]
                    )
                    download_btn = gr.Button("📥 Download Outline")
                    validate_btn = gr.Button("✓ Validate")
            
            # Right Column - Editor
            with gr.Column(scale=3, min_width=400):
                # Editor container (dynamically shows appropriate editor)
                with gr.Column() as editor_container:
                    empty_state = editors.create_empty_state()
                    resource_editor = editors.create_resource_editor()
                    section_editor = editors.create_section_editor()
                
                # Generation section
                gr.Markdown("---")
                with gr.Row():
                    generate_btn = gr.Button(
                        "🚀 Generate Document",
                        variant="primary",
                        scale=2
                    )
                    preview_btn = gr.Button("👁 Preview JSON", scale=1)
                
                # Output area
                with gr.Column(visible=False) as output_container:
                    output_markdown = gr.Markdown()
                    download_doc_btn = gr.DownloadButton(
                        "📥 Download Document",
                        visible=False
                    )
        
        # Connect callbacks
        callbacks = create_callbacks(
            state=state,
            components={
                'title': title,
                'instructions': instructions,
                'resource_list': resource_list,
                'section_list': section_list,
                'resource_editor': resource_editor,
                'section_editor': section_editor,
                'editor_container': editor_container,
                'output_container': output_container,
                'output_markdown': output_markdown,
                'download_doc_btn': download_doc_btn
            }
        )
        
        # Wire up all the callbacks
        callbacks.connect_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch()
```

### 5. Simplified Callbacks (`callbacks.py`)

```python
"""Just 5 main callbacks instead of 15+."""
from document_generator_app.models.outline import Resource, Section

def select_item(item_id, item_type, state):
    """Handle clicking on a list item."""
    state["selected_id"] = item_id
    state["selected_type"] = item_type
    return state

def add_resource(state):
    """Add new resource and select it."""
    state["outline"].resources.append(Resource())
    state["selected_id"] = f"resource_{len(state['outline'].resources) - 1}"
    state["selected_type"] = "resource"
    return state

def add_section(state, as_subsection=False):
    """Add new section (top-level or as subsection of selected)."""
    new_section = Section(title="New Section")
    
    if as_subsection and state["selected_type"] == "section":
        # Add as subsection of selected section
        path = state["selected_id"].split("_")[1:]
        parent = get_section_at_path(state["outline"].sections, path[:-1])
        if parent and len(path) < 4:  # Max 4 levels
            parent.sections.append(new_section)
            state["selected_id"] = f"section_{'_'.join(path + [str(len(parent.sections) - 1)])}"
    else:
        # Add as top-level section
        state["outline"].sections.append(new_section)
        state["selected_id"] = f"section_{len(state['outline'].sections) - 1}"
    
    state["selected_type"] = "section"
    return state

def save_item(form_data, state):
    """Save changes to selected item."""
    if state["selected_type"] == "resource":
        idx = int(state["selected_id"].split("_")[1])
        res = state["outline"].resources[idx]
        res.key = form_data["key"]
        res.description = form_data["description"]
        res.path = form_data["file"].name if form_data["file"] else form_data["path"]
        res.merge_mode = form_data["merge_mode"]
    elif state["selected_type"] == "section":
        path = state["selected_id"].split("_")[1:]
        sec = get_section_at_path(state["outline"].sections, path)
        sec.title = form_data["title"]
        if form_data["mode"] == "Prompt":
            sec.prompt = form_data["prompt"]
            sec.refs = form_data["refs"]
            sec.resource_key = None
        else:
            sec.resource_key = form_data["resource_key"]
            sec.prompt = None
            sec.refs = []
    return state

def remove_selected(state):
    """Remove the selected item."""
    if state["selected_type"] == "resource":
        idx = int(state["selected_id"].split("_")[1])
        state["outline"].resources.pop(idx)
    elif state["selected_type"] == "section":
        # Handle nested section removal
        path = state["selected_id"].split("_")[1:]
        if len(path) == 1:
            state["outline"].sections.pop(int(path[0]))
        else:
            parent = get_section_at_path(state["outline"].sections, path[:-1])
            parent.sections.pop(int(path[-1]))
    
    state["selected_id"] = None
    state["selected_type"] = None
    return state
```

## Key Implementation Patterns

### Direct Selection Instead of Dropdowns
- Click items to select them
- Selected item shows in editor on right
- No complex dropdown state management

### Simple Subsection Handling  
- "+Add" creates top-level sections
- "+Sub" creates subsection under selected section
- Max 4 levels deep (keeps it simple)
- Visual indentation shows hierarchy

### Minimal State
- Just track outline data and what's selected
- 5 callbacks instead of 15+
- No complex state synchronization

## Migration Steps

1. `mv ui/ ui_old/` - Move old UI aside
2. Create new simplified UI in `ui/`
3. Test all features work
4. `rm -rf ui_old/` - Delete old code

## Result

- **50% less code** 
- **Much cleaner UX**
- **Easier to maintain**
- **Ready for AI regeneration**

The new implementation embodies our philosophy: ruthlessly simple, directly solving the user's needs without unnecessary complexity.