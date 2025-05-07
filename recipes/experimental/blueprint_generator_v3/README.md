# Instructions for Testing the Blueprint Generator v3

This version of the Blueprint Generator is patterned after a prior version that was used to create an MVP for a platform service, but was previously stitched together with a bit of glue code. The goal of this version is to create a pure recipe version that can be used to generate blueprints for various projects.

## Setup Example

The following instructions will guide you through setting up a test project for the Blueprint Generator. This example uses a simplified Task Manager API specification to demonstrate the process. Replace the example with your own project specifications as needed.

1. Create a test directory structure:

   ```bash
   mkdir -p blueprint_test/{input,output}
   ```

2. Place high-level specification files in the `input` directory.

   ```bash
   # Create a sample Task Manager API specification
   nano blueprint_test/input/task_manager_spec.md
   ```

3. Make sure you have the necessary AI context files:
   ```bash
   # Ensure these files exist
   ls ai_context/COMPONENT_DOCS_SPEC_GUIDE.md
   ls ai_context/IMPLEMENTATION_PHILOSOPHY.md
   ls ai_context/MODULAR_DESIGN_PHILOSOPHY.md
   ```

## Run the Blueprint Generator

```bash
# From the repo root, run the blueprint generator with the test project
recipe-tool --execute recipes/experimental/blueprint_generator_v3/build.json \
  project_spec=blueprint_test/input/task_manager_spec.md \
  output_dir=blueprint_test/output/blueprint_generator_v3 \
  model=openai/o4-mini
```

## Expected Process Flow

1. **Initial Analysis**: The system should analyze the Task Manager API spec and determine it needs to be split into multiple components.

2. **Component Splitting**: It should identify approximately 4-5 components (authentication, task management, notifications, reporting).

3. **Clarification Cycle**: Some components will likely need clarification questions.

4. **Human Review**: At least one component might need human review.

5. **Blueprint Generation**: For components that pass evaluation, blueprints should be generated.

## Testing Human Review Process

When a component needs human review:

1. Check the `blueprint_test/output/human_review` directory for instructions.

2. Create a revised specification addressing the issues.

3. Run the process_human_review recipe:
   ```bash
   recipe-tool --execute recipes/experimental/blueprint_generator_v3/build.json \
     project_spec=blueprint_test/input/task_manager_spec.md \
     output_dir=blueprint_test/output \
     process_review=component_id \
     review_path=path/to/your/revised/spec.md \
     model=openai/o4-mini
   ```

## Check Progress

Throughout the process, you can monitor:

- `blueprint_test/output/status/project_status.json` for overall progress
- `blueprint_test/output/status/*_status.json` for individual component status
- `blueprint_test/output/analysis` for project analysis results
- `blueprint_test/output/clarification` for Q&A cycles
- `blueprint_test/output/evaluation` for evaluation results
- `blueprint_test/output/human_review` for human review instructions
- `blueprint_test/output/blueprints` for final blueprints

This test project is designed to exercise all parts of the blueprint generator while remaining small enough to process efficiently.
