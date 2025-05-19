"""Integration tests for the Recipe Executor app."""

import json
import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from recipe_executor_app.app import create_app
from recipe_executor_app.core import RecipeExecutorCore


@pytest.mark.asyncio
async def test_execute_recipe_integration():
    """Test integration between core and executor."""
    # Create a simple recipe
    recipe_json = {"steps": [{"type": "read_files", "config": {"path": "test_file.txt", "content_key": "content"}}]}

    # Create a temporary file with the recipe
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump(recipe_json, f)
        recipe_path = f.name

    try:
        # Create a test file referenced by the recipe
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
            f.write("Test content")
            test_file_path = f.name

        try:
            # Mock the executor to return a specific context
            with (
                patch("recipe_executor.executor.Executor.execute", new_callable=AsyncMock) as mock_execute,
                patch("recipe_executor_app.utils.resolve_path", return_value=test_file_path),
            ):
                # Create the core
                core = RecipeExecutorCore()

                # Execute the recipe
                result = await core.execute_recipe(recipe_path, None, "key1=value1")

                # Verify that the executor was called
                mock_execute.assert_called_once()

                # Verify the result has the expected keys
                assert "formatted_results" in result
                assert "raw_json" in result
                assert "debug_context" in result

        finally:
            # Clean up the test file
            os.unlink(test_file_path)

    finally:
        # Clean up the recipe file
        os.unlink(recipe_path)


@pytest.mark.asyncio
async def test_load_example_integration():
    """Test integration between core and example loading."""
    # Create a simple recipe
    recipe_json = {
        "name": "Test Recipe",
        "description": "A test recipe",
        "steps": [{"type": "read_files", "config": {"path": "test_file.txt", "content_key": "content"}}],
    }

    # Create a temporary file with the recipe
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump(recipe_json, f)
        recipe_path = f.name

    try:
        # Mock the path resolution
        with (
            patch("recipe_executor_app.core.get_repo_root", return_value="/repo"),
            patch("os.path.abspath", return_value=recipe_path),
            patch("os.path.exists", return_value=True),
            patch("recipe_executor_app.core.read_file", return_value=json.dumps(recipe_json)),
        ):
            # Create the core
            core = RecipeExecutorCore()

            # Load the recipe
            result = await core.load_recipe(recipe_path)

            # Verify the result has the expected keys
            assert "recipe_content" in result
            assert "structure_preview" in result

            # Verify the content matches the recipe
            assert json.loads(result["recipe_content"]) == recipe_json

            # Verify the preview contains the recipe name and description
            assert "Test Recipe" in result["structure_preview"]
            assert "A test recipe" in result["structure_preview"]

    finally:
        # Clean up the recipe file
        os.unlink(recipe_path)


def test_app_creation_integration():
    """Test integration between app, core, and UI components."""
    # Mock the UI building
    with patch("recipe_executor_app.app.create_executor_block") as mock_create_executor_block:
        # Create the app
        create_app()

        # Verify that the create_executor_block was called
        mock_create_executor_block.assert_called_once()

        # Verify that the argument to create_executor_block is a RecipeExecutorCore instance
        assert isinstance(mock_create_executor_block.call_args[0][0], RecipeExecutorCore)
