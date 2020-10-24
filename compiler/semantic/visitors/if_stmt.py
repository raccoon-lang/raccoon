"""
"""

from compiler.ast import (
    Integer,
)
from compiler import Visitor


class IfVisitor(Visitor):
    """
    """

    def __init__(self, info, ast):
        self.if_stmt = ast
        self.info = info

    def start_visit(self):
        self.if_stmt.accept(self)

    def act(self):
        """
        """

        for ast in self.if_stmt.body:
            type_ = type(ast)

            if type_ == Integer:
                pass

        return False
