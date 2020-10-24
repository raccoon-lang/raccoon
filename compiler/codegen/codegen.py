"""
"""

from abc import ABC
from copy import deepcopy

class Codegen(ABC):
    """
    """

    def __repr__(self):
        fields = deepcopy(vars(self))
        fields['kind'] = type(self).__name__
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"

    def generate_function(self):
        pass

    def dumps(self):
        pass
