"""
"""

from compiler.ast import (
    Integer,
)
from compiler import Visitor


class ReturnVisitor(Visitor):
    """
    """

    def __init__(self, ast, info):
        self.return_stmt = ast
        self.info = info

    def start_visit(self):
        self.return_stmt.accept(self)

    def act(self):
        """
        """

        for ast in self.return_stmt.exprs:
            type_ = type(ast)

            if type_ == Integer:
                pass

        return False
