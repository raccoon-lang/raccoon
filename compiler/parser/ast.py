"""
Contains classes that describe Raccoon's Abstract Syntax Tree.
"""

from enum import Enum


class BinaryOpKind(Enum):
    """
    The different kinds of binary operators
    """

    POWER = 0
    MUL = 1
    MATMUL = 2
    DIV = 3
    MOD = 4
    INTEGER_DIV = 5
    PLUS = 6
    MINUS = 7
    SHIFT_LEFT = 8
    SHIFT_RIGHT = 9
    BINARY_AND = 10
    BINARY_XOR = 11
    BINARY_OR = 12
    LESSER_THAN = 13
    GREATER_THAN = 14
    EQUAL = 15
    EQUAL_LESSER_THAN = 16
    EQUAL_GREATER_THAN = 17
    NOT_EQUAL = 18
    IN = 19
    NOT_IN = 20
    IS = 21
    IS_NOT = 22

    @staticmethod
    def from_string(op, rem_op=None):
        if op == "^":
            return BinaryOpKind.POWER
        elif op == "*":
            return BinaryOpKind.MUL
        elif op == "@":
            return BinaryOpKind.MATMUL
        elif op == "/":
            return BinaryOpKind.DIV
        elif op == "%":
            return BinaryOpKind.MOD
        elif op == "//":
            return BinaryOpKind.INTEGER_DIV
        elif op == "+":
            return BinaryOpKind.PLUS
        elif op == "_":
            return BinaryOpKind.MINUS
        elif op == "<<":
            return BinaryOpKind.SHIFT_LEFT
        elif op == ">>":
            return BinaryOpKind.SHIFT_RIGHT
        elif op == "&":
            return BinaryOpKind.BINARY_AND
        elif op == "||":
            return BinaryOpKind.BINARY_XOR
        elif op == "|":
            return BinaryOpKind.BINARY_OR
        elif op == "<":
            return BinaryOpKind.LESSER_THAN
        elif op == ">":
            return BinaryOpKind.GREATER_THAN
        elif op == "==":
            return BinaryOpKind.EQUAL
        elif op == ">=":
            return BinaryOpKind.EQUAL_LESSER_THAN
        elif op == "<=":
            return BinaryOpKind.EQUAL_GREATER_THAN
        elif op == "!=":
            return BinaryOpKind.NOT_EQUAL
        elif op == "in":
            return BinaryOpKind.IN
        elif op == "not" and rem_op == "in":
            return BinaryOpKind.NOT_IN
        elif op == "is" and rem_op == "not":
            return BinaryOpKind.IS_NOT
        elif op == "is":
            return BinaryOpKind.IS
        else:
            return None


class UnaryOpKind(Enum):
    """
    The different kinds of unary operators
    """

    PLUS = 0
    MINUS = 1
    BINARY_NOT = 2
    NOT = 3
    SQUARE = 4
    ROOT = 5

    @staticmethod
    def from_string(op):
        if op == "+":
            return UnaryOpKind.PLUS
        elif op == "-":
            return UnaryOpKind.MINUS
        elif op == "~":
            return UnaryOpKind.BINARY_NOT
        elif op == "not":
            return UnaryOpKind.NOT
        elif op == "²":
            return UnaryOpKind.SQUARE
        elif op == "√":
            return UnaryOpKind.ROOT
        else:
            return None


# Types related to ASTS
class ComprehensionType(Enum):
    """
    Different types of comprehension expression
    """

    GENERATOR = 0
    LIST = 1
    DICT = 2
    SET = 3


class AST:
    """
    NOTE:
        We really only need our AST classes to inherit from this one class. We don't need a
        complicated type hierarchy since the Parser already ensures a StatementExpr can't be
        passed where an ExprAST is expected, for example.
    """

    def __repr__(self):
        type_name = type(self).__name__
        fields = vars(self)
        formatted_fields = ", ".join(
            ["=".join([key, repr(value)]) for key, value in fields.items()]
        )

        return f"{type_name}({formatted_fields})"

    def __eq__(self, other):
        return vars(self) == vars(other) if isinstance(other, AST) else None


class Null(AST):
    """
    This class is useful for creating AST shim that can to be ignored.
    `parser.opt`, a method that matches zero or one occurence of a sequence,
    returns a Null if there is zero occurence of a sequence to show it is still valid.
    """

    pass


class Newline(AST):
    def __init__(self, index):
        self.index = index


