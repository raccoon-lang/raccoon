"""
A packrat parser for parsing Raccoon's syntax.

Check `compiler/parser/parser.grammar` for the language's parser grammar specification.

GUIDELINES:
    - Add/edit corresponding rule in grammar file if you are adding/editing a parser function.
    - Generally before adding/changing your parser function check if you can resuse the code of
      a similar implementation in the code.
    - AST constructors are called with positional arguments. Don't use named arguments, args or
      kwargs.
    - The `is not None` chack is not needed in a lot of places, but it should be added for
      convention and to prevent ocassional cases where they are needed and might lead to bugs.
"""

from functools import wraps
from ..lexer.lexer import TokenKind
from .ast import (
    Null,
    Newline,
    Indent,
    Dedent,
    Identifier,
    Integer,
    Float,
    ImagInteger,
    ImagFloat,
    String,
    ByteString,
    PrefixedString,
    Operator,
    UnaryExpr,
    BinaryExpr,
    IfExpr,
    FuncParam,
    PositionalParamsSeparator,
    FuncParams,
    Function,
    TupleRestExpr,
    NamedTupleRestExpr,
    Comprehension,
    ComprehensionType,
    Yield,
    Dict,
    Set,
    List,
    SubscriptIndex,
    Subscript,
    Tuple,
    StringList,
    NoneLiteral,
    Bool,
    Argument,
    Field,
    Call,
    AwaitedExpr,
    WithArgument,
    WithStatement,
    Except,
    TryStatement,
    Elif,
    IfStatement,
    WhileStatement,
    ForStatement,
    NamedExpression,
    FunctionType,
    ListType,
    TupleType,
    GenericType,
    IntersectionType,
    UnionType,
    Type,
    GenericsAnnotation,
    Class,
    ListLHS,
    TupleLHS,
    Globals,
    NonLocals,
    AssertStatement,
    DelStatement,
    PassStatement,
    BreakStatement,
    ContinueStatement,
    ReturnStatement,
    RaiseStatement,
    AssignmentStatement,
    MainPath,
    SubPath,
    ImportStatement,
    Decorator
)


class ParserError(Exception):
    """ Represents the error the parser can raise """

    def __init__(self, message, row, column):
        super().__init__(f"(line: {row}, col: {column}) {message}")
        self.message = message  # Added because it is missing after super init
        self.row = row
        self.column = column

    def __repr__(self):
        return (
            f'ParserError(message="{self.message}", row={self.row}'
            f", column={self.column})"
        )


