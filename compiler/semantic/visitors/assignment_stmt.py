"""
"""
from compiler import Visitor


class AssignmentVisitor(Visitor):
    """
    """

    def __init__(self, info, ast):
        self.assignment = ast
        self.info = info

    def start_visit(self):
        self.assignment.accept(self)

    def act(self):
        """
        """

        for ast in self.assignment.lhses:
            pass

        return False
