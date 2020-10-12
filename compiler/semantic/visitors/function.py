"""
"""

from compiler import Visitor
from compiler.ast import (
    Null,
    Identifier,
    Integer,
    Float,
    ImagInteger,
    ImagFloat,
    String,
    ByteString,
    PrefixedString,
    Operator,
    AssignmentStatement,
    Function,
    Class,
    ImportStatement,
    ReturnStatement,
)
from .func_params import (
    FuncParamsVisitor,
)


class FunctionVisitor(Visitor):
    """
    """

    def __init__(self, ast, state):
        self.frame = None
        self.state = state

    def start_visit(self):
        self.ast.accept(self)

    def act(self, function):
        """
        """

        data = FuncParamsVisitor(function.param, self.state).start_visit()

        for ast in function.body:
            type_ = type(ast)

        return False
