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

1. **Specification File**: `<target_project>/specs/<component_id>.md`
2. **Documentation File**: `<target_project>/docs/<component_id>.md`
3. **Recipe Files**:
   - `<target_project>/recipes/<component_id>_create.json`
   - `<target_project>/recipes/<component_id>_edit.json`
4. **Blueprint Summary**: `<target_project>/<component_id>_blueprint_summary.md`

## Usage Instructions

### Basic Usage

To generate a component blueprint from a candidate specification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=/path/to/candidate_spec.md \
  --context component_id=auth \
  --context component_name="Authentication" \
  --context target_project=recipe_executor \
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
- `component_id`: ID of the component (lowercase, underscore-separated)
- `component_name`: Human-readable name of the component
- `target_project`: Name of the project/folder where component will be placed
- `output_root`: Base directory for output files (default: "output")
- `module_path` (optional): Import path for the component
- `component_type` (optional): Type of component (utility, core, etc.)
- `model` (optional): LLM model to use (default: "openai:o3-mini")

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


=== File: recipes/component_blueprint_generator/build_blueprint.json ===
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
      "prompt": "You are an expert developer analyzing a candidate specification. Extract key information needed for component generation.\n\nCandidate Specification:\n{{candidate_spec}}\n\nExtract these fields only if not already provided:\n- component_id: {{component_id|default:''}}\n- component_name: {{component_name|default:''}}\n- module_path: {{module_path|default:''}}\n- component_type: {{component_type|default:''}}\n- key_dependencies: {{key_dependencies|default:''}}\n- related_docs: {{related_docs|default:''}}\n\nIf component_name is not provided and not in the spec, derive a clean title-case name from component_id.\n\nFor related_docs, identify any documentation files this component might need based on its dependencies, like 'context_docs', 'utils_docs', etc.\n\nProvide a JSON object with these fields, using reasonable defaults when information is not clear.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "extracted_info"
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/component_blueprint_generator/create.json",
      "context_overrides": {
        "candidate_spec": "{{candidate_spec}}",
        "component_id": "{{component_id|default:extracted_info.component_id}}",
        "component_name": "{{component_name|default:extracted_info.component_name}}",
        "module_path": "{{module_path|default:extracted_info.module_path}}",
        "component_type": "{{component_type|default:extracted_info.component_type}}",
        "key_dependencies": "{{key_dependencies|default:extracted_info.key_dependencies}}",
        "related_docs": "{{related_docs|default:extracted_info.related_docs}}",
        "target_project": "{{target_project|default:''}}",
        "component_path": "{{component_path|default:''}}",
        "output_root": "{{output_root|default:'output'}}",
        "project_recipe_path": "recipes/{{target_project}}"
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


=== File: recipes/component_blueprint_generator/evaluate_candidate_spec.json ===
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


=== File: recipes/component_blueprint_generator/examples/README.md ===
# Component Blueprint Generator Examples

This directory contains example candidate specifications that can be used to test and demonstrate the Component Blueprint Generator system.

## Auth Component Example

The `auth_candidate_spec.md` file provides a sample candidate specification for an authentication component that integrates with Auth0 in production and provides a mock implementation for development environments.

### Using the Example

#### 1. Evaluate the Candidate Specification

First, evaluate the candidate specification to check for completeness and identify areas that need clarification:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/evaluate_candidate_spec.json \
  --context candidate_spec_path=recipes/component_blueprint_generator/examples/auth_candidate_spec.md \
  --context output_root=output
```

This will generate an evaluation report in the `output` directory, which will highlight areas where the specification is strong and where it needs improvement.

#### 2. Generate Clarification Questions

If the evaluation indicates that the specification needs improvement, generate specific clarification questions:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/generate_clarification_questions.json \
  --context candidate_spec_path=recipes/component_blueprint_generator/examples/auth_candidate_spec.md \
  --context output_root=output
```

This will create a structured document with targeted questions organized by category that can help improve the specification.

#### 3. Generate the Complete Blueprint

Once you've reviewed the evaluation and potentially improved the specification based on the clarification questions, generate the complete component blueprint:

```bash
python recipe_executor/main.py recipes/component_blueprint_generator/build_blueprint.json \
  --context candidate_spec_path=recipes/component_blueprint_generator/examples/auth_candidate_spec.md \
  --context component_id=auth \
  --context component_name="Authentication" \
  --context target_project=example_project \
  --context output_root=output
```

### Expected Outputs

After running the full workflow, you should find these files in the `output` directory:

1. **Evaluation Report**: `auth_evaluation_summary.md` or `clarification_questions.md`
2. **Clarification Questions**: `auth_specification_clarification_questions.md`
3. **Blueprint Files**:
   - `example_project/specs/auth.md` - Formal specification
   - `example_project/docs/auth.md` - Usage documentation
   - `example_project/recipes/auth_create.json` - Recipe for creating the component
   - `example_project/recipes/auth_edit.json` - Recipe for editing the component
   - `example_project/auth_blueprint_summary.md` - Summary of the generated blueprint

### Next Steps

1. Review the evaluation and clarification questions
2. Improve the candidate specification based on the feedback
3. Regenerate the blueprint with the improved specification
4. Use the generated `auth_create.json` recipe to implement the actual component:

```bash
python recipe_executor/main.py output/example_project/recipes/auth_create.json \
  --context output_root=src
```

#### 4. Implementing the Component Using Generated Files

After generating the blueprint, use the files to implement the component:

```bash
# First, create the component using the generated recipe
python recipe_executor/main.py output/example_project/recipes/auth_create.json \
  --context output_root=src
```

This command will:

- Read the formal specification from `output/example_project/specs/auth.md`
- Use the documentation from `output/example_project/docs/auth.md` for guidance
- Generate implementation code for both Auth0 and mock authentication
- Write the files to the appropriate locations in your project
- Create all necessary classes, functions, and utilities defined in the spec

The implementation will include:

- FastAPI middleware for authentication
- JWT token verification for Auth0
- Mock authentication service for development
- User information extraction from tokens
- Role-based access control utilities
- Configuration management with environment variables
- Proper error handling and logging

To test the implementation, follow the examples provided in the documentation file. If you need to make changes to the implementation later, use the edit recipe:

```bash
python recipe_executor/main.py output/example_project/recipes/auth_edit.json \
  --context output_root=src
```

## Creating Your Own Examples

To create your own example candidate specifications:

1. Create a markdown file with your component specification
2. Place it in this examples directory
3. Follow the same workflow as described above, updating the paths as needed

The more detail you provide in your candidate specification, the more complete the generated blueprint will be. However, the system is designed to help identify gaps, so even incomplete specifications can be a good starting point.


=== File: recipes/component_blueprint_generator/examples/auth_candidate_spec.md ===
# Authentication Component Specification

## Overview

We need an authentication component for our FastAPI service that will handle user authentication using Auth0 in production environments. It should also provide a mock implementation for development and testing environments that simulates the same behavior without requiring an actual Auth0 connection.

## Features

- Authenticate users via Auth0 in production
- Provide a mock authentication service for development
- Verify JWT tokens
- Extract user information from tokens
- Support role-based access control

## Implementation Details

The component should provide FastAPI middleware and dependency functions for protecting routes. It should verify tokens from Auth0 and extract user claims. The mock implementation should generate tokens that have the same structure and can be verified locally.

We should support different roles like "admin", "user", etc. and have decorators or utilities to check permissions.

## Dependencies

- FastAPI
- Auth0 Python SDK
- PyJWT

## Configuration

The component should be configurable via environment variables:

- AUTH_MODE: "auth0" or "mock"
- AUTH0_DOMAIN
- AUTH0_API_AUDIENCE
- AUTH0_ALGORITHMS

## Expected API

```python
# Example usage
from auth import requires_auth, get_user, requires_role

@app.get("/protected")
@requires_auth
def protected_route():
    user = get_user()
    return {"message": f"Hello, {user.name}"}

@app.get("/admin")
@requires_role("admin")
def admin_route():
    return {"message": "Admin access granted"}
```


=== File: recipes/component_blueprint_generator/generate_clarification_questions.json ===
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

```
# Context Component Usage

## Importing

```python
from recipe_executor.context import Context
```

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
```

## Conclusion

Creating effective component specifications and documentation is crucial for enabling AI-assisted code generation in a modular architecture. By following these guidelines, you can create clear, comprehensive blueprints that allow for reliable and predictable implementation of each building block in your system.

Remember that the goal is to provide sufficient information for independent implementation while maintaining compatibility with the overall system architecture. When specifications and documentation work together effectively, they create a foundation for an efficient, adaptable development process that leverages AI capabilities while preserving architectural integrity.


=== File: recipes/component_blueprint_generator/includes/templates/create_recipe_template.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/specs/{{component_id}}.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/docs/{{component_id}}.md",
      "artifact": "usage_doc",
      "optional": true
    },
    {
      "type": "read_file",
      "path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy",
      "optional": true
    },
    {
      "type": "read_file",
      "path": "recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "{{model|default:'openai:o3-mini'}}",
        "output_root": "{{output_root|default:'.'}}",
        "component_id": "{{component_id}}",
        "output_path": "{{target_project}}/{{component_id}}",
        "language": "{{language|default:'python'}}",
        "spec": "{{spec}}",
        "usage_doc": "{{usage_doc}}",
        "additional_content": "<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% if related_docs %}<RELATED_DOCS>\n{{related_docs}}\n</RELATED_DOCS>{% endif %}"
      }
    }
  ]
}


