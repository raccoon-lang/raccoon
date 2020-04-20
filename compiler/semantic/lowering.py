"""
This module ...
"""


class LoweredAST:
    """
    """

    def accept_on_children(self, visitor):
        pass

    def accept(self, visitor):
        """
        Accepts visitor and calls visitor's act method. Some visitors prevent
        any further traversal by returning False from their act methods.
        """

        if visitor.act(self):
            self.accept_on_children(visitor)


class Null(LoweredAST):
    pass


class FunctionInstance(LoweredAST):
    """
    """

    def __init__(self, body_types=[], return_type=Null()):
        self.body_types = body_types
        self.return_type = return_type
