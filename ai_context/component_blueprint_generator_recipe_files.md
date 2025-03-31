=== File: recipes/component_blueprint_generator/README.md ===

# Component Blueprint Generator - Summary

## Overview

The Component Blueprint Generator is a recipe-based system that creates comprehensive component blueprints from candidate specifications. It generates all the necessary files for implementing a component following the modular building-block approach to software development with AI.

## Key Features

1. **Automated Blueprint Generation**: Convert a simple candidate spec into a complete set of blueprint files
2. **Specification Refinement**: Generate formal, structured component specifications
3. **Documentation Generation**: Create comprehensive usage documentation with examples
4. **Recipe Creation**: Generate the recipe files needed to implement and edit the component
5. **Consistent Structure**: Ensure all components follow the same structural patterns
6. **Specification Evaluation**: Assess candidate specifications for completeness and clarity
7. **Clarification Questions**: Generate targeted questions to improve incomplete specifications

## How It Works

1. A candidate specification is provided as input
2. AI analyzes the spec to extract key component information
3. The system generates a formal specification document
4. Documentation is created based on the specification
5. Recipe files for component creation and editing are generated
6. A summary report is created with instructions for using the generated files

## Generated Files for Each Component

For each component, the system generates:

1. **Specification File**: `specs/[component_path]/[component_id].md`
2. **Documentation File**: `docs/[component_path]/[component_id].md`
3. **Recipe Files**:
   - `recipes/[component_id]/create.json`
   - `recipes/[component_id]/edit.json`
4. **Blueprint Summary**: `[component_id]_blueprint_summary.md`

## Usage Instructions

### Basic Usage

To generate a component blueprint from a candidate specification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context component_path=/path/in/project \
  --context output_root=output
```

To evaluate a candidate specification and generate clarification questions if needed:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/evaluate_candidate_spec.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context output_root=output
```

