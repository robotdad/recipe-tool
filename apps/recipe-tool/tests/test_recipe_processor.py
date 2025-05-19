"""Tests for the recipe_processor module of the recipe_tool_app package."""

import json


from recipe_tool_app.recipe_processor import (
    extract_recipe_content,
    format_context_for_display,
    format_recipe_results,
    generate_recipe_preview,
    parse_recipe_json,
)


def test_parse_recipe_json_valid():
    """Test parse_recipe_json with valid JSON string."""
    # Test with valid JSON
    valid_json = '{"name": "Test Recipe", "steps": []}'
    result = parse_recipe_json(valid_json)

    # Assertions
    assert isinstance(result, dict)
    assert result["name"] == "Test Recipe"
    assert result["steps"] == []


def test_parse_recipe_json_dict_input():
    """Test parse_recipe_json with dictionary input."""
    # Test with dict input (should be converted to string)
    dict_input = {"name": "Test Recipe", "steps": []}
    result = parse_recipe_json(dict_input)

    # Assertions
    assert isinstance(result, dict)
    assert result["name"] == "Test Recipe"
    assert result["steps"] == []


def test_parse_recipe_json_empty():
    """Test parse_recipe_json with empty input."""
    # Test with empty input
    result = parse_recipe_json("")

    # Assertions
    assert isinstance(result, dict)
    assert result == {}


def test_extract_recipe_content_string():
    """Test extract_recipe_content with a string input."""
    # Test with string
    result = extract_recipe_content('{"name": "Test Recipe"}')

    # Assertions
    assert result == '{"name": "Test Recipe"}'


def test_extract_recipe_content_list():
    """Test extract_recipe_content with a list input."""
    # Test with list containing dict with content
    input_list = [{"content": '{"name": "Test Recipe"}', "path": "test.json"}]
    result = extract_recipe_content(input_list)

    # Assertions
    assert result == '{"name": "Test Recipe"}'


def test_extract_recipe_content_dict():
    """Test extract_recipe_content with a dictionary input."""
    # Test with dict with content
    input_dict = {"content": '{"name": "Test Recipe"}', "path": "test.json"}
    result = extract_recipe_content(input_dict)

    # Assertions
    assert result == '{"name": "Test Recipe"}'


def test_extract_recipe_content_none():
    """Test extract_recipe_content with invalid inputs."""
    # Test with various invalid inputs
    assert extract_recipe_content(None) is None
    assert extract_recipe_content([]) is None
    assert extract_recipe_content([{"no_content": "value"}]) is None
    assert extract_recipe_content({"no_content": "value"}) is None


def test_generate_recipe_preview():
    """Test generate_recipe_preview function."""
    # Test recipe JSON
    recipe_json = {
        "name": "Test Recipe",
        "description": "A test recipe",
        "steps": [
            {"type": "read_files", "config": {"description": "Read test file"}},
            {"type": "generate", "description": "Generate content"},
        ],
    }

    # Generate preview with execution time
    preview = generate_recipe_preview(recipe_json, execution_time=1.5)

    # Assertions for content
    assert "Recipe Structure" in preview
    assert "Execution Time" in preview
    assert "1.50 seconds" in preview
    assert "Test Recipe" in preview
    assert "A test recipe" in preview
    assert "Steps" in preview
    assert "2" in preview
    assert "read_files" in preview
    assert "generate" in preview
    assert "Read test file" in preview
    assert "Generate content" in preview


def test_generate_recipe_preview_minimal():
    """Test generate_recipe_preview with minimal recipe."""
    # Minimal recipe with just steps
    recipe_json = {
        "steps": [
            {"type": "read", "description": "Read"},
            {"type": "write", "description": "Write"},
        ]
    }

    # Generate preview without execution time
    preview = generate_recipe_preview(recipe_json)

    # Assertions
    assert "Recipe Structure" in preview
    assert "Steps" in preview
    assert "2" in preview
    assert "read" in preview
    assert "write" in preview

    # Should not contain execution time
    assert "Execution Time:" not in preview


def test_format_recipe_results():
    """Test format_recipe_results function."""
    # Test results dictionary
    results = {
        "output": '{"key": "value"}',
        "result_text": "Plain text result",
    }

    # Format with execution time
    formatted = format_recipe_results(results, execution_time=2.5)

    # Assertions
    assert "Recipe Execution Successful" in formatted
    assert "Execution Time" in formatted
    assert "2.50 seconds" in formatted
    assert "output" in formatted
    assert "result_text" in formatted
    assert "value" in formatted
    assert "Plain text result" in formatted


def test_format_recipe_results_empty():
    """Test format_recipe_results with empty results."""
    # Format with empty results
    formatted = format_recipe_results({})

    # Assertions
    assert "Recipe Execution Successful" in formatted
    assert "No string results were found" in formatted


def test_format_context_for_display():
    """Test format_context_for_display function."""
    # Test context dictionary
    context = {
        "string_value": "text",
        "int_value": 123,
        "dict_value": {"nested": "value"},
        "list_value": [1, 2, 3],
    }

    # Format context for display
    formatted = format_context_for_display(context)

    # Load the formatted string as JSON to verify structure
    parsed = json.loads(formatted)

    # Assertions
    assert parsed["string_value"] == "text"
    assert parsed["int_value"] == 123
    assert parsed["dict_value"]["nested"] == "value"
    assert parsed["list_value"] == [1, 2, 3]


def test_format_context_for_display_with_nonserializable():
    """Test format_context_for_display with non-serializable objects."""

    # Create a non-serializable object
    class NonSerializable:
        def __str__(self):
            return "NonSerializable object"

    # Test context with non-serializable object
    context = {
        "normal": "value",
        "special": NonSerializable(),
    }

    # Format context for display
    formatted = format_context_for_display(context)

    # Load the formatted string as JSON to verify structure
    parsed = json.loads(formatted)

    # Assertions
    assert parsed["normal"] == "value"
    assert parsed["special"] == "NonSerializable object"
