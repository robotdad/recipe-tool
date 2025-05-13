import { createCanvas } from "./core/canvas.js";

// node registrations
import { registerLLMGenerate } from "./nodes/llm_generate.js";
import { registerReadFiles } from "./nodes/read_files.js";
// … import the rest …

// UI shell
import { init as initChat } from "./ui/chat_assistant_panel.js";
import { initToolboxShell } from "./ui/toolbox_shell.js";

// serialization (optional for now)
// import { recipeToDrawflow, drawflowToRecipe } from './modules/serialization.js';

// integrations (optional for now)
// import { loadFlow, saveFlow } from './integration/storage_service.js';
// import { runRecipe }        from './integration/execution_service.js';

// 1. Create the canvas
const editor = createCanvas(document.getElementById("drawflow"));

// 2. Register your node types
registerReadFiles(editor);
registerLLMGenerate(editor);
// … register the rest …

// 3. Initialize the toolbox UI (adds buttons that call editor.addNode)
initToolboxShell(editor, document.getElementById("toolbox"));

// 4. Initialize the chat panel (optional)
initChat(editor, document.getElementById("sidebar"));