To specifically generate clarification questions for an incomplete specification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/generate_clarification_questions.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context output_root=output
```

### Parameters

- `candidate_spec_path`: Path to the candidate specification file
- `component_path`: Path where the component should be located in the project structure
- `output_root`: Base directory for output files (default: "output")
- `model`: LLM model to use (default: "openai:o3-mini")

### Workflow

1. **Create Candidate Spec**: Write a basic specification for your component
2. **Evaluate Specification**: Run the evaluation recipe to check for completeness
3. **Address Clarifications**: If needed, answer the clarification questions
4. **Generate Blueprint**: Run the blueprint generator recipe
5. **Review Generated Files**: Examine the specification, documentation, and recipes
6. **Generate Component**: Use the generated recipes to create the actual component code
7. **Iterate if Needed**: If changes are needed, edit the specification and regenerate

## Files in this Recipe System

| File                                    | Purpose                                                          |
| --------------------------------------- | ---------------------------------------------------------------- |
| `build_blueprint.json`                  | Main entry point recipe for blueprint generation                 |
| `create.json`                           | Orchestrates the blueprint generation process                    |
| `create_spec.json`                      | Generates the formal specification                               |
| `create_doc.json`                       | Creates component documentation                                  |
| `create_recipes.json`                   | Generates component recipe files                                 |
| `finalize_blueprint.json`               | Creates a summary report                                         |
| `evaluate_candidate_spec.json`          | Evaluates a candidate specification for completeness             |
| `generate_clarification_questions.json` | Generates questions to improve incomplete specs                  |
| `spec_template.md`                      | Template for specification files                                 |
| `doc_template.md`                       | Template for documentation files                                 |
| `SPEC_DOC_GUIDE.md`                     | Comprehensive guide to creating specifications and documentation |
| `IMPLEMENTATION_PHILOSOPHY.md`          | Philosophy for implementation approaches                         |
| `MODULAR_DESIGN_PHILOSOPHY.md`          | Philosophy for modular, building-block design                    |

## Example Workflow

1. Create a candidate specification for a new "DataValidator" component
2. Run the evaluation recipe to check for completeness and clarity
3. If the specification is incomplete, review the clarification questions
4. Update the candidate specification to address the identified gaps
5. Run the blueprint generator to create the full set of component files
6. Review the generated specification, documentation, and recipes
7. Use the generated create.json recipe to implement the component
8. If changes are needed, edit the specification and regenerate

## Benefits

- **Consistency**: All components follow the same structure and patterns
- **Efficiency**: Automates the creation of boilerplate files
- **Quality**: Ensures comprehensive specifications and documentation
- **Flexibility**: Generate variations by adjusting the candidate spec
- **Guidance**: Helps identify and address gaps in component specifications
- **Iterative Improvement**: Supports an iterative approach to specification development
- **Knowledge Transfer**: Educates developers on best practices for component design

This system embodies the modular building-block approach to software development, where components are clearly specified with stable interfaces and can be independently regenerated without breaking the whole system.

=== File: recipes/component_blueprint_generator/build-blueprint.json ===
{
"steps": [
{
"type": "read_file",
"path": "{{candidate_spec_path}}",
"artifact": "candidate_spec"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/SPEC_DOC_GUIDE.md",
"artifact": "spec_doc_guide"
},
{
"type": "read_file",
"path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
"artifact": "implementation_philosophy"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md",
"artifact": "modular_design_philosophy"
},
{
"type": "generate",
"prompt": "You are an expert developer tasked with analyzing a candidate specification and creating a blueprint for component generation. Review the candidate specification and extract key information needed to create a formal specification, documentation, and recipe files.\n\nCandidate Specification:\n{{candidate_spec}}\n\nYour task is to extract the following information:\n1. Component name\n2. Component ID (lowercase, underscore-separated version of the name)\n3. Module path (where the component would be imported from)\n4. Component type (utility, core, step, etc.)\n5. Key functionality (brief summary)\n6. Main dependencies\n\nFormat your response as a JSON object with these fields.\n\nUse the following guides for context:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "component_info"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/create.json",
"context_overrides": {
"component_info": "{{component_info}}",
"candidate_spec": "{{candidate_spec}}"
}
}
]
}

=== File: recipes/component_blueprint_generator/create.json ===
{
"steps": [
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/SPEC_DOC_GUIDE.md",
"artifact": "spec_doc_guide"
},
{
"type": "read_file",
"path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
"artifact": "implementation_philosophy"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md",
"artifact": "modular_design_philosophy"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/create_spec.json"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/create_doc.json"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/create_recipes.json"
},
{
"type": "execute_recipe",
"recipe_path": "recipes/component_blueprint_generator/recipes/finalize_blueprint.json"
}
]
}

=== File: recipes/component_blueprint_generator/evaluate-candidate-spec.json ===
{
"steps": [
{
"type": "read_file",
"path": "{{candidate_spec_path}}",
"artifact": "candidate_spec"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/SPEC_DOC_GUIDE.md",
"artifact": "spec_doc_guide"
},
{
"type": "read_file",
"path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
"artifact": "implementation_philosophy"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md",
"artifact": "modular_design_philosophy"
},
{
"type": "generate",
"prompt": "You are an expert developer evaluating a candidate component specification to determine if it has enough context for effective implementation. You'll analyze the candidate specification and identify any areas that need clarification or additional information.\n\nCandidate Specification:\n{{candidate_spec}}\n\nUse the following guides as your evaluation criteria:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nPerform a systematic evaluation of the candidate specification with these steps:\n\n1. Identify the component name and type (if possible)\n2. Determine if a clear purpose statement exists\n3. Check if core requirements are well-defined and specific\n4. Assess if implementation considerations are provided\n5. Evaluate whether component dependencies are properly identified\n6. Check if error handling approaches are specified\n7. Look for any information about future considerations\n\nFor each aspect, provide:\n- A score from 1-5 (1=Missing/Insufficient, 5=Excellent)\n- Brief explanation of the score\n- Specific clarification questions if the score is 3 or lower\n\nFormat your response with these sections:\n1. Overall Assessment - Brief overview with readiness determination\n2. Scoring Summary - Table with scores for each aspect\n3. Detailed Analysis - Detailed assessment of each aspect with clarification questions\n4. Improvement Recommendations - List of questions to improve the specification\n\nBe constructive but thorough in your assessment.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "evaluation_result"
},
{
"type": "generate",
"prompt": "Format the specification evaluation as a proper markdown file with informative title and sections.\n\nEvaluation Result:\n{{evaluation_result}}\n\nFormat your response as a FileGenerationResult with a single file. The file path should include the component name if it could be identified from the specification, otherwise use 'component'.\n\nIf the evaluation determined that the specification needs significant clarification, name the file 'clarification_questions.md'. If the specification was deemed sufficient, name the file 'evaluation_summary.md'.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "formatted_evaluation"
},
{
"type": "write_file",
"artifact": "formatted_evaluation",
"root": "{{output_root|default:'output'}}"
}
]
}

=== File: recipes/component_blueprint_generator/generate-clarification-questions.json ===
{
"steps": [
{
"type": "read_file",
"path": "{{candidate_spec_path}}",
"artifact": "candidate_spec"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/SPEC_DOC_GUIDE.md",
"artifact": "spec_doc_guide"
},
{
"type": "read_file",
"path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
"artifact": "implementation_philosophy"
},
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md",
"artifact": "modular_design_philosophy"
},
{
"type": "generate",
"prompt": "You are an expert developer helping to improve a candidate component specification by generating clarification questions. Based on the candidate specification and understanding of effective component design, create a comprehensive set of questions that would help make the specification complete and implementable.\n\nCandidate Specification:\n{{candidate_spec}}\n\nUse the following guides to understand what information is needed in an effective specification:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nGenerate clarification questions organized into these categories:\n\n1. Purpose and Scope\n- Questions about the component's primary responsibility\n- Questions about boundaries and what's out of scope\n- Questions about the problem being solved\n\n2. Functional Requirements\n- Questions about specific capabilities needed\n- Questions about user/system interactions\n- Questions about expected inputs and outputs\n\n3. Technical Requirements\n- Questions about implementation constraints\n- Questions about performance requirements\n- Questions about security considerations\n\n4. Integration and Dependencies\n- Questions about how it interacts with other components\n- Questions about external dependencies\n- Questions about interface requirements\n\n5. Error Handling and Edge Cases\n- Questions about failure scenarios\n- Questions about edge cases\n- Questions about recovery mechanisms\n\nIn each category, provide 3-5 specific questions that would help improve the specification. Make the questions clear, specific, and directly relevant to the candidate specification. For each question, briefly explain why this information is important for implementation.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "clarification_questions"
},
{
"type": "generate",
"prompt": "Format the clarification questions as a structured markdown document that can be shared with stakeholders.\n\nClarification Questions:\n{{clarification_questions}}\n\nCandidate Specification:\n{{candidate_spec}}\n\nCreate a document with these sections:\n1. Introduction - Brief explanation of the purpose of this document and the component being specified\n2. Current Specification - A summary of the current candidate specification\n3. Key Areas Needing Clarification - Overview of the major gaps identified\n4. Detailed Questions - The clarification questions organized by category\n5. Next Steps - Guidance on how to use these questions to improve the specification\n\nFormat your response as a FileGenerationResult with a single file named 'component_specification_clarification_questions.md' (or use the component name if it can be identified).",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "formatted_questions"
},
{
"type": "write_file",
"artifact": "formatted_questions",
"root": "{{output_root|default:'output'}}"
}
]
}

=== File: recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md ===

# Building Software with AI: A Modular Block Approach

_By Brian Krabach_
_3/28/2025_

---

## Introduction

Imagine you're about to build a complex modular spacecraft model. You dump out thousands of tiny building blocks and open the instruction booklet. Step by step, the booklet tells you which pieces to use and how to connect them. You don't need to worry about the details of each block or whether it will fit — the instructions guarantee that every piece snaps together correctly. Now imagine those building blocks could assemble themselves whenever you gave them the right instructions.

This is the essence of our new AI-driven software development approach: we provide the blueprint, and AI builds the product, one modular piece at a time.

## Modular Design: The Building Block Analogy

Like a modular construction kit, our software is built from small, clear modules. Each module is a self-contained "block" of functionality with defined connectors (interfaces) to the rest of the system. Because these connection points are standard and stable, we can generate or regenerate any single module independently without breaking the whole.

- **Independent Regeneration:**
  Need to improve the user login component? The AI rebuilds just that piece according to its spec, then snaps it back into place — all while the rest of the system continues to work seamlessly.

- **Large-Scale Changes:**
  For broad, cross-cutting updates, we hand the AI a larger blueprint (for a larger assembly or even the entire codebase) and let it rebuild that chunk in one go.

- **Stable External Contracts:**
  The external system contracts — the equivalent of block connectors and sockets — remain unchanged. Even if a module is regenerated, it continues to fit perfectly into its environment, benefiting from fresh optimizations and improvements.

## Code Generation and Maintenance

Modern LLM-powered tools enable us to treat code as something to describe and then generate, rather than tweaking it line-by-line. By keeping each task small and self-contained — like one page of construction instructions — the AI has all the context it needs to build that piece correctly from start to finish. This process:

- **Ensures Predictability:**
  The code generation is more predictable and reliable when working within a bounded context.

- **Maintains Specification Sync:**
  Each regenerated module is consistently in sync with its specification, as the system opts for regeneration over ad-hoc editing.

## The Human Role: From Code Mechanics to Architects

In this new approach, human developers transition from being code mechanics to becoming architects and quality inspectors. Much like a master designer, the human defines the vision and specifications up front — the blueprint for what needs to be built. After that, the focus shifts from micromanaging every block to ensuring the assembled product meets the intended vision.

Key responsibilities include:

- **Designing Requirements:**
  Crafting the overall vision and high-level specifications.

- **Clarifying Behavior:**
  Detailing the intended behavior without scrutinizing every line of code.

- **Evaluating Results:**
  Testing the finished module or system by validating its functionality, such as verifying that the user login works smoothly and securely.

This elevated role allows humans to contribute where they add the most value, while AI handles the intricate construction details.

## Building in Parallel

A major breakthrough of this approach is the ability to build multiple solutions simultaneously. With AI's rapid and modular capabilities, we can:

- **Generate Multiple Variants:**
  Experiment with several versions of a feature, such as testing different recommendation algorithms in parallel.

- **Platform-Specific Builds:**
  Construct the same application for various platforms (web, mobile, etc.) at the same time by following tailored instructions.

- **Accelerate Experimentation:**
  Run parallel tests to determine which design or user experience performs best, learning from each variant to refine the blueprint.

This cycle of parallel experimentation and rapid regeneration not only accelerates innovation but also allows for continuous refinement of high-level specifications.

## Conclusion

This modular, AI-driven approach transforms traditional software development by:

- **Breaking the work into well-defined pieces**
- **Allowing AI to handle detailed construction**
- **Enabling humans to focus on vision and quality**

The outcome is a process that is more flexible, faster, and liberating. It empowers us to reshape our software as easily as snapping together (or rebuilding) a model construction kit, even building multiple versions in parallel. For stakeholders, this means delivering the right solution faster, adapting to change seamlessly, and continually exploring new ideas — block by block.

---

> **Classified as Microsoft Confidential** > **Classified as Microsoft Confidential** > **Classified as Microsoft Confidential** > **Classified as Microsoft Confidential**

=== File: recipes/component_blueprint_generator/includes/SPEC_DOC_GUIDE.md ===

# Comprehensive Guide to Creating Effective Component Specifications and Documentation

## Introduction

This guide outlines how to create high-quality component specifications and documentation that enable AI-assisted code generation in a modular software architecture. When specifications and documentation work together effectively, they form a complete blueprint that allows for predictable, reliable code generation with minimal human intervention.

## Component Specification Best Practices

### 1. Structure and Organization

A well-structured component specification should include:

- **Component Title**: Clear, concise name that reflects the component's purpose
- **Purpose Statement**: 2-3 sentences describing what the component does and why it exists
- **Core Requirements**: Bulleted list of essential functionality
- **Implementation Considerations**: Guidance on how to approach the implementation
- **Component Dependencies**: Other components this one interacts with
- **Error Handling**: Expected approach to failures and edge cases
- **Future Considerations**: Optional section for planned extensions

### 2. Purpose Statement Clarity

The purpose statement should:

- Define the component's role in the larger system
- Establish boundaries of responsibility
- Avoid implementation details
- Be understandable without deep technical knowledge

Example:

```
"The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution."
```

### 3. Requirement Specificity

Requirements should be:

- Actionable and verifiable
- Focused on what, not how
- Free of ambiguity
- Collectively exhaustive (cover all needed functionality)
- Individually clear (one requirement per bullet)

Example:

```
- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Ensure data isolation between different executions
```

### 4. Implementation Guidance

Provide direction without over-constraining by:

- Suggesting approaches without dictating exact implementations
- Highlighting technical constraints or performance considerations
- Addressing known challenges or trade-offs
- Ensuring alignment with architectural principles

Example:

```
- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
```

### 5. Dependency Clarity

When specifying dependencies:

- List all components this one interacts with
- Explain the nature of each dependency relationship
- Note whether dependencies are required or optional
- Include external libraries or services if relevant

Example:

```
The Executor component depends on:
- **Context** - Uses Context for data sharing between steps
- **Step Registry** - Uses STEP_REGISTRY to look up step classes by type
```

### 6. Error Handling Specificity

For error handling sections:

- Identify expected error conditions
- Specify how each error should be handled
- Define error communication mechanisms
- Clarify recovery expectations

Example:

```
- Validate recipe format before execution begins
- Check that step types exist in the registry before instantiation
- Verify each step is properly structured before execution
- Provide specific error messages identifying problematic steps
```

## Component Documentation Best Practices

### 1. Structure and Organization

Well-structured documentation includes:

- **Importing Section**: How to import the component
- **Basic Usage**: Simple examples showing common use cases
- **API Reference**: Detailed description of each method/function
- **Example Patterns**: More complex usage examples
- **Integration Guidelines**: How to use with other components
- **Important Notes**: Critical things developers should know

### 2. Code Examples

Effective code examples should:

- Start with the simplest possible use case
- Progress to more complex scenarios
- Include comments explaining key parts
- Show both initialization and usage
- Demonstrate error handling where appropriate
- Be complete enough to run if copied

Example:

```python
# Create context and executor
context = Context()
executor = RecipeExecutor()

