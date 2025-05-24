Recipe goal:
Turn any existing recipe (JSON) into a ready-to-preview Mermaid diagram that follows the “collapsed-subgraph” style we like.

Set up the following inputs:

- recipe_path (required): Full path to the JSON recipe you want to visualize
- output_path: The folder to save the diagram to (default: `output`)
- diagram_filename: The filename to save the diagram to (Mermaid markdown file, default: same path as filename part of `recipe_path` but with \*.md)
- model: LLM to use to generate the diagram (default: openai/o4-mini)

Steps:

1. Read the target recipe file

- Load the entire file found at `recipe_path`

2. Ask the LLM to produce the diagram

- Invoke the model specified by `model`
- Provide this system instruction:

  > “You are an expert in the Recipe-Executor JSON format.
  > Output only a Mermaid flow-chart that follows these rules:
  > • Each `execute_recipe` becomes its own collapsed subgraph named after the file.
  > • Insert an entry node (💬) at the call site and an exit node (⬆︎) when the sub-recipe returns.
  > • Use unique IDs like `<STEM>_S0`, `<STEM>_S1`, etc.
  > • For loops, render a `loop` node followed by an indented subgraph for its sub-steps.
  > • For conditionals, draw a diamond and separate IF_TRUE and IF_FALSE subgraphs.
  > • Provide a user-friendly label for each node.
  > • Do not include comments or Liquid templates in the output.
  > • Include proper line breaks and indentation.
  >
  > Here is the recipe JSON you must transform (between `<JSON>` tags):
  > `<JSON>` > {{ recipe_src }} > `</JSON>`

- Capture the model’s plain-text response as `mermaid_diagram`.\*

3. Write the diagram to disk

- Save `mermaid_diagram` to the file given by `diagram_path` (defaulting to the same folder and filename as `recipe_path`, but with a “.md” extension).\*