class Indent(AST):
    def __init__(self, index):
        self.index = index


class Dedent(AST):
    def __init__(self, index):
        self.index = index


class Identifier(AST):
    def __init__(self, index):
        self.index = index


class Integer(AST):
    def __init__(self, index):
        self.index = index


class Float(AST):
    def __init__(self, index):
        self.index = index


class ImagInteger(AST):
    def __init__(self, index):
        self.index = index


class ImagFloat(AST):
    def __init__(self, index):
        self.index = index


class String(AST):
    def __init__(self, index):
        self.index = index


class StringList(AST):
    def __init__(self, strings):
        self.strings = strings


class ByteString(AST):
    def __init__(self, index):
        self.index = index


class PrefixedString(AST):
    def __init__(self, index):
        self.index = index


class Operator(AST):
    def __init__(self, op, rem_op=None):
        self.op = op
        self.rem_op = rem_op  # For when operator spans two tokens like `not in`


class UnaryExpr(AST):
    def __init__(self, expr, op):
        self.expr = expr
        self.op = op


class BinaryExpr(AST):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class FuncParam(AST):
    def __init__(self, name, type_annotation=None, default_value_expr=None):
        self.name = name
        self.type_annotation = type_annotation
        self.default_value_expr = default_value_expr


class PositionalParamsSeparator(AST):
    def __init__(self):
        pass


class FuncParams(AST):
    def __init__(
        self,
        params,
        tuple_rest_param=None,
        keyword_only_params=[],
        named_tuple_rest_param=None,
    ):
        self.params = params
        self.tuple_rest_param = tuple_rest_param
        self.keyword_only_params = keyword_only_params
        self.named_tuple_rest_param = named_tuple_rest_param


class Function(AST):
    def __init__(
        self,
        name,
        body,
        params=[],
        return_type_annotation=None,
        generics_annotation=None,
        is_async=False,
        decorators=[],
    ):
        self.name = name
        self.body = body
        self.params = params
        self.return_type_annotation = return_type_annotation
        self.generics_annotation = generics_annotation
        self.is_async = is_async
        self.decorators = decorators


class TupleRestExpr(AST):
    def __init__(self, expr):
        self.expr = expr


class NamedTupleRestExpr(AST):
    def __init__(self, expr):
        self.expr = expr


class Comprehension(AST):
    def __init__(
        self,
        expr,
        var_expr,
        iterable_expr,
        key_expr=None,
        comprehension_type=ComprehensionType.GENERATOR,
        where_expr=None,
        is_async=False,
        nested_comprehension=None,
    ):
        self.expr = expr
        self.key_expr = key_expr
        self.var_expr = var_expr
        self.iterable_expr = iterable_expr
        self.comprehension_type = comprehension_type
        self.where_expr = where_expr
        self.is_async = is_async
        self.nested_comprehension = nested_comprehension


class Yield(AST):
    def __init__(self, exprs, is_yield_from=False):
        self.exprs = exprs
        self.is_yield_from = is_yield_from


class Dict(AST):
    def __init__(self, key_value_pairs=[]):
        self.key_value_pairs = key_value_pairs


class Set(AST):
    def __init__(self, exprs=[]):
        self.exprs = exprs


class List(AST):
    def __init__(self, exprs=[]):
        self.exprs = exprs


class Tuple(AST):
    def __init__(self, exprs=[]):
        self.exprs = exprs


class SubscriptIndex(AST):
    def __init__(self, from_expr=None, skip_expr=None, to_expr=None):
        self.from_expr = from_expr
        self.skip_expr = skip_expr
        self.to_expr = to_expr


class Subscript(AST):
    def __init__(self, expr, indices):
        self.expr = expr
        self.indices = indices


class Call(AST):
    def __init__(self, expr, arguments):
        self.expr = expr
        self.arguments = arguments


class Field(AST):
    def __init__(self, expr, field):
        self.expr = expr
        self.field = field


class Bool(AST):
    def __init__(self, is_true):
        self.is_true = is_true


class NoneLiteral(AST):
    pass


class Argument(AST):
    def __init__(self, expr, name=None):
        self.expr = expr
        self.name = name


class AwaitedExpr(AST):
    def __init__(self, expr):
        self.expr = expr


class WithArgument(AST):
    def __init__(self, expr, name=None):
        self.expr = expr
        self.name = name


