"""Tests for the recipe_tool_app package."""

import json
from unittest.mock import MagicMock, patch


@patch("recipe_tool_app.app.init_logger")
@patch("recipe_tool_app.app.RecipeToolCore")
@patch("recipe_tool_app.app.build_ui")
def test_create_app(mock_build_ui, mock_core, mock_logger):
    """Test that the app is created successfully."""
    # Setup mocks
    mock_logger.return_value = MagicMock()
    mock_core.return_value = MagicMock()
    mock_build_ui.return_value = MagicMock()

    # Import here to use the patched modules
    from recipe_tool_app.app import create_app

    app = create_app()

    # Verify app creation process
    assert app is not None
    assert mock_core.called
    assert mock_build_ui.called
    mock_build_ui.assert_called_once_with(mock_core.return_value)


@patch("recipe_tool_app.app.argparse.ArgumentParser")
@patch("recipe_tool_app.app.create_app")
def test_main_with_args(mock_create_app, mock_arg_parser):
    """Test the main function with command line arguments."""
    # Setup mocks
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app

    # Mock ArgumentParser
    mock_parser = MagicMock()
    mock_arg_parser.return_value = mock_parser

    # Mock parse_args result
    args = MagicMock()
    args.host = "127.0.0.1"
    args.port = 8080
    args.no_mcp = True
    args.debug = True
    mock_parser.parse_args.return_value = args

    # Mock settings
    with patch("recipe_tool_app.app.settings") as mock_settings:
        # Execute main
        from recipe_tool_app.app import main

        main()

        # Verify settings were updated
        assert mock_settings.host == "127.0.0.1"
        assert mock_settings.port == 8080
        assert mock_settings.mcp_server is False
        assert mock_settings.debug is True

        # Verify app was launched
        assert mock_app.launch.called
        # Verify launch_kwargs were retrieved from settings
        assert mock_settings.to_launch_kwargs.called


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
