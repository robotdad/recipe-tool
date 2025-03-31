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
  --context component_path=/auth \
  --context output_root=output
```

### Expected Outputs

After running the full workflow, you should find these files in the `output` directory:

1. **Evaluation Report**: `auth_evaluation_summary.md` or `clarification_questions.md`
2. **Clarification Questions**: `auth_specification_clarification_questions.md`
3. **Blueprint Files**:
   - `specs/auth/auth.md` - Formal specification
   - `docs/auth/auth.md` - Usage documentation
   - `recipes/auth/create.json` - Recipe for creating the component
   - `recipes/auth/edit.json` - Recipe for editing the component
   - `auth_blueprint_summary.md` - Summary of the generated blueprint

### Next Steps

1. Review the evaluation and clarification questions
2. Improve the candidate specification based on the feedback
3. Regenerate the blueprint with the improved specification
4. Use the generated `create.json` recipe to implement the actual component:

```bash
python recipe_executor/main.py output/recipes/auth/create.json
```

#### 4. Implementing the Component Using Generated Files

After generating the blueprint, use the files in the `output` directory to implement the component:

```bash
# First, create the component using the generated recipe
python recipe_executor/main.py output/recipes/auth/create.json \
  --context output_root=src
```

This command will:

- Read the formal specification from `output/specs/auth/auth.md`
- Use the documentation from `output/docs/auth/auth.md` for guidance
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
python recipe_executor/main.py output/recipes/auth/edit.json \
  --context output_root=src
```

## Creating Your Own Examples

To create your own example candidate specifications:

1. Create a markdown file with your component specification
2. Place it in this examples directory
3. Follow the same workflow as described above, updating the paths as needed

The more detail you provide in your candidate specification, the more complete the generated blueprint will be. However, the system is designed to help identify gaps, so even incomplete specifications can be a good starting point.
