=== File: recipes/codebase_generator/README.md ===
# Codebase Generator

## Overview

The Codebase Generator is a simple but powerful recipe for generating code from specifications. It implements a minimalist approach to code generation, focusing on the core functionality needed to transform a specification into working code.

## Key Features

1. **Specification-Driven Code Generation**: Generate code directly from markdown specifications
2. **Implementation Philosophy**: Code follows a consistent philosophy favoring simplicity and clarity
3. **Support for Multiple Languages**: Configurable to generate code in different programming languages
4. **Optional Documentation Integration**: Can incorporate usage documentation into the generation process
5. **Existing Code Awareness**: Can build upon existing code when specified

## How It Works

The Codebase Generator follows a simple three-step process:

1. **Read Implementation Philosophy**: Loads the implementation philosophy which guides the code generation
2. **Generate Code**: Uses an LLM to transform the specification into code that follows the implementation philosophy
3. **Write Output**: Writes the generated code to the specified output location

## Usage Instructions

To generate code from a specification:

```bash
python recipe_executor/main.py recipes/codebase_generator/generate_code.json \
  --context spec="Your component specification here" \
  --context component_id=your_component \
  --context output_path=path/to/output
```

### Required Parameters

- `spec`: The specification text for the component
- `component_id`: Identifier for the component being generated

### Optional Parameters

- `output_path`: Path where generated code should be placed (default: current directory)
- `language`: Programming language to generate (default: python)
- `model`: LLM model to use (default: openai:o3-mini)
- `existing_code`: Existing code to build upon (if any)
- `usage_doc`: Usage documentation to incorporate
- `additional_content`: Any additional content to include in the prompt
- `output_root`: Base directory for output files (default: output)

## Implementation Philosophy

The Codebase Generator follows a philosophy of ruthless simplicity, favoring:

- Minimal implementations that do exactly what's needed
- Clear, readable code over clever solutions
- Direct approaches with minimal abstraction
- Code that is easy to understand and maintain

For more details, see the [IMPLEMENTATION_PHILOSOPHY.md](includes/IMPLEMENTATION_PHILOSOPHY.md) file.

## Example

```bash
python recipe_executor/main.py recipes/codebase_generator/generate_code.json \
  --context spec="Create a function that validates email addresses using regex and returns a boolean result, \
    provide a main for passing an arg to the function and printing the result ." \
  --context component_id=email_validator \
  --context output_path=utils
```

This will generate an email validation utility in `output/utils/email_validator.py`.

## Integration with Other Recipes

The Codebase Generator is designed to be used as a component in larger generation workflows:

### Recipe Executor Self-Generation

The Recipe Executor project itself uses the codebase generator for its own component generation via `build_component.json`. This demonstrates a powerful real-world example of complex recipe composition:

```json
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/specs{{component_path}}/{{component_id}}.md",
      "artifact": "spec"
    },
    {
      "type": "read_file",
      "path": "recipes/recipe_executor/docs{{component_path}}/{{component_id}}.md",
      "artifact": "usage_doc",
      "optional": true
    },
    {
      "type": "execute_recipe",
      "recipe_path": "recipes/codebase_generator/generate_code.json",
      "context_overrides": {
        "model": "openai:o3-mini",
        "output_root": "output",
        "output_path": "recipe_executor{{component_path}}",
        "language": "python",
        "spec": "{{spec}}",
        "usage_doc": "{{usage_doc}}",
        "existing_code": "{{existing_code}}",
        "additional_content": "{{additional_content}}"
      }
    }
  ]
}
```

This pattern shows how to:
1. Read specifications and documentation
2. Execute the codebase generator with specific context overrides
3. Build a complete system through composition of recipes

### Other Integration Patterns

- The Component Blueprint Generator creates well-structured specs that work perfectly as inputs to this generator
- You can create your own recipes that execute this generator with custom context
- This generator can be combined with testing, documentation, or deployment recipes