class Parser:
    """
    A recursive descent parser with memoizing feature basically making it a packrat parser.

    It is designed to have the following properties:
    - Results of all paths taken are memoized.
    - A parser function result should not hold values, but references to token elements.

    TODO:
        - Be sure to discard cache after getting program AST
        - Discard irrelevant tokens
            - Walk through program AST
            - Move relevant tokens into a dictionary with index keys
            - Discard old tokens
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.tokens_length = len(tokens)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.cache = {}
        self.combinator_data = {}
        self.revert_data = (self.cursor, *self.get_line_info())

    def __repr__(self):
        return f"{type(self).__name__}{vars(self)}"

    @staticmethod
    def from_code(code):
        """
        Creates a parser from code.
        """

        from ..lexer.lexer import Lexer

        tokens = Lexer(code).lex()

        return Parser(tokens)

    def get_line_info(self):
        return self.row, self.column

    def revert(self, cursor, row, column):
        """
        Revert parser state
        """

        self.cursor = cursor
        self.row = row
        self.column = column

    def eat_token(self):
        """
        Returns the next token and its index then advances the cursor position
        """

        if self.cursor + 1 < self.tokens_length:
            self.cursor += 1
            token = self.tokens[self.cursor]

            # Update row and column
            self.column = token.column
            self.row = token.row

            return (self.cursor, token)

        return None

    def consume_string(self, string):
        """
        Consumes and checks if next token holds the same data as `string`.
        Advances cursor only when next token matches string.
        """

        if self.cursor + 1 < self.tokens_length:
            token = self.tokens[self.cursor + 1]

            if token.data == string:
                self.cursor += 1
                self.column = token.column
                self.row = token.row

                return self.cursor

        return None

    def backtrackable(parser):
        """
        A decorator that changes the parser state to it's original state just before a parser
        function failed (i.e. returns None).
        """

        @wraps(parser)
        def wrapper(self, *args):
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            parser_result = parser(self, *args)

            # Revert parser state
            if parser_result is None:
                self.revert(cursor, row, column)

            return parser_result

        return wrapper

    def memoize(parser):
        """
        A decorator that memoizes the result of a recursive decent parser.
        It also reuses cache if available before running the parser.
        """

        @wraps(parser)
        def wrapper(self, *args):
            # Get info about parser function.
            cursor = self.cursor
            parser_name = parser.__name__

            # Check cache if parser function result is already saved
            cursor_key = self.cache.get(cursor)

            if cursor_key:
                # Catching KeyError here because, None is a valid result value.
                try:
                    result = cursor_key[parser_name]
                    self.cursor = result[1]
                    return result[0]
                except KeyError:
                    pass

            # Otherwise go ahead and parse, then cache result
            parser_result = parser(self, *args)
            skip = self.cursor

            if not cursor_key:
                self.cache[cursor] = {parser_name: (parser_result, skip)}
            else:
                # Catching KeyError here because, None is a valid result value.
                try:
                    cursor_key[parser_name]
                except KeyError:
                    self.cache[cursor][parser_name] = (parser_result, skip)

            return parser_result

        return wrapper

    def consume(self, *args, result_type):
        """
        Checks and consumes the next token if it is of the TokenKinds passed to the function
        """

        payload = self.eat_token()

        if payload and payload[1].kind in args:
            return result_type(payload[0])

        return None

    def register_revert(self):
        """
        Store state to which to revert parser at a later time.
        """

        self.revert_data = (self.cursor, *self.get_line_info())

    def revertable(self, expr):
        """
        Reverts parser state to previously registered revert state.

        This is usually applied to an optional compound sub rule in a production like
        `(',' expr)*` in `expr (',' expr)*`.

        Without this function, the parser can halt after eating token `','` because it cannot
        match `expr` and since the sub rule is optional, the parser won't fail but the already
        eaten `','` will become unavailable to the next parser.
        """
        if not expr:
            self.revert(*self.revert_data)
        else:
            # This is needed for while/for loops, otherwise the revert state will
            # be stuck at the state before the first iteration. We want the parser
            # state to update on each iteration.
            self.register_revert()

        return expr

    @backtrackable
    @memoize
    def newline(self):
        """
        Parses normal string literals
        """

        return self.consume(TokenKind.NEWLINE, result_type=Newline)

    @backtrackable
    @memoize
    def indent(self):
        """
        Parses byte string literals
        """

        return self.consume(TokenKind.INDENT, result_type=Indent)

    @backtrackable
    @memoize
    def dedent(self):
        """
        Parses prefixed string literals
        """

        return self.consume(TokenKind.DEDENT, result_type=Dedent)

    @backtrackable
    @memoize
    def identifier(self):
        """
        Parses identifiers
        """

        return self.consume(TokenKind.IDENTIFIER, result_type=Identifier)

    @backtrackable
    @memoize
    def integer(self):
        """
        Parses integer literals
        """

        return self.consume(
            TokenKind.DEC_INTEGER,
            TokenKind.HEX_INTEGER,
            TokenKind.BIN_INTEGER,
            TokenKind.OCT_INTEGER,
            result_type=Integer,
        )

    @backtrackable
    @memoize
    def float(self):
        """
        Parses floating point literals
        """

        return self.consume(TokenKind.DEC_FLOAT, result_type=Float)

    @backtrackable
    @memoize
    def imag_integer(self):
        """
        Parses imaginary integer literals
        """

        return self.consume(TokenKind.DEC_INTEGER_IMAG, result_type=ImagInteger)

    @backtrackable
    @memoize
    def imag_float(self):
        """
        Parses imaginary float literals
        """

        return self.consume(TokenKind.DEC_FLOAT_IMAG, result_type=ImagFloat)

    @backtrackable
    @memoize
    def string(self):
        """
        Parses normal string literals
        """

        return self.consume(TokenKind.STRING, result_type=String)

    @backtrackable
    @memoize
    def byte_string(self):
        """
        Parses byte string literals
        """

        return self.consume(TokenKind.BYTE_STRING, result_type=ByteString)

    @backtrackable
    @memoize
    def prefixed_string(self):
        """
        Parses prefixed string literals
        """

        return self.consume(TokenKind.PREFIXED_STRING, result_type=PrefixedString)

    @backtrackable
    @memoize
    def power_expr(self):
        """
        rule = '√'? atom_expr ('^' unary_expr | '²')? [right associative]
        """

        root = self.consume_string("√")
        result = self.atom_expr()

        if result is None:
            return None

        self.register_revert()
        if (self.revertable(
            (power := self.consume_string("^")) is not None
            and (unary_expr := self.integer()) is not None
        )):
            result = BinaryExpr(result, Operator(power), unary_expr)
        elif (square := self.consume_string("²")) is not None:
            result = UnaryExpr(result, Operator(square))

        if root is not None:
            result = UnaryExpr(result, Operator(root))

        return result

    @backtrackable
    @memoize
    def unary_expr(self):
        """
        rule = ('+' | '-' | '~')* power_expr [right associative]
        """

        unary_ops = []
        while True:
            if (unary_op := self.consume_string("+")) is None:
                if (unary_op := self.consume_string("-")) is None:
                    if (unary_op := self.consume_string("~")) is None:
                        break

            unary_ops.append(Operator(unary_op))

        result = self.power_expr()

        if result is None:
            return None

        for unary_op in reversed(unary_ops):
            result = UnaryExpr(result, unary_op)

        return result

    def binary_expr(self, operand_parser, operators):
        """
        Helper function for parsing left-associative binary expressions.
        NOTE:
            Not bactrackable because it is called once by backtrackable functions
        """

        result = operand_parser()

        while True:
            operator = None
            rem_operator = None

            for i in operators:
                if type(i) == tuple:
                    # Fetch the two elements in tuple.
                    operator = self.consume_string(i[0])
                    rem_operator = self.consume_string(i[1])
                    if operator is not None or rem_operator is not None:
                        break
                else:
                    if (operator := self.consume_string(i)) is not None:
                        break

            if operator is None:
                break

            rhs = operand_parser()

            if rhs is None:
                break

            result = BinaryExpr(result, Operator(operator, rem_operator), rhs)

        return result

    @backtrackable
    @memoize
    def mul_expr(self):
        """
        rule = unary_expr (('*' | '@' | '/' | '%' | '//') unary_expr)* [left associative]
        """

        return self.binary_expr(self.unary_expr, ["*", "@", "/", "%", "//"])

    @backtrackable
    @memoize
    def sum_expr(self):
        """
        rule = mul_expr (('+' | '-') mul_expr)* [left associative]
        """

        return self.binary_expr(self.mul_expr, ["+", "-"])

    @backtrackable
    @memoize
    def shift_expr(self):
        """
        rule = sum_expr (('<<' | '>>') sum_expr)* [left associative]
        """

        return self.binary_expr(self.sum_expr, ["<<", ">>"])

    @backtrackable
    @memoize
    def and_expr(self):
        """
        rule = shift_expr ('&' shift_expr)* [left associative]
        """

        return self.binary_expr(self.shift_expr, ["&"])

    @backtrackable
    @memoize
    def xor_expr(self):
        """
        rule = and_expr ('||' and_expr)* [left associative]
        """

        return self.binary_expr(self.and_expr, ["||"])

    @backtrackable
    @memoize
    def or_expr(self):
        """
        rule = xor_expr ('|' xor_expr)* [left associative]
        """

        return self.binary_expr(self.xor_expr, ["|"])

    @backtrackable
    @memoize
    def comparison_expr(self):
        """
        comparison_op =
            | '<' | '>' | '==' | '>=' | '<=' | '!=' | 'in' | 'not' 'in' | 'is' 'not' | 'is'

        rule = or_expr (comparison_op or_expr)* [left associative]
        """

        return self.binary_expr(
            self.or_expr,
            [
                "<",
                ">",
                "==",
                ">=",
                "<=",
                "!=",
                "in",
                ("not", "in"),
                ("is", "not"),
                "is",
            ],
        )

    @backtrackable
    @memoize
    def not_test(self):
        """
        rule = 'not'* comparison_expr [left associative]
        """

        result = self.comparison_expr()

        while True:
            if self.consume_string("not") is None:
                break

            result = UnaryExpr(result, Operator(not_op))

        return result

    @backtrackable
    @memoize
    def and_test(self):
        """
        rule = not_test ('and' not_test)* [left associative]
        """

        return self.binary_expr(self.not_test, ["and"])

    @backtrackable
    @memoize
    def or_test(self):
        """
        rule = and_test ('or' and_test)* [left associative]
        """

        return self.binary_expr(self.and_test, ["or"])

    @backtrackable
    @memoize
    def test(self):
        """
        rule = or_test ('if' expr 'else' expr)? [left associative]
        """

        result = self.or_test()

        if (
            result is not None
            and (self.consume_string("if") is not None)
            and (cond := self.expr()) is not None
            and self.consume_string("else") is not None
            and (else_expr := self.expr()) is not None
        ):
            result = IfExpr(result, cond, else_expr)

        return result

    @backtrackable
    @memoize
    def named_expr(self):
        """
        rule = identifier ":=" test
        """

        if (
            (identifier := self.identifier()) is not None
            and self.consume_string(":=") is not None
            and(test := self.test()) is not None
        ):
            return NamedExpression(identifier, test)

        return None

    @backtrackable
    @memoize
    def lambda_param(self):
        """
        rule = identifier ('=' expr)?
        """

        identifier = self.identifier()

        if identifier is None:
            return None

        result = FuncParam(identifier)

        self.register_revert()
        if (self.revertable(
            self.consume_string("=") is not None
            and (expr := self.expr()) is not None
        )):
            result.default_value_expr = expr

        return result

    @backtrackable
    @memoize
    def lambda_params(self):
        """
        rule =
            | '(' func_params? ')'
            | lambda_param (',' lambda_param)* ('/', lambda_param (',' lambda_param)*)? (',' '*'
              lambda_param (',' lambda_param)*)? (',' '**' lambda_param)? ','?
            | '*' lambda_param (',' lambda_param)* (',' '**' lambda_param)? ','?
            | '**' lambda_param ','?
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            self.consume_string("(") is not None
            and (func_params := self.func_params()) is not None
            and self.consume_string(")") is not None
        ):
            return func_params

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (param := self.lambda_param()) is not None:
            params = [param]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (param := self.lambda_param()) is not None
            )):
                params.append(param)

            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("/") is not None
            )):
                params.append(PositionalParamsSeparator())

                self.register_revert()
                while (self.revertable(
                    self.consume_string(",") is not None
                    and (param := self.lambda_param()) is not None
                )):
                    params.append(param)

            tuple_rest_param = None
            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("*") is not None
                and (param := self.lambda_param()) is not None
            )):
                tuple_rest_param = param

            keyword_only_params = []
            if tuple_rest_param:
                self.register_revert()
                while (self.revertable(
                    self.consume_string(",") is not None
                    and (param := self.lambda_param()) is not None
                )):
                    keyword_only_params.append(param)

            named_tuple_rest_param = None
            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("**") is not None
                and (param := self.lambda_param()) is not None
            )):
                named_tuple_rest_param = param

            return FuncParams(
                params, tuple_rest_param, keyword_only_params, named_tuple_rest_param
            )

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("*") is not None
            and (tuple_rest_param := self.lambda_param()) is not None
        ):
            named_tuple_params = []
            if tuple_rest_param:
                self.register_revert()
                while (self.revertable(
                    self.consume_string(",") is not None
                    and (param := self.lambda_param()) is not None
                )):
                    named_tuple_params.append(param)

            named_tuple_rest_param = None
            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("**") is not None
                and (param := self.lambda_param()) is not None
            )):
                named_tuple_rest_param = param

            return FuncParams(
                None, tuple_rest_param, named_tuple_params, named_tuple_rest_param
            )

        # FOURTH ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("**") is not None
            and (named_tuple_rest_param := self.lambda_param()) is not None
        ):
            return FuncParams(None, None, None, named_tuple_rest_param)

        return None

    @backtrackable
    @memoize
    def lambda_expr_def(self):
        """
        rule = 'lambda' lambda_params? ':' expr
        """

        if self.consume_string("lambda") is not None:
            params = params if (params := self.lambda_params()) else []

            if (
                self.consume_string(":") is not None
                and (expr := self.expr()) is not None
            ):
                return Function(None, [expr], params)

        return None

    @backtrackable
    @memoize
    def expr(self):
        """
        rule = lambda_expr_def | test
        """

        result = self.lambda_expr_def()
        if result is None:
            result = self.test()

        return result

    @backtrackable
    @memoize
    def exprs(self):
        """
        rule = expr (',' expr)* ','?
        """

        result = self.expr()

        if result is None:
            return None

        exprs = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (expr := self.expr()) is not None
        )):
            exprs.append(expr)

        self.consume_string(",")

        return exprs if len(exprs) > 1 else result

    @backtrackable
    @memoize
    def rest_expr(self):
        """
        rule = ('*' | '**')? expr
        """

        is_tuple_rest = None

        if self.consume_string("*"):
            is_tuple_rest = True
        elif self.consume_string("**"):
            is_tuple_rest = False

        result = self.expr()

        if result is None:
            return None

        if is_tuple_rest is True:
            result = TupleRestExpr(result)
        elif is_tuple_rest is False:
            result = NamedTupleRestExpr(result)

        return result

    @backtrackable
    @memoize
    def rest_exprs(self):
        """
        rule = rest_expr (',' rest_expr)* ','?
        """

        result = self.rest_expr()

        if result is None:
            return None

        exprs = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (rest_expr := self.rest_expr()) is not None
        )):
            exprs.append(rest_expr)

        self.consume_string(",")

        return exprs if len(exprs) > 1 else result

    @backtrackable
    @memoize
    def lambda_block_def(self):
        """
        rule = 'lambda' lambda_params? ':' indent statement+ dedent
        """

        if self.consume_string("lambda") is not None:
            params = params if (params := self.lambda_params()) else []

            if (
                self.consume_string(":") is not None
                and self.indent() is not None
            ):
                statements = []
                while (statement := self.statements()) is not None:
                    statements.append(statement)

                # There should be at least an expression.
                # TODO: Raise error if block has dedent but no expression.
                if self.dedent() is not None and len(expr) > 0:
                    return Function(None, statements, params)

        return None

    @backtrackable
    @memoize
    def indentable_expr(self):
        """
        rule =
            | lambda_block_def
            | expr
        """

        result = self.lambda_block_def()
        if result is None:
            result = self.expr()

        return result

    @backtrackable
    @memoize
    def indentable_exprs(self):
        """
        rule = indentable_expr (',' indentable_expr)* ','?
        """

        result = self.indentable_expr()

        if result is None:
            return None

        exprs = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (indentable_expr := self.indentable_expr()) is not None
        )):
            exprs.append(indentable_expr)

        self.consume_string(",")

        return exprs if len(exprs) > 1 else result

    @backtrackable
    @memoize
    def rest_indentable_expr(self):
        """
        rule = ('*' | '**')? indentable_expr
        """

        is_tuple_rest = None

        if self.consume_string("*"):
            is_tuple_rest = True
        elif self.consume_string("**"):
            is_tuple_rest = False

        result = self.indentable_expr()

        if result is None:
            return None

        if is_tuple_rest is True:
            result = TupleRestExpr(result)
        elif is_tuple_rest is False:
            result = NamedTupleRestExpr(result)

        return result

    @backtrackable
    @memoize
    def rest_indentable_exprs(self):
        """
        rule = rest_indentable_expr (',' rest_indentable_expr)* ','?
        """

        result = self.rest_indentable_expr()

        if result is None:
            return None

        exprs = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (rest_expr := self.rest_indentable_expr()) is not None
        )):
            exprs.append(rest_expr)

        self.consume_string(",")

        return exprs if len(exprs) > 1 else result

    @backtrackable
    @memoize
    def named_expr_or_test(self):
        """
        rule =
            | named_expr
            | test
        """

        if (named_expr := self.named_expr()) is not None:
            return named_expr

        if (test := self.test()) is not None:
            return test

        return None

    @backtrackable
    @memoize
    def comprehension_where(self):
        """
        rule = 'where' (named_expr | indentable_exprs)
        """

        if self.consume_string("where") is not None:
            if (named_expr := self.indentable_expr()) is not None:
                return named_expr

            if (indentable_expr := self.indentable_expr()) is not None:
                return indentable_expr

        return None

    @backtrackable
    @memoize
    def sync_comprehension_for(self):
        """
        rule = 'for' for_lhs 'in' indentable_expr comprehension_where?
        """

        result = None

        if (
            self.consume_string("for") is not None
            and (var_expr := self.for_lhs()) is not None
            and self.consume_string("in") is not None
            and (iterable_expr := self.indentable_expr()) is not None
        ):
            result = Comprehension(None, var_expr, iterable_expr)

            if (comprehension_where := self.comprehension_where()):
                result.where_expr = comprehension_where

        return result

    @backtrackable
    @memoize
    def comprehension_for(self):
        """
        rule = 'async'? sync_comprehension_for ('async'? sync_comprehension_for)*
        """

        is_async = self.consume_string("async") is not None
        result = self.sync_comprehension_for()

        if result is None:
            return None

        result.is_async = is_async

        temp_result = result
        while True:
            self.register_revert()
            is_async = self.revertable(self.consume_string("async") is None)
            if (nested_comprehension := self.sync_comprehension_for()) is not None:
                temp_result.nested_comprehension = nested_comprehension
                temp_result.is_async = is_async
                temp_result = temp_result.nested_comprehension
                continue

            break

        return result

    @backtrackable
    @memoize
    def yield_argument(self):
        """
        rule =
            | 'from' indentable_expr
            | indentable_exprs
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            self.consume_string("from") is not None
            and (indentable_expr := self.indentable_expr()) is not None
        ):
            return Yield([indentable_expr], is_yield_from=True)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        indentable_exprs = self.indentable_exprs()

        return Yield(indentable_exprs) if indentable_exprs is not None else None

    @backtrackable
    @memoize
    def yield_expr(self):
        """
        rule = 'yield' yield_argument?
        """

        result = None

        if (yield_ := self.consume_string("yield")) is not None:
            if (yield_argument := self.yield_argument()) is not None:
                return yield_argument

            result = Yield([])

        return result

    @backtrackable
    @memoize
    def expr_suite(self):
        """
        rule =
            | rest_indentable_expr
            | indent rest_indentable_expr dedent
        """

        # FIRST ALTERNATIVE
        if (rest_indentable_expr := self.rest_indentable_expr()) is not None:
            return rest_indentable_expr

        # SECOND ALTERNATIVE
        if (
            self.indent() is not None
            and (rest_indentable_expr := self.rest_indentable_expr()) is not None
            and self.dedent() is not None
        ):
            return rest_indentable_expr

        return None

    @backtrackable
    @memoize
    def indentable_exprs_or_comprehension(self):
        """
        rule =
            | (named_expr | rest_indentable_expr) comprehension_for
            | (named_expr | rest_indentable_exprs)
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        if (named_expr := self.named_expr()) is not None:
            if (comprehension_for := self.comprehension_for()) is not None:
                comprehension_for.expr = named_expr
                return comprehension_for

            return named_expr

        self.revert(cursor, row, column)
        if (rest_indentable_expr := self.rest_indentable_expr()) is not None:
            if (comprehension_for := self.comprehension_for()) is not None:
                comprehension_for.expr = rest_indentable_expr
                return comprehension_for

        self.revert(cursor, row, column)
        if (rest_indentable_exprs := self.rest_indentable_exprs()) is not None:
            return rest_indentable_exprs

        return None

    @backtrackable
    @memoize
    def dict_or_set(self):
        """
        rule =
            | test ':' expr_suite comprehension_for
            | test ':' expr_suite (',' test ':' expr_suite)* ','?
            | indentable_exprs_or_comprehension
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            (test := self.test()) is not None
            and self.consume_string(":") is not None
            and (expr_suite := self.expr_suite()) is not None
            and (comprehension_for := self.comprehension_for()) is not None
        ):
            comprehension_for.key_expr = test
            comprehension_for.expr = expr_suite
            comprehension_for.comprehension_type = ComprehensionType.DICT
            return comprehension_for

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            (test := self.test()) is not None
            and self.consume_string(":") is not None
            and (expr_suite := self.expr_suite()) is not None
        ):
            key_value_pairs = [(test, expr_suite)]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (test := self.test()) is not None
                and self.consume_string(":") is not None
                and (expr_suite := self.expr_suite()) is not None
            )):
                key_value_pairs.append((test, expr_suite))

            self.consume_string(',')

            return Dict(key_value_pairs)

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (expr := self.indentable_exprs_or_comprehension()) is not None:
            if type(expr) == Comprehension:
                expr.comprehension_type = ComprehensionType.SET
            Set(expr)
            return expr

        return None

    @backtrackable
    @memoize
    def subscript_index(self):
        """
        rule =
            | test? ':' test? (':' test?)?
            | test
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        from_expr = self.test()

        # FIRST ALTERNATIVE
        if self.consume_string(":") is not None:
            skip_expr = self.test()  # Can either be a skip_expr or to_expr
            to_expr = None
            second_colon = None

            if (second_colon := self.consume_string(":")) is not None:
                to_expr = self.test()

            if to_expr is None and skip_expr is not None and second_colon is None:
                to_expr = skip_expr
                skip_expr = None

            return SubscriptIndex(from_expr, skip_expr, to_expr)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (test := self.test()) is not None:
            return SubscriptIndex(test)

        return None

    @backtrackable
    @memoize
    def subscript(self):
        """
        rule = subscript_index (',' subscript_index)* ','?
        """

        result = self.subscript_index()

        if result is None:
            return None

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (subscript_index := self.subscript_index()) is not None
        )):
            result.append(subscript_index)

        self.consume_string(",")

        return Subscript(None, result)

    @backtrackable
    @memoize
    def all_string(self):
        """
        rule =
            | string
            | byte_string
            | prefixed_string
        """

        if (
            (string := self.string()) is not None
            or (string := self.byte_string()) is not None
            or (string := self.prefixed_string()) is not None
        ):
            return string

        return None


    @backtrackable
    @memoize
    def atom(self):
        """
        rule =
            | '(' indentable_exprs_or_comprehension? ')'
            | '(' yield_expr ')'
            | '{' dict_or_set? '}'
            | '[' indentable_exprs_or_comprehension? ']'
            | float
            | all_string+
            | 'None'
            | 'True'
            | 'False'
            | identifier

        SPECIAL BEHAVIOR:
            When `string+` has more than one `string` it gets compiled as a stringlist.
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if self.consume_string("(") is not None:
            exprs = self.indentable_exprs_or_comprehension()
            if self.consume_string(")") is not None:
                result = exprs

                # Check if this can be a tuple expression like (), (expr,) or (x, y)
                # also check if its is a comperehension
                if exprs is None:
                    result = Tuple()
                elif self.tokens[self.cursor - 1].data == ",":
                    result = Tuple(exprs)
                elif type(exprs) == list:
                    result = Tuple(exprs)

                return result

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if self.consume_string("(") is not None:
            if (
                (yield_expr := self.yield_expr()) is not None
                and self.consume_string(")") is not None
            ):
                return yield_expr

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if self.consume_string("{") is not None:
            dict_or_set = self.dict_or_set()
            if self.consume_string("}") is not None:
                # Check if this can be an empty set
                return dict_or_set if dict_or_set is not None else Set()

        # FOURTH ALTERNATIVE
        self.revert(cursor, row, column)
        if self.consume_string("[") is not None:
            expr = self.indentable_exprs_or_comprehension()
            if self.consume_string("]") is not None:
                # Check if expression is a comprehension
                if type(expr) == Comprehension:
                    expr.comprehension_type = ComprehensionType.LIST
                    return expr

                # Check if this can be an empty list
                return List(expr) if expr is not None else List()


        # FIFTH ALTERNATIVE
        if (float_ := self.float()) is not None:
            return float_

        # SIXTH ALTERNATIVE
        if (integer := self.integer()) is not None:
            return integer

        # SEVENTH ALTERNATIVE
        if (string := self.all_string()) is not None:
            string_list = [string]
            while(more_string := self.string()) is not None:
                string_list.append(more_string)

            return StringList(string_list) if len(string_list) > 1 else string

        # EIGHTH ALTERNATIVE
        self.revert(cursor, row, column)
        if self.consume_string("None") is not None:
            return NoneLiteral()

        # NINETH ALTERNATIVE
        if self.consume_string("True") is not None:
            return Bool(True)

        # TENTH ALTERNATIVE
        if self.consume_string("False") is not None:
            return Bool(False)

        # ELEVENTH ALTERNATIVE
        self.revert(cursor, row, column)
        if (identifier := self.identifier()) is not None:
            return identifier

        return None

    @backtrackable
    @memoize
    def argument(self):
        """
        rule =
            | identifier '=' indentable_expr
            | rest_indentable_expr
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            (identifier := self.identifier()) is not None
            and self.consume_string("=") is not None
            and (indentable_expr := self.indentable_expr()) is not None
        ):
            return Argument(indentable_expr, identifier)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (rest_indentable_expr := self.rest_indentable_expr()) is not None:
            return Argument(rest_indentable_expr)

        return None

    @backtrackable
    @memoize
    def arguments(self):
        """
        rule = argument (',' argument)* ','?
        """

        result = self.argument()

        if result is None:
            return None

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (argument := self.argument()) is not None
        )):
            result.append(argument)

        self.consume_string(",")

        return result

    @backtrackable
    @memoize
    def atom_trailer(self):
        """
        rule =
            | '(' arguments? ')'
            | '[' subscript ']'
            | '.' identifier
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if self.consume_string("(") is not None:
            arguments = self.arguments()

            if self.consume_string(")"):
                return Call(None, arguments)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("[") is not None
            and (subscript := self.subscript()) is not None
            and self.consume_string("]") is not None
        ):
            return subscript

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string(".") is not None
            and (identifier := self.identifier()) is not None
        ):
            return Field(None, identifier)

        return None

    @backtrackable
    @memoize
    def atom_expr(self):
        """
        rule = 'await'? atom atom_trailer* [left associative]
        """

        is_await = self.consume_string("await") is not None
        result = self.atom()

        if result is None:
            return None

        while (atom_trailer := self.atom_trailer()) is not None:
            atom_trailer.expr = result
            result = atom_trailer

        if is_await:
            result = AwaitedExpr(result)

        return result

    @backtrackable
    @memoize
    def with_item(self):
        """
        rule = expr ('as' identifier)?
        """

        if (expr := self.expr()) is not None:
            identifier = None

            self.register_revert()
            if (self.revertable(
                self.consume_string("as") is not None
                and (identifier := self.identifier()) is not None
            )):
                identifier = identifier

            return WithArgument(expr, identifier)

        return None

    @backtrackable
    @memoize
    def with_statement(self):
        """
        rule = 'with' with_item (',' with_item)* ','? ':' func_suite
        """

        if (
            self.consume_string("with") is not None
            and (with_item := self.with_item()) is not None
        ):
            arguments = [with_item]

            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and (argument := self.with_item()) is not None
            )):
                arguments.append(argument)

            self.consume_string(",")

            if (
                self.consume_string(":") is not None
                and (body := self.func_suite()) is not None
            ):
                return With(arguments, body)

        return None

    @backtrackable
    @memoize
    def else_clause(self):
        """
        rule = 'else' ':' func_suite
        """

        if (
            self.consume_string("else") is not None
            and self.consume_string(":") is not None
            and (body := self.func_suite()) is not None
        ):
            return body

        return None

    @backtrackable
    @memoize
    def except_clause(self):
        """
        rule = 'except' identifier ('as' identifier)? ':' func_suite
        """

        if (
            self.consume_string("except") is not None
            and (identifier := self.identifier()) is not None
        ):
            alias = None

            self.register_revert()
            if (self.revertable(
                self.consume_string("as") is not None
                and (alias := self.identifier()) is not None
            )):
                alias = identifier

            if (
                self.consume_string(":") is not None
                and (body := self.func_suite()) is not None
            ):
                return Except(identifier, alias, body)

        return None

    @backtrackable
    @memoize
    def finally_clause(self):
        """
        rule = 'finally' ':' func_suite
        """

        if (
            self.consume_string("finally") is not None
            and self.consume_string(":") is not None
            and (body := self.func_suite()) is not None
        ):
            return func_suite

        return None

    @backtrackable
    @memoize
    def try_statement(self):
        """
        rule = 'try' ':' func_suite (except_clause+ else_clause? finally_clause? | finally_clause)
        """

        if (
            self.consume_string("try") is not None
            and self.consume_string(":") is not None
            and (try_body := self.func_suite()) is not None
        ):
            if (except_clause := self.except_clause()) is not None:
                except_clauses = [except_clause]

                while (except_clause := self.except_clause()) is not None:
                    except_clauses.append(except_clause)

                else_body = self.else_clause()
                finally_body = self.finally_clause()

                return TryExcept(try_body, except_clauses, else_body, finally_body)

            if (finally_body := self.finally_clause()) is not None:
                return TryExcept(try_body, finally_body=finally_body)

        return None

    @backtrackable
    @memoize
    def where_clause(self):
        """
        rule = 'where' (named_expr | expr)
        """

        if self.consume_string("where") is not None:
            if (named_expr := self.named_expr()) is not None:
                return named_expr

            if (expr := self.expr()) is not None:
                return expr

        return None

    @backtrackable
    @memoize
    def for_statement(self):
        """
        rule = 'for' for_lhs 'in' exprs where_clause? ':' func_suite else_clause?
        """

        if (
            self.consume_string("for") is not None
            and (lhs := self.for_lhs()) is not None
            and self.consume_string("in") is not None
            and (iterable_expr := self.exprs()) is not None
        ):
            where_clause = self.where_clause()

            if (
                self.consume_string(":") is not None
                and (body := self.func_suite()) is not None
            ):
                else_body = self.else_clause()
                return ForStatement(lhs, iterable_expr, body, else_body, where_clause)

        return None

    @backtrackable
    @memoize
    def while_statement(self):
        """
        rule = 'while' named_expr_or_test where_clause? ':' func_suite else_clause?
        """

        if (
            self.consume_string("while") is not None
            and (cond_expr := self.named_expr_or_test()) is not None
        ):
            where_clause = self.where_clause()

            if (
                self.consume_string(":") is not None
                and (body := self.func_suite()) is not None
            ):
                else_body = self.else_clause()
                return WhileStatement(cond_expr, body, else_body, where_clause)

        return None

    @backtrackable
    @memoize
    def elif_clause(self):
        """
        rule = 'elif' named_expr_or_test ':' func_suite
        """

        if (
            self.consume_string("elif") is not None
            and (cond_expr := self.named_expr_or_test()) is not None
            and self.consume_string(":") is not None
            and (body := self.func_suite()) is not None
        ):
            return Elif(cond_expr, body)

        return None

    @backtrackable
    @memoize
    def if_statement(self):
        """
        rule = 'if' named_expr_or_test ':' func_suite elif_clause* else_clause?
        """

        if (
            self.consume_string("if") is not None
            and (cond_expr := self.named_expr_or_test()) is not None
            and self.consume_string(":") is not None
            and (body := self.func_suite()) is not None
        ):
            elif_clauses = []

            while (elif_clause := self.elif_clause()) is not None:
                elif_clauses.append(elif_clause)

            else_clause = self.else_clause()

            return IfStatement(cond_expr, body, elif_clauses, else_clause)

        return None

    @backtrackable
    @memoize
    def generic_type(self):
        """
        rule = identifier '[' type_annotation, (',' type_annotation)* ','? ']'
        """

        if (
            (generic_type := self.identifier()) is not None
            and self.consume_string("[") is not None
            and (sepcialization_type := self.type_annotation()) is not None
        ):
            sepcialization_types = [sepcialization_type]

            self.register_revert()
            while(self.revertable(
                self.consume_string(",") is not None
                and (sepcialization_type := self.type_annotation()) is not None
            )):
                sepcialization_types.append(sepcialization_type)

            self.consume_string(",")

            if self.consume_string("]") is not None:
                return GenericType(generic_type, sepcialization_types)

        return None


    @backtrackable
    @memoize
    def function_type(self):
        """
        rule = '(' (type_annotation, (',' type_annotation)* ','?)? ')' '->' type_annotation
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        if (
            self.consume_string("(") is not None
            and (param_type := self.type_annotation()) is not None
        ):
            param_types = [param_type]

            self.register_revert()
            while(self.revertable(
                self.consume_string(",") is not None
                and (param_type := self.type_annotation()) is not None
            )):
                param_types.append(param_type)

            self.consume_string(",")

            if (
                self.consume_string(")") is not None
                and self.consume_string("->") is not None
                and (return_type := self.type_annotation()) is not None
            ):
                return FunctionType(return_type, param_types)

        self.revert(cursor, row, column)
        if (
            self.consume_string("(") is not None
            and self.consume_string(")") is not None
            and self.consume_string("->") is not None
            and (return_type := self.type_annotation()) is not None
        ):
            return FunctionType(return_type)


        return None

    @backtrackable
    @memoize
    def list_type(self):
        """
        rule = '[' type_annotation, (',' type_annotation)* ','? ']'
        """

        if (
            self.consume_string("[") is not None
            and (type_ := self.type_annotation()) is not None
        ):
            types = [type_]

            self.register_revert()
            while(self.revertable(
                self.consume_string(",") is not None
                and (type_ := self.type_annotation()) is not None
            )):
                types.append(type_)

            self.consume_string(",")

            if self.consume_string("]") is not None:
                return ListType(types)

        return None

    @backtrackable
    @memoize
    def tuple_type(self):
        """
        rule = '(' type_annotation, (',' type_annotation)* ','? ')'
        """

        if (
            self.consume_string("(") is not None
            and (type_ := self.type_annotation()) is not None
        ):
            types = [type_]

            self.register_revert()
            while(self.revertable(
                self.consume_string(",") is not None
                and (type_ := self.type_annotation()) is not None
            )):
                types.append(type_)

            self.consume_string(",")

            if self.consume_string(")") is not None:
                return TupleType(types)

        return None


    @backtrackable
    @memoize
    def intersection_type(self):
        """
        rule = atom_type ('&' atom_type)*
        """

        if (first_type := self.atom_type()) is not None:
            types = [first_type]

            self.register_revert()
            while(self.revertable(
                self.consume_string("&") is not None
                and (type_ := self.atom_type()) is not None
            )):
                types.append(type_)

            return IntersectionType(types) if len(types) > 1 else first_type

        return None

    @backtrackable
    @memoize
    def union_type(self):
        """
        rule = intersection_type ('|' intersection_type)*
        """

        if (first_type := self.intersection_type()) is not None:
            types = [first_type]

            self.register_revert()
            while(self.revertable(
                self.consume_string("|") is not None
                and (type_ := self.intersection_type()) is not None
            )):
                types.append(type_)

            return UnionType(types) if len(types) > 1 else first_type

        return None

    @backtrackable
    @memoize
    def atom_type(self):
        """
        rule =
            | function_type
            | list_type
            | tuple_type
            | generic_type
            | identifier
        """

        if (
            (type_ := self.function_type()) is not None
            or (type_ := self.list_type()) is not None
            or (type_ := self.tuple_type()) is not None
            or (type_ := self.generic_type()) is not None
        ):
            return type_

        if (type_ := self.identifier()) is not None:
            return Type(type_)

        return None

    @backtrackable
    @memoize
    def type_annotation(self):
        """
        rule = union_type
        """

        if (type_ := self.union_type()) is not None:
            return type_

        return None

    @backtrackable
    @memoize
    def identifiers(self):
        """
        rule = identifier, (',' identifier)* ','?
        """

        result = self.identifier()

        if result is None:
            return None

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (identifier := self.identifier()) is not None
        )):
            result.append(identifier)

        self.consume_string(",")

        return result

    @backtrackable
    @memoize
    def generics_annotation(self):
        """
        rule = '[' identifiers ']'
        """

        if (
            self.consume_string("[") is not None
            and (types := self.identifiers()) is not None
            and self.consume_string("]") is not None
        ):
            return GenericsAnnotation(types)

        return None

    @backtrackable
    @memoize
    def class_suite(self):
        """
        rule =
            | assignment_statement
            | indent (import_statement | assignment_statement | class_def | async_func_def | func_def | all_string)+ dedent

        SPECIAL BEHAVIOR:
            When `string+` has more than one `string` it gets compiled as a stringlist.
        """

        if (assignment_statement := self.assignment_statement()) is not None:
            return [assignment_statement]

        if self.indent() is not None:
            statements = []

            while (
                (statement := self.import_statement()) is not None
                or (statement := self.assignment_statement()) is not None
                or (statement := self.class_def()) is not None
                or (statement := self.async_func_def()) is not None
                or (statement := self.func_def()) is not None
                or (statement := self.string()) is not None
            ):
                # We store consecutive strings together as a string_list
                if (
                    statements
                    and (ty := type(statement)) == String
                    and ty == ByteString
                    and ty == PrefixedString
                ):
                    prev_statement = statements[-1]

                    if type(prev_statement) == String:
                        statements[-1] = StringList([statements[-1], statement])

                    elif type(prev_statement) == StringList:
                        statements[-1].strings.append(statement)
                    else:
                        statements.append(statement)
                else:
                    statements.append(statement)

            # There should be at least an expression.
            # TODO: Raise error if block has dedent but no expression.
            if self.dedent() is not None and statements:
                return statements

        return None

    @backtrackable
    @memoize
    def class_def(self):
        """
        rule = 'class' identifier generics_annotation? ('(' identifiers ')')? ':' class_suite
        """

        if (
            self.consume_string("class") is not None
            and (name := self.identifier()) is not None
        ):
            generics_annotation = self.generics_annotation()
            parent_classes = None

            self.register_revert()
            if (self.revertable(
                self.consume_string("(") is not None
                and (parent_classes := self.identifiers()) is not None
                and self.consume_string(")") is not None
            )):
                parent_classes = parent_classes

            if (
                self.consume_string(":") is not None
                and (body := self.class_suite()) is not None
            ):
                return Class(name, body, parent_classes, generics_annotation)

        return None


    @backtrackable
    @memoize
    def lhs_argument_trailer(self):
        """
        rule =
            | '[' subscripts ']'
            | '.' identifier
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            self.consume_string("[") is not None
            and (subscripts := self.subscripts()) is not None
            and self.consume_string("]") is not None
        ):
            return subscripts

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string(".") is not None
            and (identifier := self.identifier()) is not None
        ):
            return Field(None, identifier)

        return None

    @backtrackable
    @memoize
    def lhs_argument(self):
        """
        rule = identifier lhs_argument_trailer*
        """

        result = self.identifier()

        if result is None:
            return None

        while (atom_trailer := self.lhs_argument_trailer()) is not None:
            atom_trailer.expr = result
            result = atom_trailer

        return result

    @backtrackable
    @memoize
    def lhs_arguments(self):
        """
        rule = lhs_argument (',' lhs_argument)* ','?
        """

        result = self.lhs_argument()

        if result is None:
            return None

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (lhs_argument := self.lhs_argument()) is not None
        )):
            result.append(lhs_argument)

        self.consume_string(",")

        return result

    @backtrackable
    @memoize
    def lhs(self):
        """
        rule =
            | '(' lhs_arguments ')'
            | '[' lhs_arguments ']'
            | lhs_arguments
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            self.consume_string("(") is not None
            and (lhs_arguments := self.lhs_arguments()) is not None
            and self.consume_string(")") is not None
        ):
            return TupleLHS(lhs_arguments)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("[") is not None
            and (lhs_arguments := self.lhs_arguments()) is not None
            and self.consume_string("]") is not None
        ):
            return ListLHS(lhs_arguments)

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (lhs_arguments := self.lhs_arguments()) is not None:
            return TupleLHS(lhs_arguments) if len(lhs_arguments) > 1 else lhs_arguments[0]

        return None

    @backtrackable
    @memoize
    def for_lhs(self):
        """
        rule =
            | '(' identifiers ')'
            | '[' identifiers ']'
            | identifiers
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            self.consume_string("(") is not None
            and (identifiers := self.identifiers()) is not None
            and self.consume_string(")") is not None
        ):
            return TupleLHS(identifiers)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("[") is not None
            and (identifiers := self.identifiers()) is not None
            and self.consume_string("]") is not None
        ):
            return ListLHS(identifiers)

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (identifiers := self.identifiers()) is not None:
            return TupleLHS(identifiers) if len(identifiers) > 1 else identifiers[0]

        return None

    @backtrackable
    @memoize
    def func_param(self):
        """
        rule = identifier (':' type_annotation)? ('=' indentable_expr)?
        """

        if (name := self.identifier()) is not None:
            type_annotation = None
            default_value_expr = None

            self.register_revert()
            if (self.revertable(
                self.consume_string(":") is not None
                and (type_annotation := self.type_annotation()) is not None
            )):
                type_annotation = type_annotation

            self.register_revert()
            if (self.revertable(
                self.consume_string("=") is not None
                and (default_value_expr := self.indentable_expr()) is not None
            )):
                default_value_expr = default_value_expr

            return FuncParam(name, type_annotation, default_value_expr)

        return None

    @backtrackable
    @memoize
    def func_params(self):
        """
        rule =
            | func_param (',' func_param)* (',' '*' func_param (',' func_param)*)? (',' '**' func_param)? ','?
            | '*' func_param (',' func_param)* (',' '**' func_param)? ','?
            | '**' func_param ','?
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (param := self.func_param()) is not None:
            params = [param]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (param := self.func_param()) is not None
            )):
                params.append(param)

            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("/") is not None
            )):
                params.append(PositionalParamsSeparator())

                self.register_revert()
                while (self.revertable(
                    self.consume_string(",") is not None
                    and (param := self.func_param()) is not None
                )):
                    params.append(param)

            tuple_rest_param = None
            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("*") is not None
                and (param := self.func_param()) is not None
            )):
                tuple_rest_param = param

            keyword_only_params = []
            if tuple_rest_param:
                self.register_revert()
                while (self.revertable(
                    self.consume_string(",") is not None
                    and (param := self.func_param()) is not None
                )):
                    keyword_only_params.append(param)

            named_tuple_rest_param = None
            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("**") is not None
                and (param := self.func_param()) is not None
            )):
                named_tuple_rest_param = param

            return FuncParams(
                params, tuple_rest_param, keyword_only_params, named_tuple_rest_param
            )

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("*") is not None
            and (tuple_rest_param := self.func_param()) is not None
        ):
            named_tuple_params = []
            if tuple_rest_param:
                self.register_revert()
                while (self.revertable(
                    self.consume_string(",") is not None
                    and (param := self.func_param()) is not None
                )):
                    named_tuple_params.append(param)

            named_tuple_rest_param = None
            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and self.consume_string("**") is not None
                and (param := self.func_param()) is not None
            )):
                named_tuple_rest_param = param

            return FuncParams(
                None, tuple_rest_param, named_tuple_params, named_tuple_rest_param
            )

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("**") is not None
            and (named_tuple_rest_param := self.func_param()) is not None
        ):
            return FuncParams(None, None, None, named_tuple_rest_param)

        return None

    @backtrackable
    @memoize
    def func_suite(self):
        """
        rule =
            | simple_statement
            | indent statements dedent
        """

        if (statement := self.simple_statement()) is not None:
            return [statement]

        # There should be at least an expression.
        # TODO: Raise error if block has dedent but no expression.
        if (
            self.indent() is not None
            and (statements := self.statements()) is not None
            and self.dedent() is not None
        ):
            return statements

        return None

    @backtrackable
    @memoize
    def func_def(self):
        """
        rule = 'def' identifier generics_annotation? '(' func_params? ')' ('->' type_annotation)? ':' func_suite
        """

        if (
            self.consume_string("def") is not None
            and (name := self.identifier()) is not None
        ):
            generics_annotation = self.generics_annotation()
            return_type_annotation = None


            if self.consume_string("(") is None:
                return None

            func_params = self.func_params() or []

            if self.consume_string(")") is None:
                return None

            self.register_revert()
            if (self.revertable(
                self.consume_string("->") is not None
                and (return_type_annotation := self.type_annotation()) is not None
            )):
                return_type_annotation = return_type_annotation

            if (
                self.consume_string(":") is not None
                and (body := self.func_suite()) is not None
            ):
                return Function(name, body, func_params, return_type_annotation, generics_annotation)

        return None

    @backtrackable
    @memoize
    def async_statement(self):
        """
        rule = 'async' (func_def | with_statement | for_statement)
        """

        if (
            self.consume_string("async") is not None
            and (
               (statement := self.func_def()) is not None
               or (statement := self.with_statement()) is not None
               or (statement := self.for_statement()) is not None
            )
        ):
            statement.is_async = True
            return statement

        return None

    @backtrackable
    @memoize
    def global_statement(self):
        """
        rule = 'global' identifier (',' identifier)*
        """

        if (
            self.consume_string("global") is not None
            and (name := self.identifier()) is not None
        ):
            names = [name]
            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (name := self.identifier()) is not None
            )):
                names.append(name)

            return Globals(names)

        return None

    @backtrackable
    @memoize
    def nonlocal_statement(self):
        """
        rule = 'nonlocal' identifier (',' identifier)*
        """

        if (
            self.consume_string("nonlocal") is not None
            and (name := self.identifier()) is not None
        ):
            names = [name]
            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (name := self.identifier()) is not None
            )):
                names.append(name)

            return NonLocals(names)

        return None

    @backtrackable
    @memoize
    def assert_statement(self):
        """
        rule = 'assert' expr (',' expr)?
        """

        if (
            self.consume_string("assert") is not None
            and (cond_expr := self.expr()) is not None
        ):
            message_expr = None

            self.register_revert()
            if (self.revertable(
                self.consume_string(",") is not None
                and (message_expr := self.expr()) is not None
            )):
                message_expr = message_expr

            return DelStatement(cond_expr, message_expr)



        return None

    @backtrackable
    @memoize
    def del_statement(self):
        """
        rule = 'del' identifier (',' identifier)*
        """

        if (
            self.consume_string("del") is not None
            and (name := self.identifier()) is not None
        ):
            names = [name]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (name := self.identifier()) is not None
            )):
                names.append(name)

            return DelStatement(names)

        return None

    @backtrackable
    @memoize
    def pass_statement(self):
        """
        rule = 'pass'
        """

        if self.consume_string("pass") is not None:
            return PassStatement()

        return None


    @backtrackable
    @memoize
    def break_statement(self):
        """
        rule = 'break'
        """

        if self.consume_string("break") is not None:
            return BreakStatement()

        return None


    @backtrackable
    @memoize
    def continue_statement(self):
        """
        rule = 'continue'
        """

        if self.consume_string("continue") is not None:
            return ContinueStatement()

        return None


    @backtrackable
    @memoize
    def return_statement(self):
        """
        rule = 'return' exprs?
        """

        if self.consume_string("return") is not None:
            exprs = self.exprs()
            return ReturnStatement(exprs or [])

        return None


    @backtrackable
    @memoize
    def raise_statement(self):
        """
        rule = 'raise' (expr ('from' expr))?
        """

        if self.consume_string("raise") is not None:
            expr = None
            from_expr = None

            if (expr := self.expr()):
                self.register_revert()
                if (self.revertable(
                    self.consume_string("from") is not None
                    and (from_expr := self.expr()) is not None
                )):
                    from_expr = from_expr

            return RaiseStatement(expr, from_expr)

        return None


    @backtrackable
    @memoize
    def flow_statement(self):
        """
        rule =
            | break_statement
            | continue_statement
            | return_statement
            | raise_statement
            | yield_expr
        """

        if (
            (expr := self.break_statement()) is not None
            or (expr := self.continue_statement()) is not None
            or (expr := self.return_statement()) is not None
            or (expr := self.raise_statement()) is not None
            or (expr := self.yield_expr()) is not None
        ):
            return expr

        return None

    @backtrackable
    @memoize
    def assignment_op(self):
        """
        rule =
            | '+='
            | '-='
            | '*='
            | '@='
            | '/='
            | '%='
            | '&='
            | '|='
            | '^='
            | '<<='
            | '>>='
            | '**='
            | '//='
            | '='
        """

        if (
            (op := self.consume_string("+=")) is not None
            or (op := self.consume_string("-=")) is not None
            or (op := self.consume_string("*=")) is not None
            or (op := self.consume_string("@=")) is not None
            or (op := self.consume_string("/=")) is not None
            or (op := self.consume_string("%=")) is not None
            or (op := self.consume_string("&=")) is not None
            or (op := self.consume_string("|=")) is not None
            or (op := self.consume_string("^=")) is not None
            or (op := self.consume_string("<<=")) is not None
            or (op := self.consume_string(">>=")) is not None
            or (op := self.consume_string("**=")) is not None
            or (op := self.consume_string("//=")) is not None
            or (op := self.consume_string("=")) is not None
        ):
            return Operator(op)

        return None

    @backtrackable
    @memoize
    def assignment_annotation(self):
        """
        rule = ':' type_annotation ('=' rest_indentable_expr)?
        """

        if (
            self.consume_string(":") is not None
            and (type_annotation := self.type_annotation()) is not None
        ):
            value_expr = None
            op = None

            self.register_revert()
            if (self.revertable(
                (op := self.consume_string("=")) is not None
                and (value_expr := self.rest_indentable_expr()) is not None
            )):
                value_expr = value_expr

            return AssignmentStatement([], Operator(op), value_expr, type_annotation)

        return None

    @backtrackable
    @memoize
    def assignment_statement(self):
        """
        rule =
            | lhs assignment_annotation
            | lhs assignment_op (yield_expr | rest_indentable_exprs)
            | lhs ('=' lhs)+ '=' (yield_expr | rest_indentable_exprs)
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            (lhs := self.lhs()) is not None
            and (assignment := self.assignment_annotation()) is not None
        ):
            assignment.lhses.append(lhs)
            return assignment

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            (lhs := self.lhs()) is not None
            and (op := self.assignment_op()) is not None
        ):
            if (value_expr := self.yield_expr()) is not None:
                return AssignmentStatement([lhs], op, value_expr)

            if (value_expr := self.rest_indentable_exprs()) is not None:
                return AssignmentStatement([lhs], op, value_expr)


        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (lhs := self.lhs()) is not None:
            lhses = [lhs]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (lhs := self.lhs()) is not None
            )):
                lhses.append(lhs)

            if len(lhses) > 1:
                if (
                    (op := self.assignment_op()) is not None
                    and (value_expr := self.yield_expr()) is not None
                ):
                    return AssignmentStatement(lhses, op, value_expr)

                if (
                    (op := self.assignment_op()) is not None
                    and (value_expr := self.rest_indentable_exprs()) is not None
                ):
                    return AssignmentStatement(lhses, op, value_expr)

            return assignment

        return None


    @backtrackable
    @memoize
    def path(self):
        """
        rule = identifier ('.' identifier)*
        """

        if (name := self.identifier()) is not None:
            names = [name]

            self.register_revert()
            while (self.revertable(
                self.consume_string(".") is not None
                and (name := self.identifier()) is not None
            )):
                names.append(name)

            return names

        return None

    @backtrackable
    @memoize
    def import_sub_path_with_alias(self):
        """
        rule = identifier ('as' identifier)?
        """

        if (name := self.identifier()) is not None:
            alias = None

            self.register_revert()
            while (self.revertable(
                self.consume_string("as") is not None
                and (alias := self.identifier()) is not None
            )):
                alias = alias

            return SubPath([name], alias)

        return None

    @backtrackable
    @memoize
    def import_sub_paths_with_alias(self):
        """
        rule = import_sub_path_with_alias (',' import_sub_path_with_alias)* ','?
        """

        if (sub_path := self.import_sub_path_with_alias()) is not None:
            sub_paths = [sub_path]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (sub_path := self.import_sub_path_with_alias()) is not None
            )):
                sub_paths.append(sub_path)

            self.consume_string(",")

            return sub_paths

        return None

    @backtrackable
    @memoize
    def import_main_path(self):
        """
        rule =
            | '.'* path
            | '.'+
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        relative_level = 0
        while self.consume_string(".") is not None:
            relative_level += 1

        if (path := self.path()) is not None:
            return MainPath(path, None, relative_level)

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        relative_level = 0
        while self.consume_string(".") is not None:
            relative_level += 1

        if relative_level > 0:
            return MainPath(None, None, relative_level)

        return None

    @backtrackable
    @memoize
    def import_sub_paths(self):
        """
        rule =
            | '*'
            | '(' import_sub_paths_with_alias ')'
            | import_sub_paths_with_alias
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if self.consume_string("*") is not None:
            return [SubPath(None, None, True)]

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (
            self.consume_string("(") is not None
            and (paths := self.import_sub_paths_with_alias()) is not None
            and self.consume_string(")") is not None
        ):
            return paths

        # THIRD ALTERNATIVE
        self.revert(cursor, row, column)
        if (paths := self.import_sub_paths_with_alias()) is not None:
            return paths

        return None

    @backtrackable
    @memoize
    def import_main_path_with_alias(self):
        """
        rule = import_main_path ('as' identifier)?
        """

        if (path := self.import_main_path()) is not None:
            alias = None

            self.register_revert()
            if (self.revertable(
                self.consume_string("as") is not None
                and (alias := self.identifier()) is not None
            )):
                path.alias = alias

            return path

        return None

    @backtrackable
    @memoize
    def import_main(self):
        """
        rule = 'import' import_main_path_with_alias
        """

        if (
            self.consume_string("import") is not None
            and (path := self.import_main_path_with_alias()) is not None
        ):
            return ImportStatement(path, None)

        return None

    @backtrackable
    @memoize
    def import_from(self):
        """
        rule = 'from' import_main_path 'import' import_sub_paths
        """
        if (
            self.consume_string("from") is not None
            and (main_path := self.import_main_path()) is not None
            and self.consume_string("import") is not None
            and (sub_paths := self.import_sub_paths()) is not None
        ):
            return ImportStatement(main_path, sub_paths)

        return None

    @backtrackable
    @memoize
    def import_statement(self):
        """
        rule =
            | import_main
            | import_from
        """

        if (
            (statement := self.import_main()) is not None
            or (statement := self.import_from()) is not None
        ):
            return statement

        return None

    @backtrackable
    @memoize
    def decorator_statement(self):
        """
        rule = '@' path ('(' arguments ')')? newline
        """

        if (
            self.consume_string("@") is not None
            and (path := self.path()) is not None
        ):
            arguments = []

            self.register_revert()
            while (self.revertable(
                self.consume_string("(") is not None
                and (arguments := self.arguments()) is not None
                and self.consume_string(")") is not None
            )):
                arguments = arguments

            if self.newline() is not None:
                return Decorator(path, arguments)

        return None

    @backtrackable
    @memoize
    def decorators(self):
        """
        rule = decorator_statement+
        """

        decorator_statements = []
        while (decorator_statement := self.decorator_statement()) is not None:
            decorator_statements.append(decorator_statement)

        if len(decorator_statements) > 0:
            return decorator_statements

        return None

    @backtrackable
    @memoize
    def async_func_def(self):
        """
        rule = 'async' func_def
        """

        if (
            self.consume_string("async") is not None
            and (func_def := self.func_def()) is not None
        ):
            func_def.is_async = True
            return func_def

        return None

    @backtrackable
    @memoize
    def decorated_statement(self):
        """
        rule = decorators (class_def | func_def | async_func_def)
        """

        if (
            (decorators := self.decorators()) is not None
            and (
               (statement := self.func_def()) is not None
               or (statement := self.class_def()) is not None
               or (statement := self.async_func_def()) is not None
            )
        ):
            statement.decorators = decorators
            return statement

        return None

    @backtrackable
    @memoize
    def compound_statement(self):
        """
        rule =
            | if_statement
            | while_statement
            | for_statement
            | try_statement
            | with_statement
            | decorated_statement
            | func_def
            | class_def
            | async_statement
        """

        if (
            (statement := self.if_statement()) is not None
            or (statement := self.while_statement()) is not None
            or (statement := self.for_statement()) is not None
            or (statement := self.try_statement()) is not None
            or (statement := self.with_statement()) is not None
            or (statement := self.decorated_statement()) is not None
            or (statement := self.func_def()) is not None
            or (statement := self.class_def()) is not None
            or (statement := self.async_statement()) is not None
        ):
            return statement

        return None

    @backtrackable
    @memoize
    def small_statement(self):
        """
        rule =
            | assignment_statement
            | indentable_exprs
            | pass_statement
            | flow_statement
            | del_statement
            | import_statement
            | global_statement
            | nonlocal_statement
            | assert_statement
        """

        if (
            (statement := self.assignment_statement()) is not None
            or (statement := self.indentable_exprs()) is not None
            or (statement := self.pass_statement()) is not None
            or (statement := self.flow_statement()) is not None
            or (statement := self.del_statement()) is not None
            or (statement := self.import_statement()) is not None
            or (statement := self.global_statement()) is not None
            or (statement := self.nonlocal_statement()) is not None
            or (statement := self.assert_statement()) is not None
        ):
            return statement

        return None

    @backtrackable
    @memoize
    def simple_statement(self):
        """
        rule = small_statement (';' small_statement)* ';'? newline

        SPECIAL BEHAVIOR:
            Newline token is ignored when a dedent token or no token comes next.
        """

        if (first_statement := self.small_statement()) is not None:
            small_statements = [first_statement]

            self.register_revert()
            while (self.revertable(
                self.consume_string(";") is not None
                and (statement := self.small_statement()) is not None
            )):
                small_statements.append(statement)

            self.consume_string(";")

            next_token = None
            if (next_cursor := self.cursor + 1) < self.tokens_length:
                next_token = self.tokens[next_cursor]

            # If there is no token or next token is a dedent, ignore newline.
            if not next_token or next_token.kind == TokenKind.DEDENT:
                return small_statements if len(small_statements) > 1 else first_statement
            elif next_token.kind == TokenKind.NEWLINE:
                return small_statements if len(small_statements) > 1 else first_statement

        return None

    @backtrackable
    @memoize
    def statement(self):
        """
        rule =
            | compound_statement
            | simple_statement
        """
        if (
            (statement := self.compound_statement()) is not None
            or (statement := self.simple_statement()) is not None
        ):
            return statement

        return None

    @backtrackable
    @memoize
    def statements(self):
        """
        rule = (newline | statement)+
        """

        statements = []
        statement = None

        while (
            self.newline() is not None
            or (statement := self.statement()) is not None
        ):
            if statement:
                statements.append(statement)
                statement = None

        if statements:
            return statements

        return None

    @backtrackable
    @memoize
    def program(self):
        """
        rule = statements?
        """

        if (statements := self.statements()) is not None:
            return statements
        else:
            return statements
