import pytest

from document_generator_app.schema.validator import validate_outline


@pytest.fixture
def minimal_outline():
    return {"title": "T", "general_instruction": "GI", "resources": [], "sections": []}


def test_validate_minimal_outline(minimal_outline):
    # Should not raise
    validate_outline(minimal_outline)


def test_validate_missing_field(minimal_outline):
    minimal_outline.pop("title")
    with pytest.raises(Exception):
        validate_outline(minimal_outline)
