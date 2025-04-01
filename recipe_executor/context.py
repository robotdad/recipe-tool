from typing import Any, Dict, Optional, Iterator
import copy


class Context:
    """
    The Context class provides a shared state container for the Recipe Executor system.
    It allows steps to store and retrieve artifacts and configuration options within
    a recipe execution. This implementation follows a minimalist design as specified.
    """

    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Initial artifacts to store
            config: Configuration values
        """
        # Use deep copy to prevent external modifications
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}

    def __getitem__(self, key: str) -> Any:
        """
        Dictionary-like access to artifacts.

        Args:
            key: The key of the artifact to retrieve

        Returns:
            The value associated with the key

        Raises:
            KeyError: If the key does not exist
        """
        if key in self._artifacts:
            return self._artifacts[key]
        raise KeyError(f"Key '{key}' not found in context artifacts.")

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Dictionary-like setting of artifacts.

        Args:
            key: The key to be set
            value: The value to associate with the key
        """
        self._artifacts[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get an artifact with an optional default value if the key is missing.

        Args:
            key: The key to retrieve
            default: The value to return if key is not found

        Returns:
            The value associated with the key or the default value
        """
        return self._artifacts.get(key, default)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in artifacts.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        return key in self._artifacts

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over the artifact keys. Converts keys to a list for safe iteration.

        Returns:
            An iterator over the keys of the artifacts
        """
        # Convert keys to a list to prevent issues if artifacts are modified during iteration
        return iter(list(self._artifacts.keys()))

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the keys of artifacts.

        Returns:
            An iterator over artifact keys
        """
        return self.__iter__()

    def __len__(self) -> int:
        """
        Return the number of artifacts stored in the context.

        Returns:
            The number of artifacts
        """
        return len(self._artifacts)

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a copy of the artifacts as a dictionary to ensure immutability.

        Returns:
            A copy of the artifacts dictionary
        """
        return copy.deepcopy(self._artifacts)

    def clone(self) -> 'Context':
        """
        Return a deep copy of the current context, including artifacts and configuration.

        Returns:
            A new Context object with a deep copy of the current state
        """
        return Context(artifacts=copy.deepcopy(self._artifacts), config=copy.deepcopy(self.config))