=== File: recipes/codebase_generator/generate_code.json ===
{
  "steps": [
    {
      "type": "read_file",
      "path": "recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md",
      "artifact": "implementation_philosophy"
    },
    {
      "type": "generate",
      "prompt": "You are an expert developer. Based on the following specification{% if existing_code %} and existing code{% endif %}, generate {{language|default:'python'}} code for the {{component_id}} component of a larger project.\n\nSpecification:\n{{spec}}\n\n{% if existing_code %}<EXISTING_CODE>\n{{existing_code}}\n</EXISTING_CODE>\n\n{% endif %}{% if usage_doc %}<USAGE_DOCUMENTATION>\n{{usage_doc}}\n</USAGE_DOCUMENTATION>\n{% endif %}{% if additional_content %}{{additional_content}}{% endif %}\n\nEnsure the code follows the specification exactly, implements all required functionality, and adheres to the implementation philosophy described in the tags. Include appropriate error handling and type hints. The implementation should be minimal but complete.\n\n<IMPLEMENTATION_PHILOSOPHY>\n{{implementation_philosophy}}\n</IMPLEMENTATION_PHILOSOPHY>\n\nGenerate the appropriate file(s): {{output_path|default:'.'}}/{{component_id}}.<ext>, etc.\n\n",
      "model": "{{model|default:'openai:o3-mini'}}",
      "artifact": "generated_code"
    },
    {
      "type": "write_file",
      "artifact": "generated_code",
      "root": "{{output_root|default:'output'}}"
    }
  ]
}


=== File: recipes/codebase_generator/includes/IMPLEMENTATION_PHILOSOPHY.md ===
# Implementation Philosophy

This document outlines the core implementation philosophy and guidelines for software development projects. It serves as a central reference for decision-making and development approach throughout the project.

## Core Philosophy

Embodies a Zen-like minimalism that values simplicity and clarity above all. This approach reflects:

- **Wabi-sabi philosophy**: Embracing simplicity and the essential. Each line serves a clear purpose without unnecessary embellishment.
- **Occam's Razor thinking**: The solution should be as simple as possible, but no simpler.
- **Trust in emergence**: Complex systems work best when built from simple, well-defined components that do one thing well.
- **Present-moment focus**: The code handles what's needed now rather than anticipating every possible future scenario.
- **Pragmatic trust**: The developer trusts external systems enough to interact with them directly, handling failures as they occur rather than assuming they'll happen.

This development philosophy values clear documentation, readable code, and belief that good architecture emerges from simplicity rather than being imposed through complexity.

## Core Design Principles

### 1. Ruthless Simplicity

- **KISS principle taken to heart**: Keep everything as simple as possible, but no simpler
- **Minimize abstractions**: Every layer of abstraction must justify its existence
- **Start minimal, grow as needed**: Begin with the simplest implementation that meets current needs
- **Avoid future-proofing**: Don't build for hypothetical future requirements
- **Question everything**: Regularly challenge complexity in the codebase

### 2. Architectural Integrity with Minimal Implementation

- **Preserve key architectural patterns**: MCP for service communication, SSE for events, separate I/O channels, etc.
- **Simplify implementations**: Maintain pattern benefits with dramatically simpler code
- **Scrappy but structured**: Lightweight implementations of solid architectural foundations
- **End-to-end thinking**: Focus on complete flows rather than perfect components

### 3. Library Usage Philosophy

- **Use libraries as intended**: Minimal wrappers around external libraries
- **Direct integration**: Avoid unnecessary adapter layers
- **Selective dependency**: Add dependencies only when they provide substantial value
- **Understand what you import**: No black-box dependencies

## Technical Implementation Guidelines

### API Layer

- Implement only essential endpoints
- Minimal middleware with focused validation
- Clear error responses with useful messages
- Consistent patterns across endpoints

### Database & Storage

- Simple schema focused on current needs
- Use TEXT/JSON fields to avoid excessive normalization early
- Add indexes only when needed for performance
- Delay complex database features until required

### MCP Implementation

- Streamlined MCP client with minimal error handling
- Utilize FastMCP when possible, falling back to lower-level only when necessary
- Focus on core functionality without elaborate state management
- Simplified connection lifecycle with basic error recovery
- Implement only essential health checks

### SSE & Real-time Updates

- Basic SSE connection management
- Simple resource-based subscriptions
- Direct event delivery without complex routing
- Minimal state tracking for connections

### Event System

- Simple topic-based publisher/subscriber
- Direct event delivery without complex pattern matching
- Clear, minimal event payloads
- Basic error handling for subscribers

### LLM Integration

- Direct integration with Pydantic AI
- Minimal transformation of responses
- Handle common error cases only
- Skip elaborate caching initially

### Message Routing

- Simplified queue-based processing
- Direct, focused routing logic
- Basic routing decisions without excessive action types
- Simple integration with other components

## Development Approach

### Vertical Slices

- Implement complete end-to-end functionality slices
- Start with core user journeys
- Get data flowing through all layers early
- Add features horizontally only after core flows work

### Iterative Implementation

