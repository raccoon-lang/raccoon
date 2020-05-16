"""
"""

from .assignment import AssignmentVisitor
from .return_ import ReturnVisitor
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

        for ast in function.body:
            type_ = type(ast)

            if type_ == ReturnStatement:
                result = ReturnVisitor(self.symbol_table).start_visit()
                print('>>> function.return', result)

        return False
