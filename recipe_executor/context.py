import copy
from typing import Any, Dict, Iterator, Optional


class Context:
    """
    Context is the shared state container for the Recipe Executor system.
    It provides a simple dictionary-like interface for storing and accessing artifacts
    and maintains a separate configuration for use during recipe execution.
    
    Core Responsibilities:
    - Store and provide access to artifacts (data shared between steps).
    - Maintain separate configuration values.
    - Provide dictionary-like operations (get, set, iteration).
    - Support deep cloning to ensure data isolation.
    """
    
    def __init__(self, artifacts: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Context with optional artifacts and configuration.

        Args:
            artifacts: Optional initial artifacts to store in the context.
            config: Optional configuration values for the context.
        """
        # Use deep copy for true data isolation
        self._artifacts: Dict[str, Any] = copy.deepcopy(artifacts) if artifacts is not None else {}
        self.config: Dict[str, Any] = copy.deepcopy(config) if config is not None else {}
    
    def __getitem__(self, key: str) -> Any:
        """
        Retrieve an artifact by key.

        Args:
            key: The key name of the artifact.

        Returns:
            The artifact associated with the key.
        
        Raises:
            KeyError: If the key is not present in the context, with a descriptive error message.
        """
        if key not in self._artifacts:
            raise KeyError(f"Artifact '{key}' not found in context.")
        return self._artifacts[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an artifact in the context.

        Args:
            key: The key under which the artifact is stored.
            value: The value of the artifact to store.
        """
        self._artifacts[key] = value
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get an artifact with an optional default if the key is missing.

        Args:
            key: The key of the artifact to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The artifact associated with the key or the provided default if key is missing.
        """
        return self._artifacts.get(key, default)
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the artifacts.

        Args:
            key: The key to check.

        Returns:
            True if the key exists; False otherwise.
        """
        return key in self._artifacts
    
    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over the artifact keys.

        Returns:
            An iterator for the artifact keys.
        """
        # Convert keys to a list to avoid external modifications
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
        Return the count of artifacts stored.

        Returns:
            The number of artifacts in the context.
        """
        return len(self._artifacts)
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Return a deep copy of the artifacts dictionary.
        This ensures external code cannot modify the internal state of the context.

        Returns:
            A deep copy of the artifacts dictionary.
        """
        return copy.deepcopy(self._artifacts)
    
    def clone(self) -> "Context":
        """
        Return a deep copy of the current context.

        This method clones both the artifacts and configuration to ensure complete data isolation.
        
        Returns:
            A new Context instance with the current state copied deeply.
        """
        return Context(
            artifacts=copy.deepcopy(self._artifacts),
            config=copy.deepcopy(self.config)
        )