=== File: recipes/component_blueprint_generator/includes/templates/doc_template.md ===
# {{component_name}} Component Usage

## Importing

```python
from {{module_path}} import {{component_name}}
```

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


=== File: recipes/component_blueprint_generator/includes/templates/edit_recipe_template.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "{{target_project}}/{{component_id}}.py",
      "artifact": "existing_code",
      "optional": true
    },
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/specs/{{component_id}}.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "{{project_recipe_path}}/docs/{{component_id}}.md",
      "artifact": "usage_doc",
      "optional": true
    },
    {
      "type": "read_file",
      "path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy",
      "optional": true
    },
    {
      "type": "read_file",
      "path": "recipes/component_blueprint_generator/includes/MODULAR_DESIGN_PHILOSOPHY.md",
      "artifact": "modular_design_philosophy",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "{{model|default:'openai:o3-mini'}}",
        "output_root": "{{output_root|default:'.'}}",
        "component_id": "{{component_id}}",
        "output_path": "{{target_project}}/{{component_id}}",
        "language": "{{language|default:'python'}}",
        "spec": "{{spec}}",
        "usage_doc": "{{usage_doc}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n{% if related_docs %}<RELATED_DOCS>\n{{related_docs}}\n</RELATED_DOCS>{% endif %}"
      }
    }
  ]
}


