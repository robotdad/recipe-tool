# jerosoler/Drawflow

[git-collector-data]

**URL:** https://github.com/jerosoler/Drawflow  
**Date:** 5/13/2025, 9:22:48 AM  
**Files:** 5  

=== File: README.md ===
[![npm](https://img.shields.io/npm/v/drawflow?color=green)](https://www.npmjs.com/package/drawflow)
![npm](https://img.shields.io/npm/dy/drawflow)
![npm bundle size](https://img.shields.io/bundlephobia/minzip/drawflow)
[![GitHub license](https://img.shields.io/github/license/jerosoler/Drawflow)](https://github.com/jerosoler/Drawflow/blob/master/LICENSE)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2Fjerosoler)](https://twitter.com/jerosoler)
# Drawflow

![Demo](https://github.com/jerosoler/Drawflow/raw/master/docs/drawflow.gif)

Simple flow library.

Drawflow allows you to create data flows easily and quickly.

Installing only a javascript library and with four lines of code.

⭐ [LIVE DEMO](https://jerosoler.github.io/Drawflow/)

🎨 [THEME EDIT GENERATOR](https://jerosoler.github.io/drawflow-theme-generator/)

## Table of contents
- [Features](#features)
- [Installation](#installation)
  - [Running](#running)
- [Mouse and  Keys](#mouse-and-keys)
- [Editor](#editor)
  - [Options](#editor-options)
- [Modules](#modules)
- [Nodes](#nodes)
  - [Node example](#node-example)
  - [Register Node](#register-node)
- [Methods](#methods)
  - [Methods example](#methods-example)
- [Events](#events)
  - [Events example](#events-example)
- [Export / Import](#export-/-import)
  - [Export example](#export-example)
- [Example](#example)
- [License](#license)

## Features
- Drag Nodes
- Multiple Inputs / Outputs
- Multiple connections
- Delete Nodes and Connections
- Add/Delete inputs/outputs
- Reroute connections
- Data sync on Nodes
- Zoom in / out
- Clear data module
- Support modules
- Editor mode `edit`, `fixed` or `view`
- Import / Export data
- Events
- Mobile support
- Vanilla javascript (No dependencies)
- NPM
- Vue Support component nodes && Nuxt

## Installation
Download or clone repository and copy the dist folder, CDN option Or npm.  
#### Clone
`git clone https://github.com/jerosoler/Drawflow.git`

#### CDN
```html
# Last
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.css">
<script src="https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.js"></script>
# or version view releases https://github.com/jerosoler/Drawflow/releases
<link rel="stylesheet" href="https://unpkg.com/drawflow@x.x.xx/dist/drawflow.min.css" />
<script src="https://unpkg.com/drawflow@x.x.xx/dist/drawflow.min.js"></script>
```

#### NPM
```javascript
npm i drawflow
```

### Typescript
External package. More info [#119](https://github.com/jerosoler/Drawflow/issues/119)
```javascript
npm install -D @types/drawflow
```

#### Import
```javascript
import Drawflow from 'drawflow'
import styleDrawflow from 'drawflow/dist/drawflow.min.css'
```

#### Require
```javascript
var Drawflow = require('drawflow')
var styleDrawflow = require('drawflow/dist/drawflow.min.css')
```

Create the parent element of **drawflow**.
```html
<div id="drawflow"></div>
```
### Running
Start drawflow.
```javascript
var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.start();
```
Parameter | Type | Description
--- | --- | ---
`id` | Object | Name of module
`render` | Object | It's for `Vue`.
`parent` | Object | It's for `Vue`. The parent Instance

### For vue 2 example.
```javascript
import Vue from 'vue'

// Pass render Vue
this.editor = new Drawflow(id, Vue, this);
```

### For vue 3 example.
```javascript
import { h, getCurrentInstance, render } from 'vue'
const Vue = { version: 3, h, render };

this.editor = new Drawflow(id, Vue);
// Pass render Vue 3 Instance
const internalInstance = getCurrentInstance()
editor.value = new Drawflow(id, Vue, internalInstance.appContext.app._context);
```

### Nuxt
Add to `nuxt.config.js` file
```javascript
build: {
    transpile: ['drawflow'],
    ...
  }
```

## Mouse and  Keys
- `del key` to remove element.
- `Right click` to show remove options (Mobile long press).
- `Left click press` to move editor or node selected.
- `Ctrl + Mouse Wheel` Zoom in/out (Mobile pinch).

## Editor
You can change the editor to **fixed** type to block. Only editor can be moved. You can put it before start.
```javascript
editor.editor_mode = 'edit'; // Default
editor.editor_mode = 'fixed'; // Only scroll
```
You can also adjust the zoom values.
```javascript
editor.zoom_max = 1.6;
editor.zoom_min = 0.5;
editor.zoom_value = 0.1;
```

### Editor options

Parameter | Type | Default | Description
--- | --- | --- | ---
`reroute` | Boolean | false | Active reroute
`reroute_fix_curvature` | Boolean | false | Fix adding points
`curvature` | Number | 0.5 | Curvature
`reroute_curvature_start_end` | Number | 0.5 | Curvature reroute first point and las point
`reroute_curvature` | Number | 0.5 | Curvature reroute
`reroute_width` | Number | 6 | Width of reroute
`line_path` | Number | 5 | Width of line
`force_first_input` | Boolean | false | Force the first input to drop the connection on top of the node
`editor_mode` | Text | `edit` | `edit` for edit, `fixed` for nodes fixed but their input fields available, `view` for view only
`zoom` | Number | 1 | Default zoom
`zoom_max` | Number | 1.6 | Default zoom max
`zoom_min` | Number | 0.5 | Default zoom min
`zoom_value` | Number | 0.1 | Default zoom value update
`zoom_last_value` | Number | 1 | Default zoom last value
`draggable_inputs` | Boolean | true | Drag nodes on click inputs
`useuuid` | Boolean | false | Use UUID as node ID instead of integer index. Only affect newly created nodes, do not affect imported nodes

### Reroute
Active reroute connections. Use before `start` or `import`.
```javascript
editor.reroute = true;
```
Create point with double click on line connection. Double click on point for remove.

## Modules
Separate your flows in different editors.
```javascript
editor.addModule('nameNewModule');
editor.changeModule('nameNewModule');
editor.removeModule('nameModule');
// Default Module is Home
editor.changeModule('Home');
```
`RemovedModule` if it is in the same module redirects to the `Home` module


## Nodes
Adding a node is simple.
```javascript
editor.addNode(name, inputs, outputs, posx, posy, class, data, html);
```
Parameter | Type | Description
--- | --- | ---
`name` | text | Name of module
`inputs` | number | Number of de inputs
`outputs` | number | Number of de outputs
`pos_x` | number | Position on start node left
`pos_y` | number | Position on start node top
`class` | text | Added classname to de node. Multiple classnames separated by space
`data` | json | Data passed to node
`html` | text | HTML drawn on node or `name` of register node.
`typenode` | boolean & text | Default `false`, `true` for Object HTML, `vue` for vue

You can use the attribute `df-*` in **inputs, textarea or select** to synchronize with the node data and **contenteditable**.

Atrributs multiples parents support `df-*-*...`

### Node example
```javascript
var html = `
<div><input type="text" df-name></div>
`;
var data = { "name": '' };

editor.addNode('github', 0, 1, 150, 300, 'github', data, html);
```
### Register Node

it's possible register nodes for reuse.
```javascript
var html = document.createElement("div");
html.innerHTML =  "Hello Drawflow!!";
editor.registerNode('test', html);
// Use
editor.addNode('github', 0, 1, 150, 300, 'github', data, 'test', true);

// For vue
import component from '~/components/testcomponent.vue'
editor.registerNode('name', component, props, options);
// Use for vue
editor.addNode('github', 0, 1, 150, 300, 'github', data, 'name', 'vue');
```

Parameter | Type | Description
--- | --- | ---
`name` | text | Name of module registered.
`html` | text | HTML to drawn or `vue` component.
`props` | json | Only for `vue`. Props of component. `Not Required`
`options` | json | Only for `vue`. Options of component. `Not Required`



## Methods
Other available functions.

Mehtod | Description
--- | ---
`zoom_in()` | Increment zoom +0.1
`zoom_out()` | Decrement zoom -0.1
`getNodeFromId(id)` | Get Info of node. Ex: id: `5`
`getNodesFromName(name)` | Return Array of nodes id. Ex: name: `telegram`
`removeNodeId(id)` | Remove node. Ex id: `node-x`
`updateNodeDataFromId` | Update data element. Ex: `5, { name: 'Drawflow' }`
`addNodeInput(id)` | Add input to node. Ex id: `5`
`addNodeOutput(id)` | Add output to node. Ex id: `5`
`removeNodeInput(id, input_class)` | Remove input to node. Ex id: `5`, `input_2`
`removeNodeOutput(id, output_class)` | Remove output to node. Ex id: `5`, `output_2`
`addConnection(id_output, id_input, output_class, input_class)` | Add connection. Ex: `15,16,'output_1','input_1'`
`removeSingleConnection(id_output, id_input, output_class, input_class)` | Remove connection. Ex: `15,16,'output_1','input_1'`
`updateConnectionNodes(id)` | Update connections position from Node Ex id: `node-x`
`removeConnectionNodeId(id)` | Remove node connections. Ex id: `node-x`
`getModuleFromNodeId(id)` | Get name of module where is the id. Ex id: `5`
`clearModuleSelected()` | Clear data of module selected
`clear()` | Clear all data of all modules and modules remove.

### Methods example

```javascript
editor.removeNodeId('node-4');
```

## Events
You can detect events that are happening.

List of available events:

Event | Return | Description
--- | --- | ---
  `nodeCreated` | id | `id` of Node
  `nodeRemoved` | id | `id` of Node
  `nodeDataChanged` | id | `id` of Node df-* attributes changed.
  `nodeSelected` | id | `id` of Node
  `nodeUnselected` | true | Unselect node
  `nodeMoved` | id | `id` of Node
  `connectionStart` | { output_id, output_class } | `id` of nodes and output selected
  `connectionCancel` | true | Connection Cancel
  `connectionCreated` | { output_id, input_id, output_class, input_class } | `id`'s of nodes and output/input selected
  `connectionRemoved` | { output_id, input_id, output_class, input_class } | `id`'s of nodes and output/input selected
  `connectionSelected` | { output_id, input_id, output_class, input_class } | `id`'s of nodes and output/input selected
  `connectionUnselected` | true | Unselect connection
  `addReroute` | id | `id` of Node output
  `removeReroute` | id | `id` of Node output
  `rerouteMoved` | id | `id` of Node output
  `moduleCreated` | name | `name` of Module
  `moduleChanged` | name | `name` of Module
  `moduleRemoved` | name | `name` of Module
  `click` | event | Click event
  `clickEnd` | event | Once the click changes have been made
  `contextmenu` | event | Click second button mouse event
  `mouseMove` | { x, y } | Position
  `mouseUp` | event | MouseUp Event
  `keydown` | event | Keydown event
  `zoom` | zoom_level | Level of zoom
  `translate` | { x, y } | Position translate editor
  `import` | `import` | Finish import
  `export` | data | Data export

### Events example
```javascript
editor.on('nodeCreated', function(id) {
  console.log("Node created " + id);
})
```

## Export / Import
You can export and import your data.
```javascript
var exportdata = editor.export();
editor.import(exportdata);
```
### Export example
Example of exported data:
```json
{
    "drawflow": {
        "Home": {
            "data": {}
        },
        "Other": {
            "data": {
                "16": {
                    "id": 16,
                    "name": "facebook",
                    "data": {},
                    "class": "facebook",
                    "html": "\n        
\n          
 Facebook Message
\n        
\n        ",
                    "inputs": {},
                    "outputs": {
                        "output_1": {
                            "connections": [
                                {
                                    "node": "17",
                                    "output": "input_1"
                                }
                            ]
                        }
                    },
                    "pos_x": 226,
                    "pos_y": 138
                },
                "17": {
                    "id": 17,
                    "name": "log",
                    "data": {},
                    "class": "log",
                    "html": "\n            
\n              
 Save log file
\n            
\n            ",
                    "inputs": {
                        "input_1": {
                            "connections": [
                                {
                                    "node": "16",
                                    "input": "output_1"
                                }
                            ]
                        }
                    },
                    "outputs": {},
                    "pos_x": 690,
                    "pos_y": 129
                }
            }
        }
    }
}

```

## Example
View the complete example in folder [docs](https://github.com/jerosoler/Drawflow/tree/master/docs).  
There is also an [example](docs/drawflow-element.html) how to use Drawflow in a custom element. (based on [LitElement](https://lit-element.polymer-project.org)).  

## License
MIT License


=== File: docs/beautiful.css ===
:root {
  --border-color: #cacaca;
  --background-color: #ffffff;

  --background-box-title: #f7f7f7;
}

html, body {
  margin: 0px;
  padding: 0px;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'Roboto', sans-serif;
}

header {
  height: 66px;
  border-bottom: 1px solid var(--border-color);
  padding-left: 20px;
}
header h2 {
  margin: 0px;
  line-height: 66px;
}
header a {
  color: black;
}
.them-edit-link {
  position: absolute;
  top: 10px;
  right: 100px;
  color: black;
  font-size: 40px;
}
.them-edit-link a {
  text-decoration: none;
}

.github-link{
  position: absolute;
  top: 10px;
  right: 20px;
  color: black;
}

.wrapper {
  width: 100%;
  height: calc(100vh - 67px);
  display: flex;
}

.col {
  overflow: auto;
  width: 300px;
  height: 100%;
  border-right: 1px solid var(--border-color);
}

.drag-drawflow {
  line-height: 50px;
  border-bottom: 1px solid var(--border-color);
  padding-left: 20px;
  cursor: move;
  user-select: none;
}
.menu {
  position: absolute;
  height: 40px;
  display: block;
  background: white;
  width: 100%;
}
.menu ul {
  padding: 0px;
  margin: 0px;
  line-height: 40px;
}

.menu ul li {
  display: inline-block;
margin-left: 10px;
border-right: 1px solid var(--border-color);
padding-right: 10px;
line-height: 40px;
cursor: pointer;
}

.menu ul li.selected {
  font-weight: bold;
}

.btn-export {
  float: right;
  position: absolute;
  top: 10px;
  right: 10px;
  color: white;
  font-weight: bold;
  border: 1px solid #0e5ba3;
  background: #4ea9ff;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  z-index: 5;
}

.btn-clear {
  float: right;
  position: absolute;
  top: 10px;
  right: 85px;
  color: white;
  font-weight: bold;
  border: 1px solid #96015b;
  background: #e3195a;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  z-index: 5;
}
.swal-wide{
    width:80% !important;
}

.btn-lock {
  float: right;
  position: absolute;
  bottom: 10px;
  right: 140px;
  display: flex;
  font-size: 24px;
  color: white;
  padding: 5px 10px;
  background: #555555;
  border-radius: 4px;
  border-right: 1px solid var(--border-color);
  z-index: 5;
  cursor: pointer;
}

.bar-zoom {
  float: right;
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  font-size: 24px;
  color: white;
  padding: 5px 10px;
  background: #555555;
  border-radius: 4px;
  border-right: 1px solid var(--border-color);
  z-index: 5;
}
.bar-zoom svg {
  cursor: pointer;
  padding-left: 10px;
}
.bar-zoom svg:nth-child(1) {
  padding-left: 0px;
}

#drawflow {
  position: relative;
  width: calc(100vw - 301px);
  height: calc(100% - 50px);
  top: 40px;
  background: var(--background-color);
  background-size: 25px 25px;
  background-image:
   linear-gradient(to right, #f1f1f1 1px, transparent 1px),
   linear-gradient(to bottom, #f1f1f1 1px, transparent 1px);
}

@media only screen and (max-width: 768px) {
  .col {
    width: 50px;
  }
  .col .drag-drawflow span {
    display:none;
  }
  #drawflow {
    width: calc(100vw - 51px);
  }
}



/* Editing Drawflow */

.drawflow .drawflow-node {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  -webkit-box-shadow: 0 2px 15px 2px var(--border-color);
  box-shadow: 0 2px 15px 2px var(--border-color);
  padding: 0px;
  width: 200px;
}

.drawflow .drawflow-node.selected  {
  background: white;
  border: 1px solid #4ea9ff;
  -webkit-box-shadow: 0 2px 20px 2px #4ea9ff;
  box-shadow: 0 2px 20px 2px #4ea9ff;
}

.drawflow .drawflow-node.selected .title-box {
  color: #22598c;
  /*border-bottom: 1px solid #4ea9ff;*/
}

.drawflow .connection .main-path {
  stroke: #4ea9ff;
  stroke-width: 3px;
}

.drawflow .drawflow-node .input, .drawflow .drawflow-node .output {
  height: 15px;
  width: 15px;
  border: 2px solid var(--border-color);
}

.drawflow .drawflow-node .input:hover, .drawflow .drawflow-node .output:hover {
  background: #4ea9ff;
}

.drawflow .drawflow-node .output {
  right: 10px;
}

.drawflow .drawflow-node .input {
  left: -10px;
  background: white;
}

.drawflow > .drawflow-delete {
  border: 2px solid #43b993;
  background: white;
  color: #43b993;
  -webkit-box-shadow: 0 2px 20px 2px #43b993;
  box-shadow: 0 2px 20px 2px #43b993;
}

.drawflow-delete {
  border: 2px solid #4ea9ff;
  background: white;
  color: #4ea9ff;
  -webkit-box-shadow: 0 2px 20px 2px #4ea9ff;
  box-shadow: 0 2px 20px 2px #4ea9ff;
}

.drawflow-node .title-box {
  height: 50px;
  line-height: 50px;
  background: var(--background-box-title);
  border-bottom: 1px solid #e9e9e9;
  border-radius: 4px 4px 0px 0px;
  padding-left: 10px;
}
.drawflow .title-box svg {
  position: initial;
}
.drawflow-node .box {
  padding: 10px 20px 20px 20px;
  font-size: 14px;
  color: #555555;

}
.drawflow-node .box p {
  margin-top: 5px;
  margin-bottom: 5px;
}

.drawflow-node.welcome {
  width: 250px;
}

.drawflow-node.slack .title-box {
  border-radius: 4px;
}

.drawflow-node input, .drawflow-node select, .drawflow-node textarea {
  border-radius: 4px;
  border: 1px solid var(--border-color);
  height: 30px;
  line-height: 30px;
  font-size: 16px;
  width: 158px;
  color: #555555;
}

.drawflow-node textarea {
  height: 100px;
}


.drawflow-node.personalized {
  background: red;
  height: 200px;
  text-align: center;
  color: white;
}
.drawflow-node.personalized .input {
  background: yellow;
}
.drawflow-node.personalized .output {
  background: green;
}

.drawflow-node.personalized.selected {
  background: blue;
}

.drawflow .connection .point {
  stroke: var(--border-color);
  stroke-width: 2;
  fill: white;
  
}

.drawflow .connection .point.selected, .drawflow .connection .point:hover {
  fill: #4ea9ff;
}


/* Modal */
.modal {
  display: none;
  position: fixed;
  z-index: 7;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  overflow: auto;
  background-color: rgb(0,0,0);
  background-color: rgba(0,0,0,0.7);

}

.modal-content {
  position: relative;
  background-color: #fefefe;
  margin: 15% auto; /* 15% from the top and centered */
  padding: 20px;
  border: 1px solid #888;
  width: 400px; /* Could be more or less, depending on screen size */
}

/* The Close Button */
.modal .close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor:pointer;
}

@media only screen and (max-width: 768px) {
  .modal-content {
    width: 80%;
  }
}


=== File: docs/drawflow-element.html ===
<!doctype html>
<html>
  <head>
    <script type="module" src="drawflow-element.js"></script>
    <title>Drawflow Element</title>
  </head>
  <body>
    <drawflow-element></drawflow-element>
  </body>
</html>


=== File: docs/drawflow-element.js ===
import { css, LitElement, html } from 'lit-element';
import { style } from '../dist/drawflow.style';
import '../dist/drawflow.min';

class DrawflowElement extends LitElement {
  static get styles() {
    return [
      style,
      css`
        #drawflow {
          display: block;
          position: relative;
          width: 100%;
          height: 800px;
        }
      `
    ];
  }

  render() {
    return html`
      <div id="drawflow"></div>
    `;
  }

  firstUpdated() {
    const container = this.shadowRoot?.getElementById('drawflow');
    const editor = new Drawflow(container);

    editor.reroute = true;
    editor.reroute_fix_curvature = true;

    editor.start();

    const data = {
      name: ''
    };

    editor.addNode('foo', 1, 1, 100, 200, 'foo', data, 'Foo');
    editor.addNode('bar', 1, 1, 400, 100, 'bar', data, 'Bar A');
    editor.addNode('bar', 1, 1, 400, 300, 'bar', data, 'Bar B');

    editor.addConnection(1, 2, "output_1", "input_1");
    editor.addConnection(1, 3, "output_1", "input_1");
  }
}

customElements.define("drawflow-element", DrawflowElement);


=== File: docs/index.html ===
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Drawflow | Simple Flow program libray</title>
  <meta name="description" content="Simple library for flow programming. Drawflow allows you to create data flows easily and quickly.">
</head>
<body>
  <script src="https://cdn.jsdelivr.net/gh/jerosoler/Drawflow/dist/drawflow.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/js/all.min.js" integrity="sha256-KzZiKy0DWYsnwMF+X1DvQngQ2/FxF7MF3Ff72XcpuPs=" crossorigin="anonymous"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jerosoler/Drawflow@0.0.48/dist/drawflow.min.css">
  <link rel="stylesheet" type="text/css" href="beautiful.css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/css/all.min.css" integrity="sha256-h20CPZ0QyXlBuAw7A+KluUYx/3pK+c7lYEpqLTlxjYQ=" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/sweetalert2@9"></script>
  <script src="https://unpkg.com/micromodal/dist/micromodal.min.js"></script>


  <header>
    <h2>Drawflow</h2>
    <div class="github-link"><a href="https://github.com/jerosoler/Drawflow" target="_blank"><i class="fab fa-github fa-3x"></i></a></div>
    <div class="them-edit-link"><a href="https://jerosoler.github.io/drawflow-theme-generator/" target="_blank">🎨</a></div>
  </header>
  <div class="wrapper">
    <div class="col">
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="facebook">
        <i class="fab fa-facebook"></i><span> Facebook</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="slack">
        <i class="fab fa-slack"></i><span> Slack receive message</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="github">
        <i class="fab fa-github"></i><span> Github Star</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="telegram">
        <i class="fab fa-telegram"></i><span> Telegram send message</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="aws">
        <i class="fab fa-aws"></i><span> AWS</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="log">
        <i class="fas fa-file-signature"></i><span> File Log</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="google">
        <i class="fab fa-google-drive"></i><span> Google Drive save</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="email">
        <i class="fas fa-at"></i><span> Email send</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="template">
        <i class="fas fa-code"></i><span> Template</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="multiple">
        <i class="fas fa-code-branch"></i><span> Multiple inputs/outputs</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="personalized">
        <i class="fas fa-fill"></i><span> Personalized</span>
      </div>
      <div class="drag-drawflow" draggable="true" ondragstart="drag(event)" data-node="dbclick">
        <i class="fas fa-mouse"></i><span> DBClick!</span>
      </div>


    </div>
    <div class="col-right">
      <div class="menu">
        <ul>
          <li onclick="editor.changeModule('Home'); changeModule(event);" class="selected">Home</li>
          <li onclick="editor.changeModule('Other'); changeModule(event);">Other Module</li>
        </ul>
      </div>
      <div id="drawflow" ondrop="drop(event)" ondragover="allowDrop(event)">

        <div class="btn-export" onclick="Swal.fire({ title: 'Export',
        html: '<pre><code>'+JSON.stringify(editor.export(), null,4)+'</code></pre>'
        })">Export</div>
        <div class="btn-clear" onclick="editor.clearModuleSelected()">Clear</div>
        <div class="btn-lock">
          <i id="lock" class="fas fa-lock" onclick="editor.editor_mode='fixed'; changeMode('lock');"></i>
          <i id="unlock" class="fas fa-lock-open" onclick="editor.editor_mode='edit'; changeMode('unlock');" style="display:none;"></i>
        </div>
        <div class="bar-zoom">
          <i class="fas fa-search-minus" onclick="editor.zoom_out()"></i>
          <i class="fas fa-search" onclick="editor.zoom_reset()"></i>
          <i class="fas fa-search-plus" onclick="editor.zoom_in()"></i>
        </div>
      </div>
    </div>
  </div>

  <script>
    var id = document.getElementById("drawflow");
    const editor = new Drawflow(id);
    editor.reroute = true;
    const dataToImport = {"drawflow":{"Home":{"data":{"1":{"id":1,"name":"welcome","data":{},"class":"welcome","html":"\n    <div>\n      <div class=\"title-box\">👏 Welcome!!</div>\n      <div class=\"box\">\n        <p>Simple flow library <b>demo</b>\n        <a href=\"https://github.com/jerosoler/Drawflow\" target=\"_blank\">Drawflow</a> by <b>Jero Soler</b></p><br>\n\n        <p>Multiple input / outputs<br>\n           Data sync nodes<br>\n           Import / export<br>\n           Modules support<br>\n           Simple use<br>\n           Type: Fixed or Edit<br>\n           Events: view console<br>\n           Pure Javascript<br>\n        </p>\n        <br>\n        <p><b><u>Shortkeys:</u></b></p>\n        <p>🎹 <b>Delete</b> for remove selected<br>\n        💠 Mouse Left Click == Move<br>\n        ❌ Mouse Right == Delete Option<br>\n        🔍 Ctrl + Wheel == Zoom<br>\n        📱 Mobile support<br>\n        ...</p>\n      </div>\n    </div>\n    ","typenode": false, "inputs":{},"outputs":{},"pos_x":50,"pos_y":50},"2":{"id":2,"name":"slack","data":{},"class":"slack","html":"\n          <div>\n            <div class=\"title-box\"><i class=\"fab fa-slack\"></i> Slack chat message</div>\n          </div>\n          ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"7","input":"output_1"}]}},"outputs":{},"pos_x":1028,"pos_y":87},"3":{"id":3,"name":"telegram","data":{"channel":"channel_2"},"class":"telegram","html":"\n          <div>\n            <div class=\"title-box\"><i class=\"fab fa-telegram-plane\"></i> Telegram bot</div>\n            <div class=\"box\">\n              <p>Send to telegram</p>\n              <p>select channel</p>\n              <select df-channel>\n                <option value=\"channel_1\">Channel 1</option>\n                <option value=\"channel_2\">Channel 2</option>\n                <option value=\"channel_3\">Channel 3</option>\n                <option value=\"channel_4\">Channel 4</option>\n              </select>\n            </div>\n          </div>\n          ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"7","input":"output_1"}]}},"outputs":{},"pos_x":1032,"pos_y":184},"4":{"id":4,"name":"email","data":{},"class":"email","html":"\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-at\"></i> Send Email </div>\n            </div>\n            ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"5","input":"output_1"}]}},"outputs":{},"pos_x":1033,"pos_y":439},"5":{"id":5,"name":"template","data":{"template":"Write your template"},"class":"template","html":"\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-code\"></i> Template</div>\n              <div class=\"box\">\n                Ger Vars\n                <textarea df-template></textarea>\n                Output template with vars\n              </div>\n            </div>\n            ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"6","input":"output_1"}]}},"outputs":{"output_1":{"connections":[{"node":"4","output":"input_1"},{"node":"11","output":"input_1"}]}},"pos_x":607,"pos_y":304},"6":{"id":6,"name":"github","data":{"name":"https://github.com/jerosoler/Drawflow"},"class":"github","html":"\n          <div>\n            <div class=\"title-box\"><i class=\"fab fa-github \"></i> Github Stars</div>\n            <div class=\"box\">\n              <p>Enter repository url</p>\n            <input type=\"text\" df-name>\n            </div>\n          </div>\n          ","typenode": false, "inputs":{},"outputs":{"output_1":{"connections":[{"node":"5","output":"input_1"}]}},"pos_x":341,"pos_y":191},"7":{"id":7,"name":"facebook","data":{},"class":"facebook","html":"\n        <div>\n          <div class=\"title-box\"><i class=\"fab fa-facebook\"></i> Facebook Message</div>\n        </div>\n        ","typenode": false, "inputs":{},"outputs":{"output_1":{"connections":[{"node":"2","output":"input_1"},{"node":"3","output":"input_1"},{"node":"11","output":"input_1"}]}},"pos_x":347,"pos_y":87},"11":{"id":11,"name":"log","data":{},"class":"log","html":"\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-file-signature\"></i> Save log file </div>\n            </div>\n            ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"5","input":"output_1"},{"node":"7","input":"output_1"}]}},"outputs":{},"pos_x":1031,"pos_y":363}}},"Other":{"data":{"8":{"id":8,"name":"personalized","data":{},"class":"personalized","html":"\n            <div>\n              Personalized\n            </div>\n            ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"12","input":"output_1"},{"node":"12","input":"output_2"},{"node":"12","input":"output_3"},{"node":"12","input":"output_4"}]}},"outputs":{"output_1":{"connections":[{"node":"9","output":"input_1"}]}},"pos_x":764,"pos_y":227},"9":{"id":9,"name":"dbclick","data":{"name":"Hello World!!"},"class":"dbclick","html":"\n            <div>\n            <div class=\"title-box\"><i class=\"fas fa-mouse\"></i> Db Click</div>\n              <div class=\"box dbclickbox\" ondblclick=\"showpopup(event)\">\n                Db Click here\n                <div class=\"modal\" style=\"display:none\">\n                  <div class=\"modal-content\">\n                    <span class=\"close\" onclick=\"closemodal(event)\">&times;</span>\n                    Change your variable {name} !\n                    <input type=\"text\" df-name>\n                  </div>\n\n                </div>\n              </div>\n            </div>\n            ","typenode": false, "inputs":{"input_1":{"connections":[{"node":"8","input":"output_1"}]}},"outputs":{"output_1":{"connections":[{"node":"12","output":"input_2"}]}},"pos_x":209,"pos_y":38},"12":{"id":12,"name":"multiple","data":{},"class":"multiple","html":"\n            <div>\n              <div class=\"box\">\n                Multiple!\n              </div>\n            </div>\n            ","typenode": false, "inputs":{"input_1":{"connections":[]},"input_2":{"connections":[{"node":"9","input":"output_1"}]},"input_3":{"connections":[]}},"outputs":{"output_1":{"connections":[{"node":"8","output":"input_1"}]},"output_2":{"connections":[{"node":"8","output":"input_1"}]},"output_3":{"connections":[{"node":"8","output":"input_1"}]},"output_4":{"connections":[{"node":"8","output":"input_1"}]}},"pos_x":179,"pos_y":272}}}}}
    editor.start();
    editor.import(dataToImport);


  /*
    var welcome = `
    <div>
      <div class="title-box">👏 Welcome!!</div>
      <div class="box">
        <p>Simple flow library <b>demo</b>
        <a href="https://github.com/jerosoler/Drawflow" target="_blank">Drawflow</a> by <b>Jero Soler</b></p><br>

        <p>Multiple input / outputs<br>
           Data sync nodes<br>
           Import / export<br>
           Modules support<br>
           Simple use<br>
           Type: Fixed or Edit<br>
           Events: view console<br>
           Pure Javascript<br>
        </p>
        <br>
        <p><b><u>Shortkeys:</u></b></p>
        <p>🎹 <b>Delete</b> for remove selected<br>
        💠 Mouse Left Click == Move<br>
        ❌ Mouse Right == Delete Option<br>
        🔍 Ctrl + Wheel == Zoom<br>
        📱 Mobile support<br>
        ...</p>
      </div>
    </div>
    `;
*/


    //editor.addNode(name, inputs, outputs, posx, posy, class, data, html);
    /*editor.addNode('welcome', 0, 0, 50, 50, 'welcome', {}, welcome );
    editor.addModule('Other');
    */

    // Events!
    editor.on('nodeCreated', function(id) {
      console.log("Node created " + id);
    })

    editor.on('nodeRemoved', function(id) {
      console.log("Node removed " + id);
    })

    editor.on('nodeSelected', function(id) {
      console.log("Node selected " + id);
    })

    editor.on('moduleCreated', function(name) {
      console.log("Module Created " + name);
    })

    editor.on('moduleChanged', function(name) {
      console.log("Module Changed " + name);
    })

    editor.on('connectionCreated', function(connection) {
      console.log('Connection created');
      console.log(connection);
    })

    editor.on('connectionRemoved', function(connection) {
      console.log('Connection removed');
      console.log(connection);
    })

    editor.on('mouseMove', function(position) {
      console.log('Position mouse x:' + position.x + ' y:'+ position.y);
    })

    editor.on('nodeMoved', function(id) {
      console.log("Node moved " + id);
    })

    editor.on('zoom', function(zoom) {
      console.log('Zoom level ' + zoom);
    })

    editor.on('translate', function(position) {
      console.log('Translate x:' + position.x + ' y:'+ position.y);
    })

    editor.on('addReroute', function(id) {
      console.log("Reroute added " + id);
    })

    editor.on('removeReroute', function(id) {
      console.log("Reroute removed " + id);
    })

    /* DRAG EVENT */

    /* Mouse and Touch Actions */

    var elements = document.getElementsByClassName('drag-drawflow');
    for (var i = 0; i < elements.length; i++) {
      elements[i].addEventListener('touchend', drop, false);
      elements[i].addEventListener('touchmove', positionMobile, false);
      elements[i].addEventListener('touchstart', drag, false );
    }

    var mobile_item_selec = '';
    var mobile_last_move = null;
   function positionMobile(ev) {
     mobile_last_move = ev;
   }

   function allowDrop(ev) {
      ev.preventDefault();
    }

    function drag(ev) {
      if (ev.type === "touchstart") {
        mobile_item_selec = ev.target.closest(".drag-drawflow").getAttribute('data-node');
      } else {
      ev.dataTransfer.setData("node", ev.target.getAttribute('data-node'));
      }
    }

    function drop(ev) {
      if (ev.type === "touchend") {
        var parentdrawflow = document.elementFromPoint( mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY).closest("#drawflow");
        if(parentdrawflow != null) {
          addNodeToDrawFlow(mobile_item_selec, mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY);
        }
        mobile_item_selec = '';
      } else {
        ev.preventDefault();
        var data = ev.dataTransfer.getData("node");
        addNodeToDrawFlow(data, ev.clientX, ev.clientY);
      }

    }

    function addNodeToDrawFlow(name, pos_x, pos_y) {
      if(editor.editor_mode === 'fixed') {
        return false;
      }
      pos_x = pos_x * ( editor.precanvas.clientWidth / (editor.precanvas.clientWidth * editor.zoom)) - (editor.precanvas.getBoundingClientRect().x * ( editor.precanvas.clientWidth / (editor.precanvas.clientWidth * editor.zoom)));
      pos_y = pos_y * ( editor.precanvas.clientHeight / (editor.precanvas.clientHeight * editor.zoom)) - (editor.precanvas.getBoundingClientRect().y * ( editor.precanvas.clientHeight / (editor.precanvas.clientHeight * editor.zoom)));


      switch (name) {
        case 'facebook':
        var facebook = `
        <div>
          <div class="title-box"><i class="fab fa-facebook"></i> Facebook Message</div>
        </div>
        `;
          editor.addNode('facebook', 0,  1, pos_x, pos_y, 'facebook', {}, facebook );
          break;
        case 'slack':
          var slackchat = `
          <div>
            <div class="title-box"><i class="fab fa-slack"></i> Slack chat message</div>
          </div>
          `
          editor.addNode('slack', 1, 0, pos_x, pos_y, 'slack', {}, slackchat );
          break;
        case 'github':
          var githubtemplate = `
          <div>
            <div class="title-box"><i class="fab fa-github "></i> Github Stars</div>
            <div class="box">
              <p>Enter repository url</p>
            <input type="text" df-name>
            </div>
          </div>
          `;
          editor.addNode('github', 0, 1, pos_x, pos_y, 'github', { "name": ''}, githubtemplate );
          break;
        case 'telegram':
          var telegrambot = `
          <div>
            <div class="title-box"><i class="fab fa-telegram-plane"></i> Telegram bot</div>
            <div class="box">
              <p>Send to telegram</p>
              <p>select channel</p>
              <select df-channel>
                <option value="channel_1">Channel 1</option>
                <option value="channel_2">Channel 2</option>
                <option value="channel_3">Channel 3</option>
                <option value="channel_4">Channel 4</option>
              </select>
            </div>
          </div>
          `;
          editor.addNode('telegram', 1, 0, pos_x, pos_y, 'telegram', { "channel": 'channel_3'}, telegrambot );
          break;
        case 'aws':
          var aws = `
          <div>
            <div class="title-box"><i class="fab fa-aws"></i> Aws Save </div>
            <div class="box">
              <p>Save in aws</p>
              <input type="text" df-db-dbname placeholder="DB name"><br><br>
              <input type="text" df-db-key placeholder="DB key">
              <p>Output Log</p>
            </div>
          </div>
          `;
          editor.addNode('aws', 1, 1, pos_x, pos_y, 'aws', { "db": { "dbname": '', "key": '' }}, aws );
          break;
        case 'log':
            var log = `
            <div>
              <div class="title-box"><i class="fas fa-file-signature"></i> Save log file </div>
            </div>
            `;
            editor.addNode('log', 1, 0, pos_x, pos_y, 'log', {}, log );
            break;
          case 'google':
            var google = `
            <div>
              <div class="title-box"><i class="fab fa-google-drive"></i> Google Drive save </div>
            </div>
            `;
            editor.addNode('google', 1, 0, pos_x, pos_y, 'google', {}, google );
            break;
          case 'email':
            var email = `
            <div>
              <div class="title-box"><i class="fas fa-at"></i> Send Email </div>
            </div>
            `;
            editor.addNode('email', 1, 0, pos_x, pos_y, 'email', {}, email );
            break;

          case 'template':
            var template = `
            <div>
              <div class="title-box"><i class="fas fa-code"></i> Template</div>
              <div class="box">
                Ger Vars
                <textarea df-template></textarea>
                Output template with vars
              </div>
            </div>
            `;
            editor.addNode('template', 1, 1, pos_x, pos_y, 'template', { "template": 'Write your template'}, template );
            break;
          case 'multiple':
            var multiple = `
            <div>
              <div class="box">
                Multiple!
              </div>
            </div>
            `;
            editor.addNode('multiple', 3, 4, pos_x, pos_y, 'multiple', {}, multiple );
            break;
          case 'personalized':
            var personalized = `
            <div>
              Personalized
            </div>
            `;
            editor.addNode('personalized', 1, 1, pos_x, pos_y, 'personalized', {}, personalized );
            break;
          case 'dbclick':
            var dbclick = `
            <div>
            <div class="title-box"><i class="fas fa-mouse"></i> Db Click</div>
              <div class="box dbclickbox" ondblclick="showpopup(event)">
                Db Click here
                <div class="modal" style="display:none">
                  <div class="modal-content">
                    <span class="close" onclick="closemodal(event)">&times;</span>
                    Change your variable {name} !
                    <input type="text" df-name>
                  </div>

                </div>
              </div>
            </div>
            `;
            editor.addNode('dbclick', 1, 1, pos_x, pos_y, 'dbclick', { name: ''}, dbclick );
            break;

        default:
      }
    }

  var transform = '';
  function showpopup(e) {
    e.target.closest(".drawflow-node").style.zIndex = "9999";
    e.target.children[0].style.display = "block";
    //document.getElementById("modalfix").style.display = "block";

    //e.target.children[0].style.transform = 'translate('+translate.x+'px, '+translate.y+'px)';
    transform = editor.precanvas.style.transform;
    editor.precanvas.style.transform = '';
    editor.precanvas.style.left = editor.canvas_x +'px';
    editor.precanvas.style.top = editor.canvas_y +'px';
    console.log(transform);

    //e.target.children[0].style.top  =  -editor.canvas_y - editor.container.offsetTop +'px';
    //e.target.children[0].style.left  =  -editor.canvas_x  - editor.container.offsetLeft +'px';
    editor.editor_mode = "fixed";

  }

   function closemodal(e) {
     e.target.closest(".drawflow-node").style.zIndex = "2";
     e.target.parentElement.parentElement.style.display  ="none";
     //document.getElementById("modalfix").style.display = "none";
     editor.precanvas.style.transform = transform;
       editor.precanvas.style.left = '0px';
       editor.precanvas.style.top = '0px';
      editor.editor_mode = "edit";
   }

    function changeModule(event) {
      var all = document.querySelectorAll(".menu ul li");
        for (var i = 0; i < all.length; i++) {
          all[i].classList.remove('selected');
        }
      event.target.classList.add('selected');
    }

    function changeMode(option) {

    //console.log(lock.id);
      if(option == 'lock') {
        lock.style.display = 'none';
        unlock.style.display = 'block';
      } else {
        lock.style.display = 'block';
        unlock.style.display = 'none';
      }

    }

  </script>
</body>
</html>

