# Teapot Document Generator

This recipe generates comprehensive documents about various teapot and ceramics-related topics, using a structured approach with predefined prompt templates. It leverages the document generator recipe with custom topic-based content generation.

## Files in this Directory

- `teapot_idea.md` - Original idea file with topic list and prompt templates
- `teapot.json` - Outline template with section structure and prompts for each topic
- `topics.txt` - List of topics for document generation (one per line)
- `process_topics.sh` - Bash script to process all topics sequentially

## How It Works

1. The system uses the document generator recipe with our custom teapot outline
2. Each topic from `topics.txt` is processed individually
3. The topic variable is used in both filename generation and document title
4. For each topic, the system:
   - Creates a markdown document named after the topic
   - Inserts the topic name as the document title
   - Processes each section with prompts that incorporate the topic
   - Writes the final document to the output directory

## Modifications to Document Generator

We made the following changes to the document generator recipe:

1. Added a `topic` input parameter to accept the current topic being processed
2. Modified the `document_filename` to use the topic name:
   ```json
   "document_filename": "{{ topic | default: outline_file | default: 'document' | replace: '\\', '/' | split: '/' | last | split: '.' | first | replace: ' ', '_' | downcase }}"
   ```
3. Added a `topic_string` variable to properly handle the topic name:
   ```json
   {
     "type": "set_context",
     "config": {
       "key": "topic_string",
       "value": "{{ topic }}"
     }
   }
   ```
4. Updated the `outline.title` to use the topic string:
   ```json
   {
     "type": "set_context",
     "config": {
       "key": "outline.title",
       "value": "{{ topic_string | default: outline.title }}",
       "if_exists": "overwrite"
     }
   }
   ```
5. Used the topic string directly in document initialization:
   ```json
   {
     "type": "set_context",
     "config": {
       "key": "document",
       "value": "# {{ topic_string | default: outline.title }}\n\n[document-generator]\n\n**Date:** {{ 'now' | date: '%-m/%-d/%Y %I:%M:%S %p' }}"
     }
   }
   ```

## Usage

### Generate a Document for a Single Topic

```bash
python recipe_tool.py --execute recipes/document_generator/document-generator-recipe.json \
  outline_file=recipes/teapots/teapot.json \
  output_root=output/teapots \
  model=azure/o4-mini \
  topic="Yixing zisha clay characteristics"
```

### Process All Topics in topics.txt

```bash
# Ensure the script is executable
chmod +x recipes/teapots/process_topics.sh

# Run the script
./recipes/teapots/process_topics.sh
```

The script will:
1. Activate the virtual environment if not already activated
2. Navigate to the project root directory
3. Create the output directory if it doesn't exist
4. Process each topic in `topics.txt` sequentially

## Output Structure

Each generated document follows a consistent structure with seven sections:

1. **Dawn in the Studio** - Rich, narrative introduction to the topic
2. **Footprints in Fired Earth** - Historical narrative and context
3. **Surfaces That Sing** - Artistic significance and aesthetic exploration
4. **Anatomy of Heat & Clay** - Technical breakdown of physical processes
5. **Hands in the Mud: A Studio Roadmap** - Practical guide for implementation
6. **Forks in the Firing Path** - Comparison of different approaches
7. **Kiln-side Confessions** - Narrative addressing common misconceptions

All documents are saved in the `output/teapots` directory with filenames derived from the topic.

## Known Issues and Observations

### Section Heading Inconsistencies

While testing the document generation, we observed that section headings are sometimes missing or improperly formatted in the output documents. After analyzing the code and outputs, we've identified the following:

1. **Root Cause**: The section headings are not explicitly added by the document generator recipe. Instead, the LLM is responsible for including them in its generated content.

2. **Technical Details**:
   - In `write_section.json`, content is merged directly with:
     ```json
     "key": "document",
     "value": "\n\n{{ generated.content }}",
     "if_exists": "merge"
     ```
   - The LLM prompt asks to "write ONLY THE NEW `{{ section.title }}` SECTION" but doesn't explicitly instruct to format it as a markdown heading

3. **Inconsistent Behavior**: While most sections are correctly formatted with markdown headings (e.g., `## Section Title`), some sections occasionally miss proper heading formatting depending on how the LLM generates the content.

### Potential Solutions

For the recipe author, we'd recommend one of these approaches:

1. **Explicit Heading Addition**: Modify `write_section.json` to explicitly add the section heading before appending the LLM-generated content:
   ```json
   "key": "document",
   "value": "\n\n## {{ section.title }}\n\n{{ generated.content }}",
   "if_exists": "merge"
   ```

2. **Clearer LLM Instructions**: Update the prompt to explicitly request proper markdown formatting:
   ```
   Please write ONLY THE NEW `{{ section.title }}` SECTION as a proper markdown section with '## {{ section.title }}' as the heading, in the same style as the rest of the document.
   ```

This issue is unrelated to our modifications for topic variable handling but would improve the consistency of generated documents.

### Additional Markdown Formatting Issues

After examining multiple output documents, we identified several additional markdown formatting inconsistencies:

1. **Tables Formatted as Code Blocks**: In some documents, markdown tables are enclosed in code blocks (with triple backticks), preventing them from rendering properly as tables. For example, in `rutile_micro-crystal_growth_triggers.md`:
   ```
   ```markdown
   | Method            | Difficulty | Cost       | Typical Result                                        | Best-Suited Form            |
   ...
   ```
   ```

2. **Inconsistent Bullet Point Formatting**: Some sections use proper markdown bullets (`- item`) while others use non-standard formatting like bullet symbols (`• item`), asterisks without spaces (`*item*`), or numbered lists without proper markdown syntax.

3. **Missing Section Headings**: Some sections appear in the document without any heading (particularly in the middle sections of documents).

4. **Inconsistent Header Levels**: Occasionally the LLM uses `#` (h1) instead of `##` (h2) for section headings, creating an inconsistent document structure.

### Additional Recommendations

To address these broader markdown formatting issues:

1. **Comprehensive Markdown Instructions**: Include explicit markdown formatting guidelines in the LLM prompt:
   ```
   Please format your response using proper markdown:
   - Use '## Title' for section headings
   - Format tables with standard markdown pipe syntax (no code blocks)
   - Use '- ' for bullet points
   - Use '1. ' for numbered lists
   ```

2. **Post-Processing Step**: Consider adding a post-processing step that standardizes markdown formatting in the output by:
   - Ensuring all section titles use the correct heading level
   - Converting non-standard bullets to markdown bullets
   - Removing code blocks around tables
   
3. **Example-Based Prompting**: Include examples of proper markdown formatting in the prompt, showing the LLM exactly how you want tables, lists, and headings to be formatted.

These issues are likely occurring because the LLM isn't explicitly instructed to use proper markdown syntax in its output. Since markdown is just one of many text formats an LLM might use, being explicit about the expected output format would help ensure consistency.