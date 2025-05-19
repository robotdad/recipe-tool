"""Tests for the core module of the recipe_tool_app package."""

import json
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest


@pytest.fixture
def mock_executor():
    """Create a mock executor."""
    executor = AsyncMock()
    executor.execute = AsyncMock()
    return executor


@pytest.fixture
def core_instance(mock_executor):
    """Create a RecipeToolCore instance with a mock executor."""
    from recipe_tool_app.core import RecipeToolCore

    return RecipeToolCore(executor=mock_executor)


@pytest.mark.asyncio
@patch("recipe_tool_app.core.prepare_context")
async def test_execute_recipe_file(mock_prepare_context, core_instance, mock_executor):
    """Test executing a recipe from a file."""
    # Setup
    mock_context = MagicMock()
    mock_context.dict.return_value = {"result": "Test result", "output": "Test output"}
    mock_prepare_context.return_value = ({}, mock_context)

    # Execute
    result = await core_instance.execute_recipe(recipe_file="test.json", recipe_text=None, context_vars=None)

    # Assert
    assert mock_executor.execute.called
    assert mock_executor.execute.call_args[0][0] == "test.json"
    assert "formatted_results" in result
    assert "raw_json" in result
    assert "debug_context" in result
    assert "Test result" in result["formatted_results"]
    assert "Test output" in result["formatted_results"]


@pytest.mark.asyncio
@patch("recipe_tool_app.core.prepare_context")
async def test_execute_recipe_text(mock_prepare_context, core_instance, mock_executor):
    """Test executing a recipe from text."""
    # Setup
    mock_context = MagicMock()
    mock_context.dict.return_value = {"result": "Test result", "output": "Test output"}
    mock_prepare_context.return_value = ({}, mock_context)
    recipe_text = '{"steps": []}'

    # Execute
    result = await core_instance.execute_recipe(recipe_file=None, recipe_text=recipe_text, context_vars=None)

    # Assert
    assert mock_executor.execute.called
    assert mock_executor.execute.call_args[0][0] == recipe_text
    assert "formatted_results" in result
    assert "raw_json" in result
    assert "Test result" in result["formatted_results"]
    assert "Test output" in result["formatted_results"]


@pytest.mark.asyncio
@patch("recipe_tool_app.core.prepare_context")
async def test_execute_recipe_no_input(mock_prepare_context, core_instance, mock_executor):
    """Test executing a recipe with no input."""
    # Setup
    mock_prepare_context.return_value = ({}, MagicMock())

    # Execute
    result = await core_instance.execute_recipe(recipe_file=None, recipe_text=None, context_vars=None)

    # Assert
    assert not mock_executor.execute.called
    assert "Error" in result["formatted_results"]
    assert "No recipe provided" in result["formatted_results"]


@pytest.mark.asyncio
@patch("recipe_tool_app.core.prepare_context")
@patch("recipe_tool_app.core.extract_recipe_content")
@patch("recipe_tool_app.core.os")
@patch("recipe_tool_app.utils.resolve_path")
@patch("recipe_tool_app.utils.get_repo_root")
async def test_create_recipe_successful(
    mock_get_repo_root, mock_resolve_path, mock_os, mock_extract, mock_prepare_context, core_instance, mock_executor
):
    """Test creating a recipe successfully."""
    # Setup - Make the os.path.exists check pass
    mock_os.path.exists.return_value = True
    mock_os.path.join.return_value = "/test/path/create.json"
    mock_os.path.dirname.return_value = "/test/path"
    mock_os.path.normpath.return_value = "/test/path/create.json"
    mock_os.getcwd.return_value = "/test/path"
    mock_os.times.return_value = MagicMock(elapsed=1.0)

    # Setup - Context preparation and extraction
    mock_context = MagicMock()
    mock_context.dict.return_value = {"generated_recipe": {"content": '{"name": "Test Recipe", "steps": []}'}}
    mock_prepare_context.return_value = ({}, mock_context)
    mock_get_repo_root.return_value = "/test/repo"
    mock_extract.return_value = '{"name": "Test Recipe", "steps": []}'

    # Directly set up the context dict to return
    mock_recipe_text = '{"name": "Test Recipe", "steps": []}'
    mock_context.dict.return_value = {"generated_recipe": mock_recipe_text}

    # Make sure extract returns the recipe content when called after execute
    with patch("recipe_tool_app.utils.parse_recipe_json") as mock_parse:
        mock_parse.return_value = {"name": "Test Recipe", "steps": []}

        # Need to make extract_recipe_content work in core module too, not just as a parameter patch
        with patch("recipe_tool_app.core.extract_recipe_content", return_value=mock_recipe_text):
            # Mock file reading in case it tries to read from file
            with patch("builtins.open", mock_open(read_data=mock_recipe_text)):
                # Also patch the output directory to exist
                with patch("os.makedirs"):
                    # Execute with text input
                    result = await core_instance.create_recipe(
                        idea_text="Create a test recipe", idea_file=None, reference_files=None, context_vars=None
                    )

    # Assert
    assert mock_executor.execute.called
    assert "recipe_json" in result
    assert "structure_preview" in result
    assert "Test Recipe" in result["structure_preview"]


