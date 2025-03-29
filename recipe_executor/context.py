from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class Context:
    """Holds artifacts and optional config, providing dict-like access to artifacts."""

    artifacts: dict = field(default_factory=dict)
    config: dict = field(default_factory=dict)  # for any global settings or legacy compat

    def __init__(self, artifacts=None, config=None) -> None:
        # Only keep artifacts and config in context
        self.artifacts = artifacts or {}
        self.config = config or {}

    def __getitem__(self, key) -> Any:
        # Enable dict-like read access to artifacts
        return self.artifacts[key]

    def __setitem__(self, key, value) -> None:
        # Enable dict-like write access to artifacts
        self.artifacts[key] = value

    def get(self, key, default=None) -> Any:
        # Safe get method for artifacts
        return self.artifacts.get(key, default)

    def as_dict(self) -> dict[Any, Any]:
        """Return a shallow copy of artifact data (for templating)."""
        return dict(self.artifacts)

    def __iter__(self) -> Iterator[Any]:
        # Iterate over artifact keys (to support dict-like behavior)
        return iter(self.artifacts)

    def __len__(self) -> int:
        # Number of artifacts stored
        return len(self.artifacts)

    def keys(self):
        # Keys of the artifacts dictionary
        return self.artifacts.keys()