# Execute a recipe from a file
executor.execute("path/to/recipe.json", context)

# Or from a JSON string
json_string = '{"steps": [{"type": "read_file", "path": "example.txt", "artifact": "content"}]}'
executor.execute(json_string, context)
```

### 3. Method Documentation

Document each method with:

- Method signature with type hints
- Purpose description
- Parameter explanations
- Return value description
- Possible exceptions/errors
- Usage examples

Example:

```
def render_template(text: str, context: Context) -> str:
    """
    Render the given text as a Liquid template using the provided context.
    All values in the context are converted to strings before rendering.

    Args:
        text (str): The template text to render.
        context (Context): The context for rendering the template.

    Returns:
        str: The rendered text.

    Raises:
        ValueError: If there is an error during template rendering.
    """
```

### 4. Integration Examples

Show how components work together:

- Demonstrate common integration patterns
- Illustrate correct sequencing of operations
- Show data flow between components
- Include common use cases in the larger system

Example:

```python
# Initialize components
context = Context(artifacts={"component_id": "utils"})
logger = init_logger()
executor = RecipeExecutor()

# Execute recipe with context and logger
executor.execute("recipes/generate_component.json", context, logger)

# Access results from context
result = context["generation_result"]
```

### 5. Important Notes & Warnings

Highlight critical information:

- Common pitfalls or misunderstandings
- Performance considerations
- Thread safety concerns
- Order-dependent operations
- Breaking changes from previous versions

Example:

```
1. The context is mutable and shared between steps
2. Values can be of any type
3. Configuration is read-only in typical usage (but not enforced)
4. Step authors should document keys they read/write
5. Context provides no thread safety - it's designed for sequential execution
```

## The Component Specification and Documentation Relationship

### 1. Complementary Focus

- **Specifications**: Focus on requirements, constraints, and architectural fit
- **Documentation**: Focus on usage, examples, and developer experience

### 2. Consistent Terminology

- Use identical terms for core concepts across specs and docs
- Define terms clearly in both documents
- Maintain consistent naming conventions for methods, parameters, and classes

### 3. Functional Coverage Alignment

- Every requirement in the spec should be addressed in the documentation
- Documentation shouldn't introduce functionality not mentioned in specs
- Both should reflect the same component boundaries and responsibilities

## Optimizing for AI Code Generation

### 1. Explicit Boundaries

- Clearly define where one component ends and another begins
- Specify exact interfaces and contracts
- Make inputs and outputs unambiguous
- Define error states and handling explicitly

### 2. Context Sufficiency

- Provide enough information for an isolated implementation
- Include cross-references to related components when needed
- Supply concrete examples that illustrate expected behavior
- Clarify architectural principles that should guide implementation

### 3. Implementation Independence

- Focus on what the component does, not exactly how it does it
- Allow for creative implementations within constraints
- Specify constraints clearly but don't over-constrain
- Separate required behavior from implementation suggestions

### 4. Testability Focus

- Include clear success criteria
- Define expected behaviors for edge cases
- Specify performance expectations where relevant
- Provide examples of valid and invalid inputs/outputs

## Modular Building-Block Approach Considerations

### 1. Interface Stability

- Define stable connecting points between components
- Clearly mark which interfaces are public vs. internal
- Version interfaces explicitly when they must change
- Maintain backward compatibility where possible

### 2. Independent Regeneration Support

- Design components that can be replaced without breaking others
- Document all cross-component dependencies
- Ensure all state transitions are explicit
- Avoid hidden dependencies or assumptions

### 3. Compatibility with Parallel Development

- Design components that can be developed independently
- Document how variants might differ
- Specify minimum viable implementations
- Clarify how different implementations might be evaluated

### 4. Evolution Path Support

- Document anticipated extension points
- Provide guidelines for future enhancements
- Separate core functionality from optional features
- Establish clear versioning expectations

## Common Pitfalls to Avoid

### 1. Specification Pitfalls

- **Ambiguity**: Vague requirements open to multiple interpretations
- **Implementation dictation**: Focusing too much on how instead of what
- **Missing constraints**: Failing to specify important limitations
- **Over-specification**: Constraining implementation unnecessarily
- **Inconsistent terminology**: Using multiple terms for the same concept

### 2. Documentation Pitfalls

- **Incompleteness**: Failing to document all methods or parameters
- **Outdated examples**: Examples that no longer work with current code
- **Missing error handling**: Examples that don't show how to handle failures
- **Inconsistent style**: Mixing different coding styles in examples
- **Assuming context**: Not explaining prerequisites or dependencies

## Comparative Examples

### Effective Specification Example

```
# Context Component Specification