class WithStatement(AST):
    def __init__(self, arguments, body, is_async=False):
        self.arguments = arguments
        self.body = body
        self.is_async = is_async


class Except(AST):
    def __init__(self, argument, name, body):
        self.argument = argument
        self.name = name
        self.body = body


class TryStatement(AST):
    def __init__(
        self, try_body, except_clauses=None, else_body=None, finally_body=None
    ):
        self.try_body = try_body
        self.except_clauses = except_clauses
        self.else_body = else_body
        self.finally_body = finally_body


class ForStatement(AST):
    def __init__(
        self, var_expr, iterable_expr, body, else_body, where_expr=None, is_async=False
    ):
        self.var_expr = var_expr
        self.iterable_expr = iterable_expr
        self.body = body
        self.else_body = else_body
        self.where_expr = where_expr
        self.is_async = is_async


class WhileStatement(AST):
    def __init__(self, cond_expr, body, else_body, where_expr=None):
        self.cond_expr = cond_expr
        self.body = body
        self.else_body = else_body
        self.where_expr = where_expr


class Elif(AST):
    def __init__(self, cond_expr, body):
        self.cond_expr = cond_expr
        self.body = body


class IfStatement(AST):
    def __init__(self, cond_expr, if_body, elifs=[], else_body=None):
        self.cond_expr = cond_expr
        self.if_body = if_body
        self.elifs = elifs
        self.else_body = else_body


class IfExpr(AST):
    def __init__(self, if_expr, cond_expr, else_expr):
        self.if_expr = if_expr
        self.cond_expr = cond_expr
        self.else_expr = else_expr


class NamedExpression(AST):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class GenericType(AST):
    def __init__(self, generic_type, specialization_types):
        self.generic_type = generic_type
        self.specialization_types = specialization_types


class FunctionType(AST):
    def __init__(self, return_type, param_types=[]):
        self.return_type = return_type
        self.param_types = param_types


class ListType(AST):
    def __init__(self, types):
        self.types = types


class TupleType(AST):
    def __init__(self, types):
        self.types = types


class Type(AST):
    def __init__(self, type):
        self.type = type


class IntersectionType(AST):
    def __init__(self, types):
        self.types = types


class UnionType(AST):
    def __init__(self, types):
        self.types = types


class GenericsAnnotation(AST):
    def __init__(self, types):
        self.types = types


class Class(AST):
    def __init__(
        self, name, body, parent_classes=[], generics_annotation=None, decorators=[]
    ):
        self.name = name
        self.body = body
        self.parent_classes = parent_classes
        self.generics_annotation = generics_annotation
        self.decorators = decorators


class ListLHS(AST):
    def __init__(self, exprs):
        self.exprs = exprs


class TupleLHS(AST):
    def __init__(self, exprs):
        self.exprs = exprs


class Globals(AST):
    def __init__(self, names):
        self.names = names


class NonLocals(AST):
    def __init__(self, names):
        self.names = names


class AssertStatement(AST):
    def __init__(self, cond_expr, message_expr=None):
        self.cond_expr = cond_expr
        self.message_expr = message_expr


class DelStatement(AST):
    def __init__(self, names):
        self.names = names


class PassStatement(AST):
    def __init__(self):
        pass


class BreakStatement(AST):
    def __init__(self):
        pass


class ContinueStatement(AST):
    def __init__(self):
        pass


class ReturnStatement(AST):
    def __init__(self, exprs=[]):
        self.exprs = exprs


class RaiseStatement(AST):
    def __init__(self, expr=None, from_expr=None):
        self.expr = expr
        self.from_expr = from_expr


class AssignmentStatement(AST):
    def __init__(self, lhses, assignment_op, value_expr, type_annotation=None):
        self.lhses = lhses
        self.assignment_op = assignment_op
        self.value_expr = value_expr
        self.type_annotation = type_annotation


class MainPath(AST):
    def __init__(self, path_names, alias=None, relative_level=0):
        self.path_names = path_names
        self.relative_level = relative_level
        self.alias = alias


class SubPath(AST):
    def __init__(self, path_names, alias=None, is_import_all=False):
        self.is_import_all = is_import_all
        self.path_names = path_names
        self.alias = alias


class ImportStatement(AST):
    def __init__(self, main_path, sub_paths):
        self.main_path = main_path
        self.sub_paths = sub_paths


class Decorator(AST):
    def __init__(self, path, arguments):
        self.path = path
        self.arguments = arguments
