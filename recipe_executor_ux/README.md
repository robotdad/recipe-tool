# Recipe Flow Editor: Comprehensive Project Guide

## 1. Project Overview

The Recipe Flow Editor is a web-based application designed to create, edit, and execute "recipes" for the recipe-tool automation framework. It provides a visual interface for building workflow recipes through a node-based graph editor, similar to tools like Zapier or n8n.

**Purpose**: To enable users to visually compose and execute recipe workflows without manually editing JSON files.

**Key Features**:

- Visual node-based workflow editor
- Recipe loading and saving functionality
- Recipe execution with real-time logs
- Node property editing
- Drag-and-drop workflow composition

## 2. Architecture and Technology Stack

### Backend

- **FastAPI**: Serves both the API endpoints and static files
- **Python**: Integrates with the recipe-tool library for recipe execution
- **SSE (Server-Sent Events)**: For real-time execution logs

### Frontend

- **Vanilla JavaScript**: No framework dependencies
- **Cytoscape.js**: Graph visualization library for the flow editor
- **Cytoscape Extensions**:
  - cytoscape-dagre: For directed graph layout
  - cytoscape-edgehandles: For edge creation
- **No build system**: Static files served directly

### Server Components

- `/api/recipes`: List available recipes
- `/api/recipes/{id}`: Get a specific recipe
- `/api/recipes/save`: Save a recipe
- `/api/recipes/execute`: Execute a recipe
- `/api/execution/{id}/stream`: Stream execution logs

## 3. Current Implementation Status

### Completed Components

- Basic UI layout with three panels (recipe list, flow editor, execution panel)
- Recipe listing and loading
- Node creation and positioning in the flow editor
- Node property editing panel
- Recipe execution with real-time logs
- JSON viewer/editor for recipes
- Drag-and-drop interface for node creation

### Partially Implemented

- Edge creation between nodes (right-click to create connections)
- Recipe saving functionality
- Node styling and appearance
- Node property editing for different step types

### Recent Fixes

- Fixed drag-and-drop from palette to canvas
- Added floating palette for step types
- Corrected style selectors for Cytoscape to avoid errors with missing data

## 4. Known Issues

1. **Style Errors**: Cytoscape may show errors when applying styles to nodes without required data fields (`label`, `color`). Fixed by updating style selectors.

2. **Edge Handling**: Right-click to create edges may not work consistently.

3. **Node Positioning**: Auto-layout may not produce ideal node positions for complex workflows.

4. **Recipe Validation**: No validation against recipe schema before saving.

5. **Error Handling**: Limited error reporting for execution failures.

## 5. Key Files and Codebase Structure

```
recipe_executor_ux/
├── main.py                 # FastAPI application
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   ├── js/
│   │   ├── app.js          # Main application logic
│   │   └── flow-editor.js  # Cytoscape flow editor component
│   └── lib/                # Third-party libraries (optional - using CDN now)
├── templates/              # HTML templates
│   └── index.html          # Main application page
└── requirements.txt        # Python dependencies
```

### Key Component Details

#### `main.py`

Handles API endpoints and serves the frontend. Key endpoints include:

- GET `/api/recipes`: List recipes
- GET `/api/recipes/{id}`: Get recipe JSON
- POST `/api/recipes/save`: Save recipe
- POST `/api/recipes/execute`: Execute a recipe
- GET `/api/execution/{id}/stream`: Stream execution logs

#### `index.html`

The main UI template with three-panel layout:

- Left: Recipe list sidebar
- Center: Flow editor canvas and property panel
- Right: Execution panel with context variables and logs

#### `flow-editor.js`

The core visualization component that:

- Creates and manages the Cytoscape instance
- Handles node creation, selection, and styling
- Manages edge creation
- Exports/imports recipe JSON
- Updates node properties

#### `app.js`

The main application logic that:

- Initializes the flow editor
- Handles API communication
- Manages recipe loading/saving
- Handles palette drag-and-drop
- Controls execution and logging

## 6. Setup and Running Instructions

### Prerequisites

- Python 3.8+
- pip
- recipe-tool installed (`pip install recipe-tool`)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. From the project directory:
   ```bash
   python main.py
   ```
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Open http://localhost:8000 in a browser

## 7. Next Steps and Prioritized Roadmap

### Immediate Tasks (High Priority)

1. **Complete Edge Creation**:

   - Fix right-click to create connections
   - Add visual feedback during edge creation
   - Implement better connection validation

