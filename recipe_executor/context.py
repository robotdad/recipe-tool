import copy


class Context:
    def __init__(self, artifacts=None, config=None):
        self.artifacts = artifacts or {}
        self.config = config or {}

    def __getitem__(self, key):
        return self.artifacts.get(key)

    def __setitem__(self, key, value):
        self.artifacts[key] = value

    def get(self, key, default=None):
        return self.artifacts.get(key, default)

    def keys(self):
        return self.artifacts.keys()

    def __len__(self):
        return len(self.artifacts)

    def __iter__(self):
        return iter(self.artifacts)

    def as_dict(self):
        return copy.copy(self.artifacts)
