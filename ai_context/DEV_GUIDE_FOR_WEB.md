# Dev Guide for Web (Vanilla JS)

When contributing to the web codebase (HTML/CSS/JS), follow these guidelines to keep things simple, clear, and consistent—even when the project spans multiple files or directories.

- **Project Structure**
  Keep components organized. Use subdirectories when helpful, but keep nesting shallow. Typical structure:

  ```
  /component-name/
    index.html
    style.css
    script.js
  ```

- **JavaScript**

  - Use **vanilla JS only**—no frameworks unless explicitly called for.
  - Use `const` and `let`. Avoid global variables.
  - Scope logic to functions or modules; avoid polluting the global namespace.
  - Wrap initialization in `DOMContentLoaded` or a `setup()` function.
  - Prefer long, descriptive names over abbreviations (e.g. `updateUserList`, not `updUL`).
  - Check for the existence of optional DOM elements before using them.
  - Use template literals for string building (\`\`\`), not concatenation.

- **HTML**

  - Use semantic tags (`<section>`, `<article>`, etc.) where appropriate.
  - Keep markup readable—indent consistently.
  - Link scripts at the bottom of `<body>` or use `defer` in `<head>`.

- **CSS**

  - Keep styles scoped to the component if possible.
  - Avoid global styles unless needed for layout or theming.
  - Prefer class selectors over element selectors for maintainability.

- **General Practices**

  - If the spec calls for multiple pages or sections, create additional HTML files and mirror the structure.
  - Avoid unnecessary abstraction—keep logic and markup straightforward unless complexity demands otherwise.
  - Do not add guards for libraries or assets that are required per the spec—assume they’re present.
  - Keep inline scripts and styles to a minimum unless specifically required.
