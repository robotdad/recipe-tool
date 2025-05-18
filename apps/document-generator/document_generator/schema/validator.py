"""
Schema validation utilities for outline JSON.
"""
import json
from pathlib import Path

import jsonschema
from jsonschema import validate, ValidationError

_SCHEMA_PATH = Path(__file__).parent / "outline_schema.json"

def validate_outline(data: dict) -> None:
    """
    Validate outline data against the JSON schema.
    Raises jsonschema.ValidationError on failure.
    """
    schema_text = _SCHEMA_PATH.read_text()
    schema = json.loads(schema_text)
    validate(instance=data, schema=schema)