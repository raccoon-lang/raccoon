"""
"""

from compiler.ast import (
    Integer,
)
from compiler import Visitor


class ReturnVisitor(Visitor):
    """
    """

    def __init__(self, ast, state):
        self.state = state

    def start_visit(self):
        self.ast.accept(self)

    def act(self, return_):
        """
        """

        for ast in return_.exprs:
            type_ = type(ast)

            if type_ == Integer:
                pass

        return False
