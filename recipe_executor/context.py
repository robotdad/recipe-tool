# context.py
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Context:
    """
    Encapsulates the shared context for recipe execution.

    Contains required fields such as 'input_root' and 'output_root', and an extra dictionary
    for any additional context values.
    """

    input_root: str
    output_root: str
    extra: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-like access for required fields and extra values.
        """
        if key == "input_root":
            return self.input_root
        if key == "output_root":
            return self.output_root
        return self.extra.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Allow dictionary-like setting for required fields and extra values.
        """
        if key == "input_root":
            self.input_root = value
        elif key == "output_root":
            self.output_root = value
        else:
            self.extra[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value by key, returning default if not found.
        """
        if key == "input_root":
            return self.input_root
        if key == "output_root":
            return self.output_root
        return self.extra.get(key, default)

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update the context with a dictionary of new values.
        """
        for key, value in updates.items():
            self[key] = value

    def as_dict(self) -> Dict[str, Any]:
        """
        Return a plain dictionary combining required fields and extra context.
        """
        return {"input_root": self.input_root, "output_root": self.output_root, **self.extra}