=== File: recipes/component_blueprint_generator/includes/templates/spec_template.md ===
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


=== File: recipes/component_blueprint_generator/recipes/create_doc.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/component_blueprint_generator/includes/templates/doc_template.md",
      "artifact": "doc_template"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer creating component documentation. Based on the component specification and information, create comprehensive usage documentation following the template structure.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nModule Path: {{module_path|default:''}}\nComponent Type: {{component_type|default:''}}\n\nDocumentation Template:\n{{doc_template}}\n\nUse the following guides for context:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\nIMPORTANT GUIDELINES:\n1. Create complete, detailed documentation for the component\n2. Include clear examples, method documentation, and integration guidance\n3. Within the documentation, use the component_id (\"{{component_id}}\") as the base name for all classes, modules, and file references unless explicitly overridden in the candidate spec\n4. Format your response as a FileGenerationResult with a single file named \"{{component_id}}.md\"\n\nDo not include the component name or other text in the filename - it must be exactly \"{{component_id}}.md\".",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_doc"
    },
    {
      "type": "write_file",
      "artifact": "generated_doc",
      "root": "{{output_root|default:'output'}}/{{target_project}}/docs"
    }
  ]
}


=== File: recipes/component_blueprint_generator/recipes/create_recipes.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/component_blueprint_generator/includes/templates/create_recipe_template.json",
      "artifact": "create_recipe_template"
    },
    {
      "type": "read_file",
      "path": "recipes/component_blueprint_generator/includes/templates/edit_recipe_template.json",
      "artifact": "edit_recipe_template"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer creating recipe files for component generation and editing. Based on the component specification and template recipes, create the final recipe files.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nTarget Project: {{target_project}}\nProject Recipe Path: {{project_recipe_path}}\n\nCreate Recipe Template:\n{{create_recipe_template}}\n\nEdit Recipe Template:\n{{edit_recipe_template}}\n\n# IMPORTANT GUIDELINES\n\n1. Use the templates as your starting point and maintain their overall structure\n\n2. For additional file includes and related docs:\n   - Analyze the component specification to identify related components or documentation it might need\n   - Include read_file steps for any relevant documents (like utils_docs for a component that uses utilities)\n   - Format additional content using XML-style tags (like <CONTEXT_DOCS>content</CONTEXT_DOCS>)\n   - Follow the pattern seen in executor_create.json, llm_create.json, etc.\n\n3. For context overrides:\n   - Keep all existing context variables provided in the template\n   - Add component-specific variables as needed\n   - Use the pattern: \"additional_content\": \"<TAG_NAME>\\n{{artifact_name}}\\n</TAG_NAME>\"\n\n4. Naming and paths:\n   - Use exactly '{{component_id}}_create.json' and '{{component_id}}_edit.json' for filenames\n   - Ensure all paths use correct variables: {{project_recipe_path}}, {{component_id}}, etc.\n\nFormat your response as a FileGenerationResult with two files:\n1. '{{component_id}}_create.json' - The create recipe\n2. '{{component_id}}_edit.json' - The edit recipe",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "recipe_files"
    },
    {
      "type": "write_file",
      "artifact": "recipe_files",
      "root": "{{output_root|default:'output'}}/{{target_project}}/recipes"
    }
  ]
}


