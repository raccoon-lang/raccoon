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
from compiler.semantic.info import SymbolInfo, SymbolKind
from compiler.semantic.checks import SemanticChecks

class FuncParamVisitor(Visitor):
    """
    """

    def __init__(self, info, param_ast, function_ast):
        self.param = param_ast
        self.function = function_ast
        self.info = info

    def start_visit(self):
        self.param.accept(self)

    def act(self, ast):
        """
        """

        # Get scope, function and param tokens.
        param_name_token = self.info.tokens[self.param.name.index]
        function_name_token = self.info.tokens[self.function.name.index]
        scope = self.info.symbols[-1]

        # Check params names do not conflict with each other
        SemanticChecks.param_name_conflict(param_name_token, function_name_token, scope)

        # Save parameter in symbol table
        self.info.add_new_symbol(
            param_name_token.data,
            symbol_info=SymbolInfo(
                SymbolKind.PARAM,
                ast_ref=self.param
            )
        )

        return False

class FuncParamsVisitor(Visitor):
    """
    """

    def __init__(self, info, ast):
        self.function = ast
        self.params = ast.params
        self.info = info

    def start_visit(self):
        self.params.accept(self)

    def act(self, ast):
        """
        """

        for param in self.params.params:
            FuncParamVisitor(self.info, param, self.function).start_visit()

        return False


class FunctionVisitor(Visitor):
    """
    """

    def __init__(self, info, ast):
        self.function = ast
        self.info = info

    def start_visit(self):
        self.function.accept(self)

    def act(self, ast):
        """
        """

        # Get function name token
        function_name_token = self.info.tokens[self.function.name.index]

        # Save function in symbol table
        self.info.add_new_top_level_symbol(
            function_name_token.data,
            SymbolInfo(
                kind=SymbolKind.FUNCTION,
                ast_ref=self.function,
            )
        )

        # Create a new scope in symbol table for function
        self.info.add_new_scope(function_name_token.data)

        # Handle parameters
        FuncParamsVisitor(self.info, self.function).start_visit()

        return False
