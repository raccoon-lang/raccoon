"""
"""
from compiler import Visitor


class AssignmentVisitor(Visitor):
    """
    """

    def __init__(self, ast, state):
        self.state = state

    def start_visit(self):
        self.ast.accept(self)

    def act(self, assignement):
        """
        """

        for ast in assignement.lhses:
            pass

        return False
