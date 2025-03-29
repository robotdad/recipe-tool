from dataclasses import dataclass, field
from typing import Any, Dict
import os


@dataclass
class Context:
    input_root: str
    output_root: str
    data: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, other: Dict[str, Any]):
        self.data.update(other)

    def full_input_path(self, path: str) -> str:
        # if path is absolute, return as is, else join with input_root
        if os.path.isabs(path):
            return path
        return os.path.join(self.input_root, path)

    def full_output_path(self, path: str) -> str:
        # if path is absolute, return as is, else join with output_root
        if os.path.isabs(path):
            return path
        return os.path.join(self.output_root, path)
