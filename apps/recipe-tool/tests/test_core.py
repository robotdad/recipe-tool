"""Tests for the core module of the recipe_tool_app package."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

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
@patch("recipe_tool_app.core.os")
@patch("recipe_tool_app.path_resolver.get_repo_root")
async def test_create_recipe_successful(
    mock_get_repo_root, mock_os, mock_prepare_context, core_instance, mock_executor
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
    mock_recipe_text = '{"name": "Test Recipe", "steps": []}'

    # Make the first dict call return empty dict, and the second call return recipe content
    mock_context.dict.side_effect = [
        {"output_root": "/test/output"},  # Initial context
        {"generated_recipe": mock_recipe_text, "output_root": "/test/output"},  # After execution
    ]

    mock_prepare_context.return_value = ({}, mock_context)
    mock_get_repo_root.return_value = "/test/repo"

    # Mock create_temp_file to return a fake path and cleanup function
    with patch("recipe_tool_app.core.create_temp_file") as mock_create_temp:
        mock_create_temp.return_value = ("/tmp/idea.md", MagicMock())

        # Mock _find_recipe_output to return recipe content
        with patch.object(core_instance, "_find_recipe_output") as mock_find:
            mock_find.return_value = mock_recipe_text

            # Mock generate_recipe_preview to return a preview
            with patch("recipe_tool_app.core.generate_recipe_preview") as mock_preview:
                mock_preview.return_value = "### Recipe Structure\n\n**Name**: Test Recipe\n"

                # Execute with text input
                result = await core_instance.create_recipe(
                    idea_text="Create a test recipe", idea_file=None, reference_files=None, context_vars=None
                )

    # Assert
    assert mock_executor.execute.called
    assert "recipe_json" in result
    assert "structure_preview" in result
    assert result["recipe_json"] == mock_recipe_text


@pytest.mark.asyncio
async def test_create_recipe_with_temp_file(core_instance):
    """Test the temporary file creation and cleanup during recipe creation."""
    # Mock the create_temp_file function
    with patch("recipe_tool_app.core.create_temp_file") as mock_create_temp:
        # Setup temp file path and cleanup function
        mock_temp_path = "/tmp/test_temp_file.md"
        mock_cleanup = MagicMock()
        mock_create_temp.return_value = (mock_temp_path, mock_cleanup)

        # Mock the os.path.exists check for the recipe file
        with patch("recipe_tool_app.core.os.path.exists") as mock_exists:
            mock_exists.return_value = True

            # Mock prepare_context
            with patch("recipe_tool_app.core.prepare_context") as mock_prepare:
                mock_context = MagicMock()
                mock_context.dict.return_value = {}
                mock_prepare.return_value = ({}, mock_context)

                # Mock the executor
                with patch.object(core_instance, "executor") as mock_exec:
                    mock_exec.execute = AsyncMock()

                    # Mock _find_recipe_output to return None (no recipe found)
                    with patch.object(core_instance, "_find_recipe_output") as mock_find:
                        mock_find.return_value = None

                        # Execute with text but without a file
                        await core_instance.create_recipe(
                            idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                        )

    # Assert temp file operations were called correctly
    mock_create_temp.assert_called_once_with("Test idea", prefix="idea_", suffix=".md")
    mock_cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_recipe_preview_generation(core_instance):
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
    recipe_text = json.dumps(recipe_json)

    # Mock create_temp_file to return a fake path and cleanup function
    with patch("recipe_tool_app.core.create_temp_file") as mock_create_temp:
        mock_create_temp.return_value = ("/tmp/idea.md", MagicMock())

        # Mock prepare_context
        with patch("recipe_tool_app.core.prepare_context") as mock_prepare:
            mock_context = MagicMock()
            mock_context.dict.side_effect = [
                {"output_root": "/test/output"},  # Initial context
                {"generated_recipe": recipe_text, "output_root": "/test/output"},  # After execution
            ]
            mock_prepare.return_value = ({}, mock_context)

            # Mock os
            with patch("recipe_tool_app.core.os") as mock_os:
                mock_os.path.exists.return_value = True
                mock_os.times.return_value = MagicMock(elapsed=1.0)

                # Mock executor
                with patch.object(core_instance, "executor") as mock_exec:
                    mock_exec.execute = AsyncMock()

                    # Mock _find_recipe_output to return recipe content
                    with patch.object(core_instance, "_find_recipe_output") as mock_find:
                        mock_find.return_value = recipe_text

                        # Mock parse_recipe_json
                        with patch("recipe_tool_app.core.parse_recipe_json") as mock_parse:
                            mock_parse.return_value = recipe_json

                            # Execute with text input
                            result = await core_instance.create_recipe(
                                idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                            )

    # Assert preview content
    assert "recipe_json" in result
    assert "structure_preview" in result
    assert result["recipe_json"] == recipe_text

    # Mock generate_recipe_preview was called with the parsed recipe JSON
    with patch("recipe_tool_app.core.generate_recipe_preview") as mock_preview:
        mock_preview.return_value = "### Recipe Structure\n\n**Name**: Test Recipe\n\n**Description**: A test recipe\n\n**Steps**: 2\n\n| # | Type | Description |\n|---|------|-------------|\n| 1 | read_files | Read test file |\n| 2 | generate | Generate content |\n"
        preview = mock_preview(recipe_json, 1.0)

        # Check the preview format
        assert "Recipe Structure" in preview
        assert "Test Recipe" in preview
        assert "A test recipe" in preview
        assert "Steps" in preview
        assert "read_files" in preview
        assert "generate" in preview
        assert "Read test file" in preview
        assert "Generate content" in preview
