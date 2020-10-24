from copy import deepcopy

class CompilerOptions:
    def __init__(self, target_code=None):
        self.verbose = False
        self.target_code = target_code

    def __repr__(self):
        fields = deepcopy(vars(self))
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"
