"""
"""
from compiler import Visitor


class ClassVisitor(Visitor):
    """
    """

    def __init__(self, ast, info):
        self.class_def = ast
        self.info = info

    def start_visit(self):
        self.class_def.accept(self)

    def act(self):
        """
        """
        return False
