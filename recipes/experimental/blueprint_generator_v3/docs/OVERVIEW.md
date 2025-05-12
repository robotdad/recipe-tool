# Blueprint Generation Recipe Overview

The Blueprint Generation Recipe transforms abstract project specifications into concrete implementation plans through a structured, intelligent workflow. This recipe bridges the gap between high-level concepts and actionable development blueprints by methodically analyzing requirements, decomposing complex projects into manageable components, and refining specifications through iterative evaluation. By combining automated processing with targeted human intervention when necessary, the recipe ensures that even complex technical initiatives can be systematically broken down into well-defined, implementable components with clear dependencies and interfaces.

## Diagram

[Blueprint Generation Recipe Flow Diagram](DIAGRAM.md)

## Process Flow

1. **Project Analysis**: The recipe analyzes the project spec, incorporating context files, reference files, and the two philosophy files to determine if the project needs to be split into components. If no splitting is needed, it proceeds to process as a single component.

   - **Project Spec**: This is the main specification file that outlines the project requirements, passed in from the user.
   - **Context Files**: These files provide additional context and guidelines for the project, such as:
     - Vision documents, mission documents, and project charters
     - Architecture documents, API specifications, and technical specifications
     - Design documents such as data flow diagrams, sequence diagrams, and class diagrams
     - User stories, user journeys, and use cases
     - Acceptance criteria, user interface designs, and user experience designs
   - **Reference Files**: These files contain relevant information that aids in understanding how to use the external dependencies for the project, such as:
     - API documentation, SDK documentation, and library documentation
     - Code examples, tutorials, and sample projects
     - Best practices, design patterns, and coding standards
     - Configuration files, environment setup instructions, and deployment guides
     - Test cases, test plans, and test data
   - **Philosophy Files**: These are hard-coded:
     - `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
       - This file outlines the implementation philosophy for the project, including design principles, coding standards, and best practices.
     - `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
       - This file provides guidelines for modular design principles for success using LLM's to generate code in a modular and scalable way.
   - **Component Docs and Spec Guide**: These files are also hard-coded:
   - `ai_context/COMPONENT_DOCS_SPEC_GUIDE.md`
     - This file contains guidelines for creating the blueprint components - docs and spec files - used for determining what information is missing, evaluating specs, and ultimately generating the blueprint files.
   - Analyze each of the context files and reference files and create a list of their contents to be used in the analysis process. This list should include the file name, the type of file (context or reference), and a brief description of its contents so that they can be selectively paired up with the relevant modular components.

2. **Component Splitting**: For projects requiring splitting, the recipe identifies multiple components based on the analysis results.

   - The splitting process is guided by the context files, reference files, and philosophy files to ensure that each component is well-defined and manageable.
   - The recipe generates a list of components, each with its own specification.
   - After splitting, each component is also analyzed to determine if it needs further splitting. If so, the recipe will recursively split the components until they are small enough to be manageable, using the same context files, reference files, and philosophy files as before.

3. **Candidate Spec Generation**: For each identified component, the recipe generates a "candidate spec" using the result of the split analysis for that component, the original project spec, relevant context and reference files, and the philosophy files.

4. **Clarification Questions Generation**: The candidate spec is reviewed against the component docs and spec guidance documents to generate clarification questions for aspects needing additional information.

   - Since the modular design philosophy dictates that all modules should able to be built in isolation, the other components and even overall project spec are not included in this question generation process.

5. **Updated Spec Creation**: Using the clarification questions along with the candidate spec, project spec, context files, reference files, and philosophy files, the recipe creates an updated specification that addresses these questions.

6. **Specification Evaluation**: The updated candidate spec is evaluated against the component docs and spec guide to determine if it's ready for blueprint generation. As before, this evaluation is done in isolation, meaning that the other components and even the overall project spec are not included in this evaluation process.

   - Create a reubric for this evaluation based upon the component docs and spec guide.
   - The candidate spec is considered read if it passes with an above average score of 4.0 out of 5.0 averaged across all rubric categories, provided no category is below 3.0 out of 5.0.

7. **Revision Process**: If the specification is not ready and this is the first revision attempt, the recipe runs it through another clarification questions generation cycle. If it's already been through one revision, it generates clarification questions again but flags these for human review.

8. **Ready Component Handling**: Components with specifications that pass evaluation are marked as ready while the recipe completes processing all remaining components.

9. **Human Review Integration**: After all components have been processed (with up to two revision attempts each), any components needing human review cause the flow to pause. The user can review outstanding questions, create answer files, and feed these back into the recipe to update the relevant components.

   - Progress will never proceed past this point until the human review process is completed.
   - The human review process is designed to be iterative, allowing for multiple rounds of feedback and refinement until the components are ready for blueprint generation.

10. **Blueprint Generation Preparation**: Once all components have passing specifications, the recipe proceeds to the blueprint generation phase. This involves creating a blueprint for each component based on the passing candidate spec, project spec, relevant context and reference files, philosophy docs, and component docs/spec guide.

    - The recipe generates a list of all components that passed evaluation and are ready for blueprint generation.
    - It also creates a list of all context files and reference files, for each component, that will be included in the final blueprints.

11. **Dependency Analysis**: Each component is analyzed for dependencies, creating a dependency list to be included in the final blueprints.

12. **Individual Blueprint Generation**: The recipe loops through each component, generating individual blueprint files. Each blueprint incorporates the passing candidate spec, project spec, context files, reference files, philosophy docs, and component docs/spec guide to create a complete docs/spec pair for the component per the component docs/spec guide as the ultimate truth for the component.

This workflow ensures systematic decomposition of complex projects into well-specified components with clear implementation blueprints.
