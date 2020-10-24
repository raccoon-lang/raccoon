"""
"""
from copy import deepcopy
from platform import machine


class Codegen:
    """
    """

    def __init__(self):
        self.word_size = 64 if '64' in machine() else 32

    def __repr__(self):
        fields = deepcopy(vars(self))
        fields['kind'] = type(self).__name__
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"

    def generate_function(self):
        pass

    def dumps(self):
        pass