## Purpose
The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.

## Core Requirements
- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Ensure data isolation between different executions
- Follow minimalist design principles

## Implementation Considerations
- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Provide clear error messages for missing keys
- Return copies of internal data to prevent external modification
- Maintain minimal state with clear separation of concerns

## Component Dependencies
The Context component has no external dependencies on other Recipe Executor components.

## Error Handling
- Raise KeyError with descriptive message when accessing non-existent keys
- No special handling for setting values (all types allowed)

## Future Considerations
- Namespacing of artifacts
```

### Ineffective Specification Example

```
# Context Component Specification

The Context will be a global data store object for passing data between steps. It should be as flexible as possible and handle all data types. We should consider potential threading issues, performance optimizations, and potential for future extensions.

It will probably need to be a dictionary-like object, maybe with some extra features. Make sure to include good error handling.

We might add namespacing later, so keep that in mind.
```

### Effective Documentation Example

````
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
````

## Initialization

The Context can be initialized with optional artifacts and configuration:

```python
# Method signature
def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the Context with optional artifacts and configuration.

    Args:
        artifacts: Initial artifacts to store
        config: Configuration values
    """
```

Examples:

```python
# Empty context
context = Context()

# With initial artifacts
context = Context(artifacts={"spec": "specification content"})

# With configuration
context = Context(config={"output_dir": "./output"})

# With both
context = Context(
    artifacts={"spec": "specification content"},
    config={"output_dir": "./output"}
)
```

## Core API

### Storing Values

```python
# Usage example
context["key"] = value
```

### Retrieving Values

```python
# Usage examples
value = context["key"]  # Raises KeyError if not found
value = context.get("key", default=None)  # Returns default if not found
```

## Important Notes

1. Context is mutable and shared between steps
2. Values can be of any type
3. Configuration is read-only in typical usage (but not enforced)
4. Step authors should document keys they read/write
5. Context provides no thread safety - it's designed for sequential execution

```

### Ineffective Documentation Example

```

# Context Usage

The Context class is used to store data. You can create it like this:

```python
c = Context()
```

You can store and retrieve data:

```python
c["key"] = value
x = c["key"]
```

Make sure to handle errors.

````

## Conclusion

Creating effective component specifications and documentation is crucial for enabling AI-assisted code generation in a modular architecture. By following these guidelines, you can create clear, comprehensive blueprints that allow for reliable and predictable implementation of each building block in your system.

Remember that the goal is to provide sufficient information for independent implementation while maintaining compatibility with the overall system architecture. When specifications and documentation work together effectively, they create a foundation for an efficient, adaptable development process that leverages AI capabilities while preserving architectural integrity.


=== File: recipes/component_blueprint_generator/includes/templates/doc-template.md ===
# {{component_name}} Component Usage

## Importing

```python
from {{module_path}} import {{component_name}}
````

## Initialization

[Description of initialization]

```python
# Example initialization
```

## Core API

### [Method/Function 1]

```python
def method_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    [Method description]

    Args:
        param1: [Parameter description]
        param2: [Parameter description]

    Returns:
        [Return value description]

    Raises:
        [Exception]: [Exception description]
    """
