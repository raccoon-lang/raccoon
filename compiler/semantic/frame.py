"""
"""


class FunctionFrame:
    """
    def foo(a, b):
        x = bar(a, 500)
        y = b + x
        if cond:
            z = "Hello"
        else:
            z = y
        return z

    frame foo(0, 1):
        2: bar(0, int)
        3: +(2, 1)
        4: i64 | 3
        _: 4

    FunctionFrame(
        param_size=2,
        type_flow=[
            ("bar", [0, "lib.int"]),
            ("+", ["lib.i64", 1]),
            (".union", [12, 3]),
            (".return", [4]),
        ]
    )
    """

    def __init__(self, param_size, type_flow, ast):
        self.param_size = param_size
        self.type_flow = type_flow
        self.ast = ast


class TypeFrame:
    """
    """

    def __init__(self):
        self.type_layout = []

