"""
"""
from compiler import Visitor

class FuncParamVisitor(Visitor):
    """
    """

    def __init__(self, ast, state):
        self.state = state

    def start_visit(self):
        self.ast.accept(self)

    def act(self, param):
        """
        TODO: Finish smantic analysis.
        """

        # Check params names do not conflict with each other
        

        return False

class FuncParamsVisitor(Visitor):
    """
    """

    def __init__(self, ast, state):
        self.state = state

    def start_visit(self):
        self.ast.accept(self)

    def act(self, params):
        """
        """

        for param in params:
            FuncParamVisitor(self.state, param).start_visit()

        return False
