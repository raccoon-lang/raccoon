"""
"""
from compiler import Visitor


class FuncParamsVisitor(Visitor):
    """
    """

    def __init__(self, ast, state):
        self.state = state

    def start_visit(self):
        self.ast.accept(self)

    def act(self, assignment):
        """
        """
        
        return False
