# Context Component Specification

## Purpose

The Context component is the shared state container for the Recipe Executor system. It provides a simple dictionary-like interface that steps use to store and retrieve data during recipe execution.

## Core Requirements

- Store and provide access to artifacts (data shared between steps)
- Maintain separate configuration values
- Support dictionary-like operations (get, set, iterate)
- Provide a clone() method that returns a deep copy of the context's current artifacts and configuration
- Ensure data isolation between different executions
- Follow minimalist design principles

## Implementation Considerations

- Use simple dictionary-based storage internally
- Copy input dictionaries to prevent external modification
- Implement a clone() method that returns a deep copy of the context's current state
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
- Support for merging multiple contexts