- 80/20 principle: Focus on high-value, low-effort features first
- One working feature > multiple partial features
- Validate with real usage before enhancing
- Be willing to refactor early work as patterns emerge

### Testing Strategy

- Emphasis on integration and end-to-end tests
- Manual testability as a design goal
- Focus on critical path testing initially
- Add unit tests for complex logic and edge cases
- Testing pyramid: 60% unit, 30% integration, 10% end-to-end

### Error Handling

- Handle common errors robustly
- Log detailed information for debugging
- Provide clear error messages to users
- Fail fast and visibly during development

## Decision-Making Framework

When faced with implementation decisions, ask these questions:

1. **Necessity**: "Do we actually need this right now?"
2. **Simplicity**: "What's the simplest way to solve this problem?"
3. **Directness**: "Can we solve this more directly?"
4. **Value**: "Does the complexity add proportional value?"
5. **Maintenance**: "How easy will this be to understand and change later?"

## Areas to Embrace Complexity

Some areas justify additional complexity:

1. **Security**: Never compromise on security fundamentals
2. **Data integrity**: Ensure data consistency and reliability
3. **Core user experience**: Make the primary user flows smooth and reliable
4. **Error visibility**: Make problems obvious and diagnosable

## Areas to Aggressively Simplify

Push for extreme simplicity in these areas:

1. **Internal abstractions**: Minimize layers between components
2. **Generic "future-proof" code**: Resist solving non-existent problems
3. **Edge case handling**: Handle the common cases well first
4. **Framework usage**: Use only what you need from frameworks
5. **State management**: Keep state simple and explicit

## Practical Examples

### Good Example: Direct SSE Implementation

```python
# Simple, focused SSE manager that does exactly what's needed
class SseManager:
    def __init__(self):
        self.connections = {}  # Simple dictionary tracking

    async def add_connection(self, resource_id, user_id):
        """Add a new SSE connection"""
        connection_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        self.connections[connection_id] = {
            "resource_id": resource_id,
            "user_id": user_id,
            "queue": queue
        }
        return queue, connection_id

    async def send_event(self, resource_id, event_type, data):
        """Send an event to all connections for a resource"""
        # Direct delivery to relevant connections only
        for conn_id, conn in self.connections.items():
            if conn["resource_id"] == resource_id:
                await conn["queue"].put({
                    "event": event_type,
                    "data": data
                })
```

### Bad Example: Over-engineered SSE Implementation

```python
# Overly complex with unnecessary abstractions and state tracking
class ConnectionRegistry:
    def __init__(self, metrics_collector, cleanup_interval=60):
        self.connections_by_id = {}
        self.connections_by_resource = defaultdict(list)
        self.connections_by_user = defaultdict(list)
        self.metrics_collector = metrics_collector
        self.cleanup_task = asyncio.create_task(self._cleanup_loop(cleanup_interval))

    # [50+ more lines of complex indexing and state management]
```

### Good Example: Simple MCP Client

```python
# Focused MCP client with clean error handling
class McpClient:
    def __init__(self, endpoint: str, service_name: str):
        self.endpoint = endpoint
        self.service_name = service_name
        self.client = None

    async def connect(self):
        """Connect to MCP server"""
        if self.client is not None:
            return  # Already connected

        try:
            # Create SSE client context
            async with sse_client(self.endpoint) as (read_stream, write_stream):
                # Create client session
                self.client = ClientSession(read_stream, write_stream)
                # Initialize the client
                await self.client.initialize()
        except Exception as e:
            self.client = None
            raise RuntimeError(f"Failed to connect to {self.service_name}: {str(e)}")

    async def call_tool(self, name: str, arguments: dict):
        """Call a tool on the MCP server"""
        if not self.client:
            await self.connect()

        return await self.client.call_tool(name=name, arguments=arguments)
```

### Bad Example: Over-engineered MCP Client

```python
# Complex MCP client with excessive state management and error handling
class EnhancedMcpClient:
    def __init__(self, endpoint, service_name, retry_strategy, health_check_interval):
        self.endpoint = endpoint
        self.service_name = service_name
        self.state = ConnectionState.DISCONNECTED
        self.retry_strategy = retry_strategy
        self.connection_attempts = 0
        self.last_error = None
        self.health_check_interval = health_check_interval
        self.health_check_task = None
        # [50+ more lines of complex state tracking and retry logic]
```

## Remember

- It's easier to add complexity later than to remove it
- Code you don't write has no bugs
- Favor clarity over cleverness
- The best code is often the simplest

This philosophy document serves as the foundational guide for all implementation decisions in the project.


