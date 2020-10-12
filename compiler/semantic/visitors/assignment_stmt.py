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

    def act(self, assignment):
        """
        """

        for ast in assignment.lhses:
            pass

        return False
