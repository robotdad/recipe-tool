from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, create_model


def json_schema_to_pydantic_model(schema: Dict[str, Any], model_name: str = "SchemaModel") -> Type[BaseModel]:
    """
    Convert a JSON-Schema dictionary into a dynamic Pydantic model.

    Args:
        schema: A valid JSON-Schema fragment describing either an object or array.
        model_name: Name given to the generated model class.

    Returns:
        A subclass of `pydantic.BaseModel` suitable for validation & serialization.

    Raises:
        ValueError: If the schema is invalid or unsupported.
    """
    # Counter for nested object model names
    counter: Dict[str, int] = {"count": 0}

    def _parse(sub_schema: Dict[str, Any]) -> Any:
        if not isinstance(sub_schema, dict):
            raise ValueError(f"Invalid schema fragment: {sub_schema}")
        if "type" not in sub_schema:
            raise ValueError("Schema must have a 'type' field")
        schema_type = sub_schema["type"]

        # Primitive types
        if schema_type == "string":
            return str
        if schema_type == "integer":
            return int
        if schema_type == "number":
            return float
        if schema_type == "boolean":
            return bool

        # Object type
        if schema_type == "object":
            counter["count"] += 1
            nested_name = f"JsonSchemaObj_{counter['count']}"
            properties = sub_schema.get("properties", {})
            if not isinstance(properties, dict):
                raise ValueError("'properties' must be an object mapping")
            required_props = sub_schema.get("required", [])
            if not isinstance(required_props, list):
                raise ValueError("'required' must be a list of property names")
            fields: Dict[str, Any] = {}
            for prop_name, prop_schema in properties.items():
                prop_type = _parse(prop_schema)
                if prop_name in required_props:
                    fields[prop_name] = (prop_type, ...)
                else:
                    fields[prop_name] = (Optional[prop_type], None)
            return create_model(nested_name, **fields)  # type: ignore

        # Array type
        if schema_type in ("array", "list"):
            items_schema = sub_schema.get("items")
            if items_schema is None:
                raise ValueError("'items' field is required for array types")
            item_type = _parse(items_schema)
            return List[item_type]

        # Fallback for unknown types
        return Any

    # Top-level handling
    if not isinstance(schema, dict) or "type" not in schema:
        raise ValueError("Top-level schema must be a dict with a 'type' field")
    top_type = schema["type"]

    # Root object model
    if top_type == "object":
        props = schema.get("properties", {})
        if not isinstance(props, dict):
            raise ValueError("'properties' must be an object mapping")
        required = schema.get("required", [])
        if not isinstance(required, list):
            raise ValueError("'required' must be a list of property names")
        root_fields: Dict[str, Any] = {}
        for name, subsch in props.items():
            field_type = _parse(subsch)
            if name in required:
                root_fields[name] = (field_type, ...)
            else:
                root_fields[name] = (Optional[field_type], None)
        return create_model(model_name, **root_fields)  # type: ignore

    # Root array model as a root model
    if top_type in ("array", "list"):
        items = schema.get("items")
        if items is None:
            raise ValueError("'items' field is required for array types")
        item_type = _parse(items)
        # Use __root__ for root-level arrays
        return create_model(model_name, __root__=(List[item_type], ...))  # type: ignore

    raise ValueError("Root schema type must be 'object' or 'array'")
