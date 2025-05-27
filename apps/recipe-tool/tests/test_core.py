"""Tests for the core module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from recipe_tool_app.core import RecipeToolCore


@pytest.fixture
def mock_executor():
    """Create a mock executor."""
    executor = AsyncMock()
    executor.execute = AsyncMock()
    return executor


@pytest.fixture
def core_instance(mock_executor):
    """Create a RecipeToolCore instance with a mock executor."""
    return RecipeToolCore(executor=mock_executor)


@pytest.mark.asyncio
async def test_create_recipe_from_text(core_instance, mock_executor):
    """Test creating a recipe from text."""
    recipe_json = '{"name": "Test Recipe", "steps": []}'

    # Mock create_temp_file
    with patch("recipe_tool_app.core.create_temp_file") as mock_create_temp:
        mock_create_temp.return_value = ("/tmp/idea.md", MagicMock())

        # Mock os operations
        with patch("recipe_tool_app.core.os") as mock_os:
            mock_os.path.exists.return_value = True
            mock_os.times.return_value = MagicMock(elapsed=1.0)
            mock_os.makedirs.return_value = None

            # Mock Context
            with patch("recipe_tool_app.core.Context") as mock_context_class:
                mock_context = MagicMock()
                mock_context.dict.return_value = {"generated_recipe": recipe_json}
                mock_context_class.return_value = mock_context

                # Execute
                result = await core_instance.create_recipe(
                    idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                )

                # Verify
                assert mock_executor.execute.called
                assert "recipe_json" in result
                assert result["recipe_json"] == recipe_json


@pytest.mark.asyncio
async def test_create_recipe_from_file(core_instance, mock_executor):
    """Test creating a recipe from a file."""
    recipe_json = '{"name": "Test Recipe", "steps": []}'

    # Mock os operations
    with patch("recipe_tool_app.core.os") as mock_os:
        mock_os.path.exists.return_value = True
        mock_os.times.return_value = MagicMock(elapsed=1.0)
        mock_os.makedirs.return_value = None

        # Mock Context
        with patch("recipe_tool_app.core.Context") as mock_context_class:
            mock_context = MagicMock()
            mock_context.dict.return_value = {"generated_recipe": recipe_json}
            mock_context_class.return_value = mock_context

            # Execute
            result = await core_instance.create_recipe(
                idea_text="", idea_file="/path/to/idea.md", reference_files=None, context_vars=None
            )

            # Verify
            assert mock_executor.execute.called
            assert "recipe_json" in result
            assert result["recipe_json"] == recipe_json


@pytest.mark.asyncio
async def test_create_recipe_no_input(core_instance):
    """Test creating a recipe with no input."""
    result = await core_instance.create_recipe(idea_text="", idea_file=None, reference_files=None, context_vars=None)

    assert "recipe_json" in result
    assert result["recipe_json"] == ""
    assert "Error" in result["structure_preview"]
    assert "No idea provided" in result["structure_preview"]


@pytest.mark.asyncio
async def test_create_recipe_with_error(core_instance, mock_executor):
    """Test creating a recipe that raises an error."""
    # Mock executor to raise error
    mock_executor.execute.side_effect = ValueError("Test error")

    # Mock create_temp_file
    with patch("recipe_tool_app.core.create_temp_file") as mock_create_temp:
        mock_create_temp.return_value = ("/tmp/idea.md", MagicMock())

        # Mock os operations
        with patch("recipe_tool_app.core.os") as mock_os:
            mock_os.path.exists.return_value = True
            mock_os.makedirs.return_value = None

            # Mock Context
            with patch("recipe_tool_app.core.Context") as mock_context_class:
                mock_context = MagicMock()
                mock_context_class.return_value = mock_context

                # Execute
                result = await core_instance.create_recipe(
                    idea_text="Test idea", idea_file=None, reference_files=None, context_vars=None
                )

                # Verify error handling
                assert "recipe_json" in result
                assert result["recipe_json"] == ""
                assert "Error" in result["structure_preview"]
                assert "Test error" in result["structure_preview"]


def test_find_recipe_output():
    """Test find_recipe_output function."""
    from recipe_tool_app.recipe_processor import find_recipe_output

    recipe_json = '{"name": "Test Recipe"}'

    # Test 1: Recipe in context
    context = {"generated_recipe": recipe_json}
    result = find_recipe_output(context)
    assert result == recipe_json

    # Test 2: Recipe as list
    context = {"generated_recipe": [{"content": recipe_json}]}
    result = find_recipe_output(context)
    assert result == recipe_json

    # Test 3: Recipe as dict with content
    context = {"generated_recipe": {"content": recipe_json}}
    result = find_recipe_output(context)
    assert result == recipe_json

    # Test 4: Recipe in file
    with patch("recipe_tool_app.recipe_processor.os.path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("recipe_tool_app.recipe_processor.read_file") as mock_read:
            mock_read.return_value = recipe_json
            context = {"output_root": "/output", "target_file": "recipe.json"}
            result = find_recipe_output(context)
            assert result == recipe_json


def test_generate_preview():
    """Test generate_preview function."""
    from recipe_tool_app.recipe_processor import generate_preview

    recipe = {
        "name": "Test Recipe",
        "description": "Test description",
        "steps": [
            {"type": "read", "config": {"description": "Read files"}},
            {"type": "write", "description": "Write output"},
        ],
    }

    preview = generate_preview(recipe, 1.23)

    assert "Recipe Structure" in preview
    assert "Test Recipe" in preview
    assert "Test description" in preview
    assert "**Steps**: 2" in preview
    assert "read" in preview
    assert "write" in preview
    assert "Read files" in preview
    assert "Write output" in preview
