# Recipe Executor Development Guidelines

## Build and Run Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run a recipe**: `python recipe_executor/main.py path/to/recipe.yaml`
- **Run with options**: `python recipe_executor/main.py recipe.yaml --model claude-3-7-sonnet-20250219 --provider anthropic`
- **Debug mode**: `python recipe_executor/main.py recipe.yaml --log-level debug`

## Code Style Guidelines

- **Python version**: 3.9+ compatible
- **Imports**: Standard library first, third-party packages second, local modules third (alphabetical within groups)
- **Typing**: Use type hints for all function parameters and return values
- **Error handling**: Use try/except with specific exceptions rather than bare except blocks
- **Documentation**: Docstrings using triple quotes for classes and functions
- **Line length**: Max 120 characters
- **Structure**: Follow existing module organization
- **Validation**: For Python, use Pydantic models for data validation and serialization
- **Asynchronous code**: Use async/await for all I/O operations
- **Python**: Follow Google Python Style Guide with type hints
- **TypeScript**: 4-space indent, 100 char line length, single quotes, semicolons
- **Architecture**: Domain-driven with clear layer separation
- **Exceptions**: Consistent error handling with custom exception hierarchy
- **Models**: API models separate from domain models
- **Frontend**: React components organized by feature
- **Events**: Event-driven architecture for SSE implementation
