from typing import Any, Dict, Iterator, Optional


class Context:
    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts (Optional[Dict[str, Any]]): Initial artifacts to store.
            config (Optional[Dict[str, Any]]): Configuration values.
        """
        # Use copies to ensure isolation from external changes
        self._artifacts: Dict[str, Any] = artifacts.copy() if artifacts is not None else {}
        self.config: Dict[str, Any] = config.copy() if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        """Dictionary-like access to artifacts."""
        if key not in self._artifacts:
            raise KeyError(f"Artifact with key '{key}' does not exist.")
        return self._artifacts[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Dictionary-like setting of artifacts."""
        self._artifacts[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get an artifact with an optional default value."""
        return self._artifacts.get(key, default)

    def keys(self) -> Iterator[str]:
        """Return an iterator over the keys of artifacts."""
        return iter(self._artifacts.keys())

    def __len__(self) -> int:
        """Return the number of artifacts."""
        return len(self._artifacts)

    def __iter__(self) -> Iterator[str]:
        """Iterate over artifact keys."""
        return iter(self._artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """Return a copy of the artifacts as a dictionary to ensure immutability."""
        return self._artifacts.copy()
