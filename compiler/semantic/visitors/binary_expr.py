"""
"""
from compiler import Visitor


class BinaryExprVisitor(Visitor):
    """
    """

    def __init__(self, info, ast):
        self.binary_expr = ast
        self.info = info

    def start_visit(self):
        self.binary_expr.accept(self)

    def act(self, ast):
        """
        """

        for ast in self.binary_expr.lhses:
            pass

        return False
