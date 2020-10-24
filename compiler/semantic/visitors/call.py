"""
"""
from compiler import Visitor


class CallVisitor(Visitor):
    """
    """

    def __init__(self, info, ast):
        self.call = ast
        self.info = info

    def start_visit(self):
        self.call.accept(self)

    def act(self, ast):
        """
        """
        
        return False
