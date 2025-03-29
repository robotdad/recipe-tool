from dataclasses import dataclass, field


@dataclass
class Context:
    input_root: str
    output_root: str
    extras: dict = field(default_factory=dict)

    def __getitem__(self, key):
        # Allow access to extras via context[key]
        return self.extras.get(key)

    def __setitem__(self, key, value):
        self.extras[key] = value

    def get(self, key, default=None):
        return self.extras.get(key, default)

    def update(self, data: dict):
        self.extras.update(data)
