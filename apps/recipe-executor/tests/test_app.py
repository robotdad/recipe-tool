"""Tests for the recipe_executor_app package."""

import json
from unittest.mock import patch, MagicMock


@patch("recipe_executor_app.app.Executor")
@patch("recipe_executor_app.app.init_logger")
def test_create_app(mock_logger, mock_executor):
    """Test that the app is created successfully."""
    # Setup mocks
    mock_logger.return_value = MagicMock()
    mock_executor.return_value = MagicMock()

    # Import here to use the patched modules
    from recipe_executor_app.app import create_app

    app = create_app()
    assert app is not None


def test_json_serialization_with_nonserializable():
    """Test JSON serialization with non-serializable objects."""
    # Create a test object that's not directly serializable
    class TestObject:
        def __str__(self):
            return "TestObject"
    
    test_obj = TestObject()
    test_dict = {"key1": "value1", "key2": test_obj}
    
    # Serialize using the default parameter
    json_str = json.dumps(test_dict, default=lambda o: str(o))
    
    # Parse back to verify
    parsed = json.loads(json_str)
    
    # Check that the string representation was used
    assert parsed["key1"] == "value1"
    assert parsed["key2"] == "TestObject"
