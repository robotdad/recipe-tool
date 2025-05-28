# Document Generator - Simplified UI Plan

## Executive Summary

This plan outlines a redesigned, simplified user interface for the Document Generator app that follows our implementation and modular design philosophies. The new design emphasizes clarity, direct manipulation, and a clean two-column layout that separates list management from detail editing.

## Current Problems

1. **Over-engineered complexity**: Dropdown selectors with hidden detail panels create confusion
2. **Excessive state management**: 15+ callback functions managing interconnected state
3. **Poor UX flow**: Users must select from dropdowns to see/edit items
4. **Unclear visual hierarchy**: Everything crammed into accordions in a single column

## New Design Vision

### Layout Structure

```
┌─────────────────────────┬─────────────────────────┐
│     LEFT COLUMN         │     RIGHT COLUMN        │
│ (List Management)       │ (Detail Editor)         │
├─────────────────────────┼─────────────────────────┤
│ Document Title [____]   │                         │
│                         │ [Empty State Message]   │
│ General Instructions    │   or                    │
│ [__________________]    │ [Selected Item Editor]  │
│                         │                         │
│ Resources               │                         │
│ [+Add] [-Remove]        │                         │
│ • Resource 1            │                         │
│ • Resource 2            │                         │
│                         │                         │
│ Sections                │                         │
│ [+Add] [+Sub] [-Remove] │                         │
│ • Section 1             │                         │
│ • Section 2             │                         │
│   • Section 2.1         │                         │
│     • Section 2.1.1     │                         │
│   • Section 2.2         │                         │
│ • Section 3             │                         │
│                         │                         │
└─────────────────────────┴─────────────────────────┘
```

### Subsection Handling

**Simple approach for nesting (supports up to 4 levels):**
1. Select a section to make it the "parent"
2. Click "+Sub" to add a subsection under selected parent
3. Click "+Add" to add a new top-level section
4. Visual indentation shows hierarchy clearly

### Key Design Principles

1. **Direct Manipulation**: Click items in the list to edit them
2. **Clear Visual Hierarchy**: List on left, details on right
3. **Minimal State**: Only track the selected item and the data
4. **Progressive Disclosure**: Show detail editor only when needed

## Implementation Approach

### 1. Component Structure (Following Modular Philosophy)

```
# Move old UI out of the way first
mv ui/ ui_old/

# Then create new structure directly
ui/
├── components.py          # All UI components (lists and editors)
├── callbacks.py           # Simplified callback handlers (~5 total)
├── layout.py             # Main Blocks layout
└── utils.py              # Reuse existing outline utilities
```

### 2. State Management (Ruthless Simplicity)

```python
# Minimal state - just what we need
app_state = {
    "outline": Outline(),           # The data model
    "selected_type": None,          # "resource" or "section"
    "selected_index": None,         # Index of selected item
}
```

### 3. UI Components

#### Left Column Components

**Document Metadata**
```python
def document_metadata():
    """Simple title and instruction inputs"""
    title = gr.Textbox(label="Document Title", placeholder="Enter document title")
    instructions = gr.TextArea(
        label="General Instructions", 
        placeholder="Overall guidance for document generation",
        lines=3
    )
    return title, instructions
```

**Resource List**
```python
def resource_list(resources):
    """Display resources as a simple clickable list"""
    with gr.Group():
        gr.Markdown("### Resources")
        with gr.Row():
            add_btn = gr.Button("➕ Add", scale=1)
            remove_btn = gr.Button("➖ Remove", scale=1)
        
        # Simple list display - each item is clickable
        resource_items = []
        for i, res in enumerate(resources):
            btn = gr.Button(
                f"📄 {res.key or 'Untitled Resource'}",
                variant="secondary",
                size="sm"
            )
            resource_items.append(btn)
    
    return add_btn, remove_btn, resource_items
```

