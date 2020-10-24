"""
"""
from copy import deepcopy
from platform import machine


class Codegen:
    """
    """

    def __init__(self, semantic_info):
        self.word_size = 64 if '64' in machine() else 32
        self.semantic_info = semantic_info

    def __repr__(self):
        fields = deepcopy(vars(self))
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"

    def generate(self):
        return self

    def dumps(self):
        pass