2. **Recipe Validation**:

   - Add schema validation before saving
   - Prevent invalid connections between steps
   - Validate step configurations

3. **Error Handling**:
   - Improve error reporting for execution failures
   - Add input validation for properties

### Medium Priority

1. **UI Enhancements**:

   - Add tooltips for nodes and controls
   - Improve node appearance with icons
   - Add minimap for large workflows
   - Zoom controls and canvas navigation

2. **Recipe Management**:

   - Recipe categories or folders
   - Recipe templates
   - Recipe versioning

3. **Property Editor Improvements**:
   - Step-specific property UI components
   - Property validation
   - Property help text

### Future Enhancements (Lower Priority)

1. **Advanced Features**:

   - Recipe debugging tools
   - Step-by-step execution
   - Conditional branch visualization
   - Loop visualization

2. **Collaboration Features**:

   - Recipe sharing
   - User permissions
   - Comments and annotations

3. **Integration Improvements**:
   - Recipe import/export
   - Integration with external systems

## 8. Implementation Details and Technical Notes

### Cytoscape Setup

Cytoscape.js is initialized with specific styles and extensions in `flow-editor.js`. The configuration includes:

- Node styling for different step types
- Edge styling
- Layout configuration using dagre
- Extensions registration

### Node Type System

Each step type has defined appearance settings in `this.stepTypes` in `flow-editor.js`:

```javascript
this.stepTypes = {
  read_files: { color: "#8dd3c7", icon: "📁" },
  write_files: { color: "#bebada", icon: "💾" },
  // other step types...
};
```

### Property Panel

The property panel dynamically generates fields based on the selected node's type using `displayNodeProperties()` in `flow-editor.js`. Each step type has specific configuration fields defined in `getConfigFieldsForType()`.

### Drag and Drop Implementation

Drag and drop uses the HTML5 Drag and Drop API:

- `dragstart` event on palette items sets data
- `dragover` event on canvas prevents default behavior
- `drop` event creates nodes at drop position

### Recipe Execution

Recipe execution uses Server-Sent Events (SSE) to stream logs:

1. POST to `/api/recipes/execute` starts execution
2. Connect to `/api/execution/{id}/stream` for logs
3. Status updates and logs stream in real-time

## 9. Common Troubleshooting

### Node Styling Issues

If nodes aren't styled correctly, check:

- Cytoscape style selectors
- Node data fields (ensure `label` and `color` are set)
- Style application in `updateNodeAppearance()`

### Drag and Drop Problems

If drag and drop doesn't work:

- Check browser console for errors
- Verify `draggable="true"` is set on palette items
- Ensure data is properly set with `setData()` and retrieved with `getData()`
- Confirm drop target has `preventDefault()` on dragover

### Edge Creation Issues

If edge creation fails:

- Check Cytoscape console errors
- Ensure edgehandles extension is correctly initialized
- Verify node data has required fields

### Recipe Execution Failures

If recipe execution fails:

- Check server logs for Python errors
- Verify the recipe-tool is properly installed
- Check SSE connection in browser Network tab
- Verify JSON format of the recipe

## 10. Resources and References

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Cytoscape.js Documentation](https://js.cytoscape.org/)
- [Cytoscape-dagre Documentation](https://github.com/cytoscape/cytoscape.js-dagre)
- [Cytoscape-edgehandles Documentation](https://github.com/cytoscape/cytoscape.js-edgehandles)

### Key Libraries (CDN Links)

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/dagre/0.8.5/dagre.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/cytoscape-edgehandles@4.0.1/cytoscape-edgehandles.js"></script>
```

### Recipe-Tool Documentation

Refer to the recipe-tool documentation for details on:

- Recipe JSON schema
- Step types and their configurations
- Execution parameters
- Context variable format

## 11. Additional Notes for Handoff

### Current Development Approach

The project follows a **simpicity-first philosophy**:

- Vanilla JS without build tools for easy modification
- Direct DOM manipulation instead of frameworks
- No state management libraries
- API-first design for future extensibility

### Testing

- Manual testing is currently the primary approach
- Test recipes are available in the `recipes/` directory
- Each feature should be tested by:
  1. Creating a new recipe
  2. Adding different node types
  3. Connecting nodes
  4. Setting properties
  5. Saving and executing the recipe

### Debugging Tips

- Use browser dev tools to inspect Cytoscape objects
- The window.flowEditor instance is exposed for console debugging
- FastAPI provides automatic documentation at `/docs`
- Add logging to backend with `logger.debug()`
