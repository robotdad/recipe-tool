from copy import deepcopy
from typing import Any, Dict, Iterator, Optional


class Context:
    """
    Context is a shared state container for the Recipe Executor system.
    It provides a dictionary-like interface to store and retrieve artifacts and configuration
    used by different steps during recipe execution.

    Attributes:
        artifacts (Dict[str, Any]): Stores shared step data.
        config (Dict[str, Any]): Stores configuration values, separate from artifacts.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store.
            config: Configuration values.
        """
        # Use deepcopy to ensure isolation from initial inputs
        self.artifacts: Dict[str, Any] = deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = deepcopy(config) if config is not None else {}

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-like setting of artifacts."""
        self.artifacts[key] = value

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to artifacts. Raises KeyError if key is missing."""
        if key not in self.artifacts:
            raise KeyError(f"Artifact with key '{key}' not found in context.")
        return self.artifacts[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve an artifact with an optional default value.

        Args:
            key: The key of the artifact.
            default: Default value if key is not found.

        Returns:
            The value associated with key or default if key does not exist.
        """
        return self.artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the artifacts."""
        return key in self.artifacts

    def __iter__(self) -> Iterator[str]:
        """Iterate over the artifact keys."""
        return iter(self.artifacts)

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of artifacts."""
        return iter(self.artifacts.keys())

    def __len__(self) -> int:
        """Return the number of artifacts stored in the context."""
        return len(self.artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the artifacts to ensure immutability from outside modifications."""
        return deepcopy(self.artifacts)

    def clone(self) -> 'Context':
        """Return a deep copy of the current context including both artifacts and config."""
        return Context(artifacts=deepcopy(self.artifacts), config=deepcopy(self.config))