```

Example:

```python
# Usage example
```

### [Method/Function 2]

...

## Integration with Other Components

[Description of how this component interacts with others]

```python
# Integration example
```

## Important Notes

1. [Important note 1]
2. [Important note 2]
3. ...

=== File: recipes/component_blueprint_generator/includes/templates/spec-template.md ===

# {{component_name}} Component Specification

## Purpose

[Brief description of the component's purpose and role in the system]

## Core Requirements

- [Requirement 1]
- [Requirement 2]
- [Requirement 3]
- ...

## Implementation Considerations

- [Implementation consideration 1]
- [Implementation consideration 2]
- [Implementation consideration 3]
- ...

## Component Dependencies

The {{component_name}} component depends on:

- [Dependency 1] - [Description of relationship]
- [Dependency 2] - [Description of relationship]
- ...

## Error Handling

- [Error handling approach 1]
- [Error handling approach 2]
- ...

## Future Considerations

- [Future consideration 1]
- [Future consideration 2]
- ...

=== File: recipes/component_blueprint_generator/recipes/create-doc.json ===
{
"steps": [
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/templates/doc_template.md",
"artifact": "doc_template"
},
{
"type": "generate",
"prompt": "You are an expert developer creating component documentation. Based on the component specification and information, create comprehensive usage documentation following the template structure.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Information:\n{{component_info}}\n\nDocumentation Template:\n{{doc_template}}\n\nUse the following guides for context:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\nCreate complete, detailed documentation for the component that follows the template structure but is tailored to this specific component's functionality. Include clear examples, method documentation, and integration guidance.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "generated_doc"
},
{
"type": "write_file",
"artifact": "generated_doc",
"root": "{{output_root|default:'output'}}/docs/{{component_path}}"
}
]
}

=== File: recipes/component_blueprint_generator/recipes/create-recipes.json ===
{
"steps": [
{
"type": "generate",
"prompt": "You are an expert developer creating recipe files for component generation and editing. Based on the component specification, documentation, and information, create JSON recipe files that will be used to generate and later edit the component code.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent Information:\n{{component_info}}\n\nUse the following guides for context:\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nCreate two recipe files:\n1. A 'create.json' recipe that generates the component from scratch\n2. An 'edit.json' recipe that can edit an existing implementation of the component\n\nBoth recipes should follow the pattern used in the recipe_executor and codebase_generator projects, using appropriate steps like read_file, generate, and write_file. The recipes should handle dependencies, read in the specification and documentation, and use them to generate or edit the component code.\n\nYour response should be a JSON object with two keys: 'create_recipe' and 'edit_recipe', each containing the full JSON content of the respective recipe file.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "generated_recipes"
},
{
"type": "generate",
"prompt": "You've just created JSON recipes for component generation. Based on these recipes, create a file list that we can use to write the files to disk. Extract the recipes from the JSON structure and format them for writing to individual files.\n\nGenerated Recipes:\n{{generated_recipes}}\n\nFormat your response as a FileGenerationResult with two files:\n1. 'recipes/{{component_id}}/create.json' - The create recipe\n2. 'recipes/{{component_id}}/edit.json' - The edit recipe\n\nEnsure the JSON is properly formatted and follows the structure of the other recipe files in the system.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "recipe_files"
},
{
"type": "write_file",
"artifact": "recipe_files",
"root": "{{output_root|default:'output'}}"
}
]
}

=== File: recipes/component_blueprint_generator/recipes/create-spec.json ===
{
"steps": [
{
"type": "read_file",
"path": "recipes/component_blueprint_generator/includes/templates/spec_template.md",
"artifact": "spec_template"
},
{
"type": "generate",
"prompt": "You are an expert developer creating a formal component specification. Based on the candidate specification and component information, create a detailed specification document following the template structure.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent Information:\n{{component_info}}\n\nSpecification Template:\n{{spec_template}}\n\nUse the following guides for context:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nCreate a complete, detailed specification for the component that follows the template structure but is tailored to this specific component's needs.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "generated_spec"
},
{
"type": "write_file",
"artifact": "generated_spec",
"root": "{{output_root|default:'output'}}/specs/{{component_path}}"
}
]
}

=== File: recipes/component_blueprint_generator/recipes/finalize-blueprint.json ===
{
"steps": [
{
"type": "generate",
"prompt": "You are an expert developer finalizing a component blueprint. Review all the generated artifacts and create a summary report that describes what has been created and how to use these artifacts to generate the component.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent Recipe Files:\n{{recipe_files}}\n\nComponent Information:\n{{component_info}}\n\nCreate a summary report that includes:\n1. An overview of the component\n2. A list of all generated files with their locations\n3. Instructions for using the recipes to generate the component\n4. Any special considerations or next steps\n\nThis report should serve as a guide for someone who wants to use these blueprint files to generate the actual component code.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "blueprint_summary"
},
{
"type": "generate",
"prompt": "Format the blueprint summary as a proper markdown file with the component ID as the file name.\n\nBlueprint Summary:\n{{blueprint_summary}}\n\nComponent Information:\n{{component_info}}\n\nFormat your response as a FileGenerationResult with a single file named '{{component_id}}_blueprint_summary.md' containing the formatted markdown summary.",
"model": "{{model|default:'openai:o3-mini'}}",
"artifact": "formatted_summary"
},
{
"type": "write_file",
"artifact": "formatted_summary",
"root": "{{output_root|default:'output'}}"
}
]
}
