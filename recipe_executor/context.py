import copy
from typing import Any, Dict, Iterator, Optional


class Context:
    """
    Context is the shared state container for the Recipe Executor system.
    It provides a simple dictionary-like interface for storing and accessing artifacts
    and maintains a separate configuration for use during recipe execution.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store in the context.
            config: Configuration values for the context.
        """
        # Use deep copy to ensure data isolation
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve an artifact by key. Raises KeyError with a descriptive error message if key does not exist.

        Args:
            key: The key of the artifact.

        Returns:
            The artifact associated with the key.

        Raises:
            KeyError: If the key is not found in the artifacts.
        """
        if key not in self._artifacts:
            raise KeyError(f"Artifact '{key}' not found in context.")
        return self._artifacts[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an artifact in the context.

        Args:
            key: The key under which the artifact is stored.
            value: The artifact value to store.
        """
        self._artifacts[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get an artifact with an optional default value if the key is missing.

        Args:
            key: The key to retrieve.
            default: The value to return if key is not found.

        Returns:
            The artifact associated with the key or the default value if not found.
        """
        return self._artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the artifacts.

        Args:
            key: The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.

        Returns:
            An iterator over the keys of the artifacts.
        """
        # Convert keys to a list to isolate internal state from modifications
        return iter(list(self._artifacts.keys()))

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.

        Returns:
            An iterator over the keys of the artifacts.
        """
        return iter(list(self._artifacts.keys()))

    def __len__(self) -> int:
        """
        Return the number of artifacts stored in the context.

        Returns:
            The number of stored artifacts.
        """
        return len(self._artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts dictionary.
        This ensures the internal state is isolated from external modification.

        Returns:
            A deep copy of the artifacts dictionary.
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> "Context":
        """
        Return a deep copy of the current context, including artifacts and configuration.

        Returns:
            A new Context instance with copies of the current artifacts and configuration.
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))