@pytest.mark.asyncio
@patch("recipe_tool_app.core.tempfile.mkstemp")
@patch("recipe_tool_app.core.os")
async def test_create_recipe_with_temp_file(mock_os, mock_mkstemp, core_instance):
    """Test the temporary file creation and cleanup during recipe creation."""
    # Setup
    mock_fd = 123
    mock_temp_path = "/tmp/test_temp_file.md"
    mock_mkstemp.return_value = (mock_fd, mock_temp_path)

    mock_file = MagicMock()
    mock_os.fdopen.return_value.__enter__.return_value = mock_file
    mock_os.path.exists.return_value = True

    # We'll need to patch many functions to avoid execution
    with patch("recipe_tool_app.core.prepare_context") as mock_prepare:
        mock_prepare.return_value = ({}, MagicMock())
        with patch.object(core_instance, "executor") as mock_exec:
            mock_exec.execute = AsyncMock()
            with patch("recipe_tool_app.core.extract_recipe_content") as mock_extract:
                mock_extract.return_value = None

                # Execute with text but without a file
                await core_instance.create_recipe(
                    idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                )

    # Assert temp file operations
    mock_os.fdopen.assert_called_with(mock_fd, "w")
    mock_file.write.assert_called_with("Test idea")
    mock_os.unlink.assert_called_with(mock_temp_path)


@pytest.mark.asyncio
@patch("recipe_tool_app.utils.extract_recipe_content")
@patch("recipe_tool_app.utils.parse_recipe_json")
async def test_recipe_preview_generation(mock_parse, mock_extract, core_instance):
    """Test the generation of recipe structure previews."""
    # Setup a mock recipe JSON
    recipe_json = {
        "name": "Test Recipe",
        "description": "A test recipe",
        "steps": [
            {"type": "read_files", "config": {"description": "Read test file"}},
            {"type": "generate", "description": "Generate content"},
        ],
    }

    # Make the extraction return a valid recipe string
    mock_extract.return_value = json.dumps(recipe_json)
    mock_parse.return_value = recipe_json

    # Create patches to avoid execution
    with patch("recipe_tool_app.core.prepare_context") as mock_prepare:
        mock_context = MagicMock()
        recipe_text = json.dumps(recipe_json)
        # Make sure context.dict() returns a proper value with generated_recipe
        mock_context.dict.side_effect = [
            # First context dict call in the create_recipe function
            {},
            # This will be returned after execution when processing results
            {"generated_recipe": recipe_text},
        ]
        mock_prepare.return_value = ({}, mock_context)

        with patch.object(core_instance, "executor") as mock_exec:
            mock_exec.execute = AsyncMock()
            with patch("recipe_tool_app.core.os") as mock_os:
                mock_os.path.exists.return_value = True
                mock_os.times.return_value = MagicMock(elapsed=1.0)
                mock_os.path.join.return_value = "/test/path"
                mock_os.path.dirname.return_value = "/test"
                mock_os.path.normpath.return_value = "/test/path"

                # We need to make sure extract_recipe_content returns the recipe when called within core.create_recipe
                # This patch intercepts the call after execute() returns
                with patch("recipe_tool_app.core.extract_recipe_content") as core_extract:
                    core_extract.return_value = recipe_text

                    # Mock out the output directory file check
                    with patch("builtins.open", mock_open(read_data=recipe_text)):
                        # Execute
                        result = await core_instance.create_recipe(
                            idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                        )

    # Assert preview content
    assert "recipe_json" in result
    assert "structure_preview" in result

    # Verify expected content is present
    preview = result["structure_preview"]

    assert "Test Recipe" in preview
    assert "A test recipe" in preview
    assert "Steps" in preview
    assert "2" in preview
    assert "read_files" in preview
    assert "generate" in preview

    # Verify it has the test descriptions
    assert "Read test file" in preview
    assert "Generate content" in preview
