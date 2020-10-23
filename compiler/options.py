from copy import deepcopy

class CompilerOptions:
    def __init__(self):
        self.verbose = False

    def __repr__(self):
        fields = deepcopy(vars(self))
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"
