"""Essential utilities for the Recipe Executor app."""

import json
import os
import tempfile
from typing import Any, Callable, Dict, Optional, Tuple


def get_repo_root() -> str:
    """Get the repository root directory."""
    current = os.path.dirname(os.path.abspath(__file__))
    # Check if we've reached the root (works on all platforms)
    while True:
        if os.path.exists(os.path.join(current, "pyproject.toml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Reached filesystem root
            break
        current = parent
    return os.path.dirname(os.path.abspath(__file__))


def get_main_repo_root() -> Optional[str]:
    """Get the main repository root that contains recipes directory."""
    current = get_repo_root()
    while True:
        if os.path.exists(os.path.join(current, "recipes")) and os.path.exists(os.path.join(current, "ai_context")):
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Reached filesystem root
            break
        current = parent
    return None


def read_file(path: str) -> str:
    """Read content from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_temp_file(content: str, suffix: str = ".txt") -> Tuple[str, Callable[[], None]]:
    """Create a temporary file with cleanup function."""
    temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=suffix, delete=False, encoding="utf-8")
    temp_file.write(content)
    temp_file.close()

    def cleanup():
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass

    return temp_file.name, cleanup


def parse_context_vars(context_str: Optional[str]) -> Dict[str, Any]:
    """Parse context variables from comma-separated key=value pairs."""
    if not context_str:
        return {}

    context = {}
    for pair in context_str.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            context[key.strip()] = value.strip()
    return context


def format_results(results: Dict[str, str], execution_time: float = 0.0) -> str:
    """Format recipe execution results as markdown."""
    md = [f"### Recipe Execution Results\n\n**Execution Time**: {execution_time:.2f}s\n"]

    for key, value in results.items():
        md.append(f"\n**{key}**:\n")
        if value.startswith("{") or value.startswith("["):
            md.append(f"```json\n{value}\n```")
        else:
            md.append(f"```\n{value}\n```")

    return "\n".join(md)


def safe_json_dumps(obj: Any) -> str:
    """Safely convert object to JSON string."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return json.dumps({"error": "Could not serialize object"})
