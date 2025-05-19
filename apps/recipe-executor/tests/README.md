# Recipe Executor App Tests

This directory contains tests for the Recipe Executor App.

## Running Tests

Run all tests with:

```bash
cd apps/recipe-executor
make test
```

Run tests with coverage:

```bash
make coverage
```

## Test Structure

- `__init__.py`: Package initialization
- `test_app.py`: Tests for app.py
- `test_core.py`: Tests for core.py
- `test_ui_components.py`: Tests for ui_components.py
- `test_utils.py`: Tests for utils.py

## Adding Tests

To add a new test:

1. Create a new test file or add to an existing one
2. Use pytest fixtures for test setup
3. Use the unittest.mock module for mocking dependencies
4. Run the tests to ensure they pass

Example test:

```python
import pytest
from unittest.mock import MagicMock, patch

def test_something():
    """Test description."""
    # Arrange
    # ... set up test data ...
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == expected_result
```

## Testing Async Functions

For async functions, use:

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test description."""
    # Arrange
    # ... set up test data ...
    
    # Act
    result = await async_function_to_test()
    
    # Assert
    assert result == expected_result
```