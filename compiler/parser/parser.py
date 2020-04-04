"""
A packrat parser for parsing Corona's syntax.

Check `compiler/parser/parser.grammar` for the language's parser grammar specification.
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
    FuncExpr,
    TupleRestExpr,
    NamedTupleRestExpr,
    Comprehension,
    ComprehensionType,
    Yield,
    Dict,
    Set,
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
    With,
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

    def p(self, *parsers, fn=None):
        """
        A combinator function for parsing PEG sequence.
        Supports function and out argument for pulling out relevant data.

        NOTE:
            Currently not used. Surprisingly implementing parsers logic give more concise code.
            And combinators have terrible performance anyway, so I may remove this impl later.
        """

        def func():
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            func.__name__ = "p"
            result = []

            for parser in parsers:
                is_a_str = type(parser) == str
                ast = self.consume_string(parser) if is_a_str else parser()

                if ast is None:
                    # Revert parser state
                    self.revert(cursor, row, column)
                    break

                result.append(ast)
            else:
                if fn:
                    fn(result, self.combinator_data)

                return result

            return None

        return func

    def alt(self, *parsers, fn=None):
        """
        A combinator function for parsing PEG alternatives.
        Supports function and out argument f0r pulling out relevant data.

        NOTE:
            Currently not used. Surprisingly implementing parsers logic give more concise code.
            And combinators have terrible performance anyway, so I may remove this impl later.
        """

        def func():
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            func.__name__ = "alt"
            result = None
            choice = -1

            for idx, parser in enumerate(parsers):
                # Parser functions and consume_string revert parser state if they fail
                # so need for reverting after each alternative try.
                is_a_str = type(parser) == str
                ast = self.consume_string(parser) if is_a_str else parser()

                if ast is not None:
                    choice = idx
                    result = ast
                    break

            if result is None:
                # Revert parser state
                self.revert(cursor, row, column)
            elif fn:
                fn(result, self.combinator_data, choice)

            return result

        return func

    def more(self, *parsers, fn=None):
        """
        A combinator function for parsing one or more occurences of a PEG sequence.
        Supports function and out argument for pulling out relevant data.

        NOTE:
            Currently not used. Surprisingly implementing parsers logic give more concise code.
            And combinators have terrible performance anyway, so I may remove this impl later.
        """

        def func():
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            func.__name__ = "more"
            result = []

            while True:
                ast = self.p(*parsers)()
                if ast is None:
                    break

                result.append(ast)

            if len(result) < 1:
                # Revert parser state
                self.revert(cursor, row, column)
                return None

            elif fn:
                fn(result, self.combinator_data)

            return result

        return func

    def opt_more(self, *parsers, fn=None):
        """
        A combinator function for parsing zero or more occurences of a PEG sequence.
        Supports function and out argument for pulling out relevant data.

        NOTE:
            Currently not used. Surprisingly implementing parsers logic give more concise code.
            And combinators have terrible performance anyway, so I may remove this impl later.
        """

        def func():
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            func.__name__ = "opt_more"
            result = []

            while True:
                ast = self.p(*parsers)()
                if ast is None:
                    break

                result.append(ast)

            if len(result) < 1:
                # Revert parser state
                self.revert(cursor, row, column)
                return Null()

            elif fn:
                fn(result, self.combinator_data)

            return result

        return func

    def opt(self, *parsers, fn=None):
        """
        A combinator function for parsing zero or one occurence of a PEG sequence.
        Supports function and out argument for pulling out relevant data.

        NOTE:
            Currently not used. Surprisingly implementing parsers logic give more concise code.
            And combinators have terrible performance anyway, so I may remove this impl later.
        """

        def func():
            # Get important parser state before parsing.
            cursor, row, column = self.cursor, *self.get_line_info()

            func.__name__ = "opt_more"

            result = self.p(*parsers)()
            if result is None:
                # Revert parser state
                self.revert(cursor, row, column)
                return Null()

            elif fn:
                fn(result, self.combinator_data)

            return result

        return func

    def register_revert(self):
        """
        Store state to which to revert parser to later.
        """

        self.revert_data = (self.cursor, *self.get_line_info())

    def revertable(self, cond):
        """
        Reverts parser state to previously registered revert state
        """
        if not cond:
            self.revert(*self.revert_data)
        else:
            # This is needed for while loops, otherwise the revert state will
            # be stuck at the state before the first iteration. So we want
            # to update the state on each iteration.
            self.register_revert()

        return cond


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
        result = self.integer()  # TODO

        if result is None:
            return None

        power = self.consume_string("^")
        integer2 = self.integer()  # TODO

        if power is not None or integer2 is not None:
            result = BinaryExpr(result, Operator(power), integer2)
        else:
            square = self.consume_string("²")
            if square is not None:
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
            and (or_test := self.or_test()) is not None
            and self.consume_string("else") is not None
            and (or_test2 := self.or_test()) is not None
        ):
            result = IfExpr(result, or_test, or_test2)

        return result

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

        if (
            self.consume_string("=") is not None
            and (test := self.test()) is not None
        ):
            result.default_value_expr = test

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

        # TODO: Fix impl for `'(' func_params? ')'` to use self.func_params()

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            self.consume_string("(") is not None
            and (func_params := self.lambda_params()) is not None
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
                return FuncExpr(None, [expr], params)

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

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (expr := self.expr()) is not None
        )):
            result.append(expr)

        self.consume_string(",")

        return result

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

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (rest_expr := self.rest_expr()) is not None
        )):
            result.append(rest_expr)

        self.consume_string(",")

        return result

    @backtrackable
    @memoize
    def lambda_block_def(self):
        """
        rule = 'lambda' lambda_params? ':' indent statement+ dedent
        """

        # TODO: Change expr to statement

        if self.consume_string("lambda") is not None:
            params = params if (params := self.lambda_params()) else []

            if (
                self.consume_string(":") is not None
                and self.indent() is not None
            ):
                exprs = []
                while (expr := self.expr()) is not None:
                    exprs.append(expr)

                # There should be at least an expression.
                # TODO: Raise error if block has dedent but no expression.
                if self.dedent() is not None and len(expr) > 0:
                    return FuncExpr(None, exprs, params)

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

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (indentable_expr := self.indentable_expr()) is not None
        )):
            result.append(indentable_expr)

        self.consume_string(",")

        return result

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

        result = [result]

        self.register_revert()
        while (self.revertable(
            self.consume_string(",") is not None
            and (rest_expr := self.rest_indentable_expr()) is not None
        )):
            result.append(rest_expr)

        self.consume_string(",")

        return result

    @backtrackable
    @memoize
    def comprehension_where(self):
        """
        rule = 'where' indentable_exprs
        """

        result = None

        if (
            self.consume_string("where") is not None
            and (indentable_expr := self.indentable_expr()) is not None
        ):
            result = indentable_expr

        return result

    @backtrackable
    @memoize
    def sync_comprehension_for(self):
        """
        rule = 'for' lhs 'in' indentable_expr comprehension_iter?
        """

        result = None

        # TODO: Change identifier to lhs

        if (
            self.consume_string("for") is not None
            and (identifier := self.identifier()) is not None
            and self.consume_string("in") is not None
            and (indentable_expr := self.indentable_expr()) is not None
        ):
            result = Comprehension(None, identifier, indentable_expr)

            if (comprehension_where := self.comprehension_where()):
                result.where_exprs = comprehension_where

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
    def indentable_exprs_or_comprehension(self):
        """
        rule =
            | rest_indentable_expr comprehension_for
            | rest_indentable_expr (',' rest_indentable_expr)* ','?
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if (
            (rest_indentable_expr := self.rest_indentable_expr()) is not None
            and (comprehension_for := self.comprehension_for()) is not None
        ):
            comprehension_for.expr = rest_indentable_expr
            return comprehension_for

        # SECOND ALTERNATIVE
        self.revert(cursor, row, column)
        if (rest_indentable_expr := self.rest_indentable_expr()) is not None:
            rest_indentable_exprs = [rest_indentable_expr]

            self.register_revert()
            while (self.revertable(
                self.consume_string(",") is not None
                and (rest_expr := self.rest_indentable_expr()) is not None
            )):
                rest_indentable_exprs.append(rest_expr)

            self.consume_string(",")

            return rest_indentable_exprs

        return None

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
    def dict_or_set(self):
        """
        rule =
            | test ':' expr_suite comprehension_for
            | test ':' expr_suite (',' test ':' expr_suite)* ','?
            | rest_indentable_expr comprehension_for
            | rest_indentable_exprs
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
        if (
            (rest_indentable_expr := self.rest_indentable_expr()) is not None
            and (comprehension_for := self.comprehension_for()) is not None
        ):
            comprehension_for.expr = rest_indentable_expr
            comprehension_for.comprehension_type = ComprehensionType.SET
            return comprehension_for

        # FOURTH ALTERNATIVE
        self.revert(cursor, row, column)
        if (rest_indentable_exprs := self.rest_indentable_exprs()) is not None:
            return Set(rest_indentable_exprs)

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
        rule = subscript (',' subscript)* ','?
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
    def atom(self):
        """
        rule =
            | '(' indentable_exprs_or_comprehension? ')'
            | '(' yield_expr ')'
            | '{' dict_or_set? '}'
            | identifier
            | float
            | string+
            | 'None'
            | 'True'
            | 'False'
        """

        cursor, row, column = self.cursor, *self.get_line_info()

        # FIRST ALTERNATIVE
        if self.consume_string("(") is not None:
            exprs = self.indentable_exprs_or_comprehension()
            if self.consume_string(")") is not None:
                result = exprs

                # Check if this can be a tuple expression like () and (expr,)
                if exprs is None:
                    result = Tuple(exprs)
                elif self.tokens[self.cursor - 1].data == ",":
                    result = Tuple()

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
        if self.consume_string("(") is not None:
            dict_or_set = self.dict_or_set()
            if self.consume_string(")") is not None:

                # Check if this can be a set expression like {}
                return dict_or_set if dict_or_set is not None else Set()


        # FOURTH ALTERNATIVE
        if (float_ := self.float()) is not None:
            return float_

        # FIFTH ALTERNATIVE
        if (integer := self.integer()) is not None:
            return integer

        # SIXTH ALTERNATIVE
        if (string := self.string()) is not None:

            string_list = [string]
            while(string := self.string() is not None):
                string_list.append(string)

            return string_list if string_list else string

        # SEVENTH ALTERNATIVE
        self.revert(cursor, row, column)
        if self.consume_string("None") is not None:
            return NoneLiteral()

        # EIGHTH ALTERNATIVE
        if self.consume_string("True") is not None:
            return Bool(True)

        # NINETH ALTERNATIVE
        if self.consume_string("False") is not None:
            return Bool(False)

        # TENTH ALTERNATIVE
        self.revert(cursor, row, column)
        if (identifier := self.identifier()) is not None:
            return identifier

        return None

    @backtrackable
    @memoize
    def identifiers(self):
        """
        rule = identifier (',' identifier)* ','?
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

        # TODO: Change expr_suite for func_suite

        self.register_revert()
        if (self.revertable(
            self.consume_string("with") is not None
            and (with_item := self.with_item()) is not None
        )):
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
                and (expr_suite := self.expr_suite()) is not None
            ):
                return With(arguments, expr_suite)

        return None
