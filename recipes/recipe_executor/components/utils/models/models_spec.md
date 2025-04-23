# Models-Utility Component Specification

## Purpose

Provide reusable helpers for Pydantic models, such as conversion from JSON-Schema definitions to fully-typed
`pydantic.BaseModel` subclasses.

## Core Requirements

- `json_schema_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]`
  Converts any root-level **object** or **array** (incl. nested structures & `"required"`) into a `BaseModel` created with `pydantic.create_model`.
- Support JSON-Schema primitive types: `"string"`, `"integer"`, `"number"`, `"boolean"`.
- Support compound types: `"object"`, `"array"` (alias `"list"`).
- Unknown / unsupported `"type"` values fall back to `typing.Any`.
- Returns the Python type (or nested model) **and** the default/ellipsis to pass to `create_model`.
- Stateless, synchronous, no logging, no I/O.
- Raise `ValueError` on malformed schemas (e.g., missing `"type"`).

## Implementation Considerations

- Use **`pydantic.create_model`** exactly once per generated model.
- Generate deterministic nested-model names (`JsonSchemaObj_1`, `JsonSchemaObj_2`, …) to avoid collisions.

## Component Dependencies

### Internal Components

- **None**

### External Libraries

- **pydantic** – (Required) Provides `BaseModel` and `create_model`.
- **typing** – (Required) `Any`, `List`, `Tuple`, `Type`.

### Configuration Dependencies

None

## Logging

None

## Error Handling

- Raise **`ValueError`** with a clear message when the input schema is invalid or unsupported.

## Dependency Integration Considerations

None

## Output Files

- `models/models.py`