=== File: recipes/component_blueprint_generator/recipes/create_spec.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/component_blueprint_generator/includes/templates/spec_template.md",
      "artifact": "spec_template"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer creating a formal component specification. Based on the candidate specification and component information, create a detailed specification document following the template structure.\n\nCandidate Specification:\n{{candidate_spec}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nModule Path: {{module_path|default:''}}\nComponent Type: {{component_type|default:''}}\nKey Dependencies: {{key_dependencies|default:''}}\n\nSpecification Template:\n{{spec_template}}\n\nUse the following guides for context:\n<SPEC_DOC_GUIDE>\n{{spec_doc_guide}}\n</SPEC_DOC_GUIDE>\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\n<MODULAR_DESIGN_PHILOSOPHY>\n{{modular_design_philosophy}}\n</MODULAR_DESIGN_PHILOSOPHY>\n\nIMPORTANT GUIDELINES:\n1. Create a complete, detailed specification for the component\n2. Within the specification, use the component_id (\"{{component_id}}\") as the base name for all classes, modules, and file references unless explicitly overridden in the candidate spec\n3. Format your response as a FileGenerationResult with a single file named \"{{component_id}}.md\"\n\nDo not include the component name or other text in the filename - it must be exactly \"{{component_id}}.md\".",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_spec"
    },
    {
      "type": "write_file",
      "artifact": "generated_spec",
      "root": "{{output_root|default:'output'}}/{{target_project}}/specs"
    }
  ]
}


=== File: recipes/component_blueprint_generator/recipes/finalize_blueprint.json ===
{
  "steps": [
    {
      "type": "generate",
      "prompt": "You are an expert developer finalizing a component blueprint. Review all the generated artifacts and create a summary report that describes what has been created and how to use these artifacts to generate the component.\n\nComponent Specification:\n{{generated_spec}}\n\nComponent Documentation:\n{{generated_doc}}\n\nComponent Recipe Files:\n{{recipe_files}}\n\nComponent ID: {{component_id}}\nComponent Name: {{component_name}}\nTarget Project: {{target_project}}\n\nCreate a summary report as a properly formatted markdown file with the title '{{component_id}}_blueprint_summary.md' that includes:\n1. An overview of the component\n2. A list of all generated files with their locations\n3. Instructions for using the recipes to generate the component\n4. Any special considerations or next steps\n\nThis report should serve as a guide for someone who wants to use these blueprint files to generate the actual component code.\n\nFormat your response as a FileGenerationResult with a single file named '{{component_id}}_blueprint_summary.md'.",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "formatted_summary"
    },
    {
      "type": "write_file",
      "artifact": "formatted_summary",
      "root": "{{output_root|default:'output'}}/{{target_project}}"
    }
  ]
}