**Section List** 
```python
def section_list(sections, level=0):
    """Display sections with visual nesting"""
    section_items = []
    for i, sec in enumerate(sections):
        # Indent based on level
        indent = "　" * level  # Using full-width space
        btn = gr.Button(
            f"{indent}📑 {sec.title or 'Untitled Section'}",
            variant="secondary", 
            size="sm"
        )
        section_items.append((level, i, btn))
        
        # Recursively add subsections
        if sec.sections:
            section_items.extend(section_list(sec.sections, level + 1))
    
    return section_items
```

#### Right Column Components

**Empty State**
```python
def empty_state():
    """Show when nothing is selected"""
    gr.Markdown("""
    ### 👈 Select an item to edit
    
    Click on a resource or section in the left panel to view and edit its details.
    
    **Tips:**
    - Use ➕ Add to create new items
    - Click any item to edit it
    - Use ➖ Remove to delete the selected item
    """)
```

**Resource Editor**
```python
def resource_editor():
    """Edit form for a selected resource"""
    with gr.Column():
        gr.Markdown("### 📄 Resource Details")
        
        key = gr.Textbox(label="Resource Key", placeholder="unique_key")
        description = gr.TextArea(
            label="Description", 
            placeholder="What this resource contains",
            lines=2
        )
        
        gr.Markdown("#### Source")
        source_type = gr.Radio(
            ["URL", "File Upload", "Local Path"],
            label="Source Type",
            value="URL"
        )
        
        with gr.Column(visible=True) as url_input:
            url = gr.Textbox(label="URL", placeholder="https://...")
        
        with gr.Column(visible=False) as file_input:
            file = gr.File(label="Upload File")
            
        with gr.Column(visible=False) as path_input:
            path = gr.Textbox(label="File Path", placeholder="/path/to/file")
        
        merge_mode = gr.Dropdown(
            ["concat", "dict"],
            label="Merge Mode",
            value="concat",
            info="How to combine this resource with others"
        )
        
        save_btn = gr.Button("💾 Save Changes", variant="primary")
```

**Section Editor**
```python  
def section_editor():
    """Edit form for a selected section"""
    with gr.Column():
        gr.Markdown("### 📑 Section Details")
        
        title = gr.Textbox(label="Section Title", placeholder="Section heading")
        
        mode = gr.Radio(
            ["Prompt-based", "Static Resource"],
            label="Content Mode",
            value="Prompt-based"
        )
        
        with gr.Column(visible=True) as prompt_mode:
            prompt = gr.TextArea(
                label="Generation Prompt",
                placeholder="Instructions for generating this section",
                lines=4
            )
            refs = gr.CheckboxGroup(
                label="Reference Resources",
                choices=[],  # Populated from available resources
                info="Select resources to include as context"
            )
            
        with gr.Column(visible=False) as static_mode:
            resource_key = gr.Dropdown(
                label="Static Resource",
                choices=[],  # Populated from available resources
                info="Use this resource as the section content"
            )
            
        save_btn = gr.Button("💾 Save Changes", variant="primary")
```

### 4. Interaction Flow

1. **Selection**: User clicks item in left list → Show editor in right column
2. **Editing**: User modifies fields in editor → Enable save button
3. **Saving**: User clicks save → Update model, refresh list
4. **Adding**: User clicks add → Create empty item, select it, show editor
5. **Removing**: User clicks remove → Delete selected item, clear editor

### 5. Benefits of This Approach

1. **Simplicity**: Dramatically fewer callbacks and state variables
2. **Clarity**: Visual layout matches mental model
3. **Efficiency**: Direct manipulation instead of dropdown navigation  
4. **Scalability**: Easy to add new resource/section types
5. **Maintainability**: Each component is self-contained

## Migration Strategy

1. **Move old UI**: `mv ui/ ui_old/`
2. **Create new UI**: Write simplified components directly in `ui/`
3. **Test**: Verify all features work
4. **Cleanup**: `rm -rf ui_old/`

## Next Steps

1. Move existing UI aside
2. Build new components in place
3. Connect to existing executor backend
4. Delete old code

## Success Metrics

- Reduce callback functions from 15+ to <5
- Reduce lines of UI code by 50%+
- Support sections up to 4 levels deep
- Direct selection instead of dropdown navigation