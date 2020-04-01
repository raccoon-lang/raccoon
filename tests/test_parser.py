from unittest.mock import MagicMock, Mock
from compiler.parser.parser import Parser
from compiler.parser.ast import (
    Null,
    Newline,
    Identifier,
    Integer,
    Float,
    ImagInteger,
    ImagFloat,
    String,
    ByteString,
    PrefixedString,
)


def test_parser_memoizes_parser_functions_results_successfully():
    # Memoize if parser successful
    parser0 = Parser.from_code("identifier")
    result0 = parser0.identifier()

    assert result0 == Identifier(0)
    assert parser0.cache == {-1: {"identifier": (Identifier(0), 0)}}

    # Check to see if parser is memoizing subccesses and failures properly
    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.integer)()

    assert parser1.cache == {
        -1: {
            "prefixed_string": (PrefixedString(0), 0),
        },
        0: {
            "imag_float": (ImagFloat(1), 1),
        },
        1: {
            "integer": (None, 2)
        }
    }

    parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.identifier)()

    assert parser1.cache == {
        -1: {
            "prefixed_string": (PrefixedString(0), 0),
        },
        0: {
            "imag_float": (ImagFloat(1), 1),
        },
        1: {
            "integer": (None, 2),
            "identifier": (Identifier(2), 2)
        }
    }

    # Check to see if parser reuses cache instead of making repeated calls
    parser2 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    imag_float = MagicMock(return_value=ImagFloat(1), __name__='imag_float')

    # These functions are needed because the decorators have wrapper functions that take
    # a self argument.
    def memoize_imag_float_wrapper(parser):
        return Parser.memoize(imag_float)(parser)

    def backtrackable_imag_float_wrapper():
        return Parser.backtrackable(memoize_imag_float_wrapper)(parser2)

    parser2.imag_float = backtrackable_imag_float_wrapper

    # parser2.imag_float should onmly be called once here. It's chahed redult should be used
    # for subsequent calls.
    parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.integer)()
    parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.identifier)()
    parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.identifier)()

    assert len(imag_float.mock_calls) == 1


def test_parser_backtracks_on_fail_successfully():
    parser0 = Parser.from_code("1hello")
    result0 = parser0.identifier()

    # TODO: Try more complex parser functions

    assert parser0.cursor == -1
    assert result0 is None


def test_newline_parses_newlines_successfully():
    result0 = Parser.from_code("\n").newline()
    result1 = Parser.from_code("\r\n").newline()
    result2 = Parser.from_code("\r").newline()

    assert result0 == Newline(0)
    assert result1 == Newline(0)
    assert result2 == Newline(0)


def test_identifier_parses_identifiers_successfully():
    result = Parser.from_code("_HEoDagu123").identifier()

    assert result == Identifier(0)


def test_integer_parses_integer_literals_successfully():
    result0 = Parser.from_code("5_000").integer()
    result1 = Parser.from_code("0001").integer()
    result2 = Parser.from_code("0b11_00").integer()
    result3 = Parser.from_code("0o217").integer()
    result4 = Parser.from_code("0xffEE_210").integer()

    assert result0 == Integer(0)
    assert result1 == Integer(0)
    assert result2 == Integer(0)
    assert result3 == Integer(0)
    assert result4 == Integer(0)


def test_float_parses_float_literals_successfully():
    result0 = Parser.from_code(".05").float()
    result1 = Parser.from_code("0.0_55").float()
    result2 = Parser.from_code("1_00.00_50").float()
    result3 = Parser.from_code("1.e-5_00").float()
    result4 = Parser.from_code("1.").float()
    result5 = Parser.from_code("1_00.1_00e-1_00").float()

    assert result0 == Float(0)
    assert result1 == Float(0)
    assert result2 == Float(0)
    assert result3 == Float(0)
    assert result4 == Float(0)
    assert result5 == Float(0)


def test_imag_integer_parses_imaginary_integer_literals_successfully():
    result0 = Parser.from_code("5_000im").imag_integer()
    result1 = Parser.from_code("0001im").imag_integer()

    assert result0 == ImagInteger(0)
    assert result1 == ImagInteger(0)


def test_imag_float_parses_imaginary_float_literals_successfully():
    result0 = Parser.from_code(".05im").imag_float()
    result1 = Parser.from_code("0.0_55im").imag_float()
    result2 = Parser.from_code("1_00.00_50im").imag_float()
    result3 = Parser.from_code("1.e-5_00im").imag_float()
    result4 = Parser.from_code("1_00.1_00e-1_00im").imag_float()

    assert result0 == ImagFloat(0)
    assert result1 == ImagFloat(0)
    assert result2 == ImagFloat(0)
    assert result3 == ImagFloat(0)
    assert result4 == ImagFloat(0)


def test_string_parses_string_literals_successfully():
    result0 = Parser.from_code("'hello\t there'").string()
    result1 = Parser.from_code('" This is a new world"').string()
    result2 = Parser.from_code("'''\n This is a new world\n'''").string()
    result3 = Parser.from_code('"""\n This is a new world\n"""').string()

    assert result0 == String(0)
    assert result1 == String(0)
    assert result2 == String(0)
    assert result3 == String(0)


def test_byte_string_parses_byte_string_literals_successfully():
    result0 = Parser.from_code("b'hello\t there'").byte_string()
    result1 = Parser.from_code('rb" This is a new world"').byte_string()
    result2 = Parser.from_code("b'''\n This is a new world\n'''").byte_string()
    result3 = Parser.from_code('rb"""\n This is a new world\n"""').byte_string()

    assert result0 == ByteString(0)
    assert result1 == ByteString(0)
    assert result2 == ByteString(0)
    assert result3 == ByteString(0)


def test_prefixed_string_parses_prefixed_string_literals_successfully():
    result0 = Parser.from_code("u'hello\t there'").prefixed_string()
    result1 = Parser.from_code('rf" This is a new world"').prefixed_string()
    result2 = Parser.from_code("r'''\n This is a new world\n'''").prefixed_string()
    result3 = Parser.from_code('rf"""\n This is a new world\n"""').prefixed_string()

    assert result0 == PrefixedString(0)
    assert result1 == PrefixedString(0)
    assert result2 == PrefixedString(0)
    assert result3 == PrefixedString(0)


def test_p_combinator_function_parses_matched_sequence_successfully():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0 +")
    result0 = parser0.p(parser0.integer, parser0.float, "+")()

    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    result1 = parser1.p(
        parser1.prefixed_string, parser1.imag_float, parser1.identifier
    )()

    def parser2_func(parser_data, combinator_data):
        combinator_data["imag_float"] = parser_data[1]

    parser2 = Parser.from_code("u'hello' .05im 5_000im")
    result2 = parser2.p(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 == [Integer(0), Float(1), 2]
    assert result1 == [PrefixedString(0), ImagFloat(1), Identifier(2)]
    assert result2 == [PrefixedString(0), ImagFloat(1), ImagInteger(2)]
    assert parser2.combinator_data == {"imag_float": ImagFloat(1)}


def test_p_combinator_function_fails_with_unmatched_sequence():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0")
    result0 = parser0.p(parser0.integer, parser0.integer)()

    parser1 = Parser.from_code("u'hello'")
    result1 = parser1.p(parser1.prefixed_string, parser1.imag_float)()

    def parser2_func(parser_data, combinator_data):
        combinator_data["imag_float"] = parser_data[1]

    parser2 = Parser.from_code("u'hello' .05im")
    result2 = parser2.p(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 is None
    assert result1 is None
    assert result2 is None
    assert parser2.combinator_data == {}


def test_alt_combinator_function_parses_matched_alternative_successfully():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0")
    result0 = parser0.alt(
        parser0.p(parser0.integer, parser0.float, "+"), parser0.integer,
    )()

    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    result1 = parser1.alt(
        parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.integer),
        parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.identifier),
    )()

    def parser2_func(parser_data, combinator_data, choice):
        if choice == 0:
            taken = (parser_data[1], 0)
        elif choice == 1:
            taken = (parser_data[1], 1)
        elif choice == 2:
            taken = (parser_data[1], 2)

        combinator_data["alt"] = taken

    parser2 = Parser.from_code("u'hello' .05im 5_000im")
    result2 = parser2.alt(
        parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.integer),
        parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.imag_integer),
        parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.imag_float),
        fn=parser2_func,
    )()

    assert result0 == Integer(0)
    assert result1 == [PrefixedString(0), ImagFloat(1), Identifier(2)]
    assert result2 == [PrefixedString(0), ImagFloat(1), ImagInteger(2)]
    assert parser2.combinator_data == {"alt": (ImagFloat(1), 1)}


def test_alt_combinator_function_takes_first_matched_alternative_successfully():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0 +")
    result0 = parser0.alt(
        parser0.p(parser0.integer, parser0.float),
        parser0.p(parser0.integer, parser0.float, "+"),
    )()

    parser1 = Parser.from_code("5 6.0 +")
    result1 = parser1.alt(
        parser1.p(parser1.integer, parser1.float, "+"),
        parser1.p(parser1.integer, parser1.float),
    )()

    parser2 = Parser.from_code("5 6.0 +")
    result2 = parser2.alt(
        parser2.p(parser2.integer, parser2.float, "/"),
        parser2.p(parser2.integer, parser2.float),
    )()

    assert result0 == [Integer(0), Float(1)]
    assert result1 == [Integer(0), Float(1), 2]
    assert result2 == [Integer(0), Float(1)]


def test_alt_combinator_function_fails_with_unmatched_alternatives():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0")
    result0 = parser0.alt(
        parser0.p(parser0.integer, parser0.float, "+"), parser0.float,
    )()

    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    result1 = parser1.alt(
        parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.integer),
        parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.float),
    )()

    def parser2_func(parser_data, combinator_data, choice):
        if choice == 0:
            taken = (parser_data[1], 0)
        elif choice == 1:
            taken = (parser_data[1], 1)
        elif choice == 2:
            taken = (parser_data[1], 2)

        combinator_data["alt"] = taken

    parser2 = Parser.from_code("u'hello' .05im 5_000im")
    result2 = parser2.alt(
        parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.integer),
        parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.identifier),
        parser2.p(parser2.prefixed_string, parser2.imag_float, parser2.imag_float),
        fn=parser2_func,
    )()

    assert result0 is None
    assert result1 is None
    assert result2 is None
    assert parser2.combinator_data == {}


def test_more_combinator_function_parses_matched_one_or_more_sequence_successfully():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0 + 2_000 .100 +")
    result0 = parser0.more(parser0.integer, parser0.float, "+")()

    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS r'start' 0.10im")
    result1 = parser1.more(
        parser1.prefixed_string, parser1.imag_float, parser1.identifier
    )()

    def parser2_func(parser_data, combinator_data):
        combinator_data["first"] = parser_data[0]

    parser2 = Parser.from_code("u'hello' .05im 5_000im")
    result2 = parser2.more(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 == [[Integer(0), Float(1), 2], [Integer(3), Float(4), 5]]
    assert result1 == [[PrefixedString(0), ImagFloat(1), Identifier(2)]]
    assert result2 == [[PrefixedString(0), ImagFloat(1), ImagInteger(2)]]
    assert parser2.combinator_data == {
        "first": [PrefixedString(0), ImagFloat(1), ImagInteger(2)]
    }


def test_more_combinator_function_fails_with_unmatched_sequence():
    # TODO: More complex examples
    parser0 = Parser.from_code("5 6.0")
    result0 = parser0.more(parser0.integer, parser0.integer)()

    parser1 = Parser.from_code("u'hello'")
    result1 = parser1.more(parser1.prefixed_string, parser1.imag_float)()

    def parser2_func(parser_data, combinator_data):
        combinator_data["first"] = parser_data[0]

    parser2 = Parser.from_code("u'hello' .05im")
    result2 = parser2.more(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 is None
    assert result1 is None
    assert result2 is None
    assert parser2.combinator_data == {}


def test_opt_more_combinator_function_parses_matched_zero_or_more_sequences_successfully():
    # TODO: More complex examples

    # Match found
    parser0 = Parser.from_code("5 6.0 + 2_000 .100 +")
    result0 = parser0.opt_more(parser0.integer, parser0.float, "+")()

    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS r'start' 0.10im")
    result1 = parser1.opt_more(
        parser1.prefixed_string, parser1.imag_float, parser1.identifier
    )()

    def parser2_func(parser_data, combinator_data):
        combinator_data["first"] = parser_data[0]

    parser2 = Parser.from_code("u'hello' .05im 5_000im")
    result2 = parser2.opt_more(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 == [[Integer(0), Float(1), 2], [Integer(3), Float(4), 5]]
    assert result1 == [[PrefixedString(0), ImagFloat(1), Identifier(2)]]
    assert result2 == [[PrefixedString(0), ImagFloat(1), ImagInteger(2)]]
    assert parser2.combinator_data == {
        "first": [PrefixedString(0), ImagFloat(1), ImagInteger(2)]
    }

    # No match
    parser0 = Parser.from_code("5 6.0")
    result0 = parser0.opt_more(parser0.integer, parser0.integer)()

    parser1 = Parser.from_code("u'hello'")
    result1 = parser1.opt_more(parser1.prefixed_string, parser1.imag_float)()

    def parser2_func(parser_data, combinator_data):
        combinator_data["first"] = parser_data[0]

    parser2 = Parser.from_code("u'hello' .05im")
    result2 = parser2.opt_more(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 == Null()
    assert result1 == Null()
    assert result2 == Null()
    assert parser2.combinator_data == {}


def test_opt_combinator_function_parses_matched_zero_or_one_sequence_successfully():
    # TODO: More complex examples

    # Match found
    parser0 = Parser.from_code("5 6.0 +")
    result0 = parser0.opt(parser0.integer, parser0.float, "+")()

    parser1 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    result1 = parser1.opt(
        parser1.prefixed_string, parser1.imag_float, parser1.identifier
    )()

    def parser2_func(parser_data, combinator_data):
        combinator_data["imag_integer"] = parser_data[2]

    parser2 = Parser.from_code("u'hello' .05im 5_000im")
    result2 = parser2.opt(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 == [Integer(0), Float(1), 2]
    assert result1 == [PrefixedString(0), ImagFloat(1), Identifier(2)]
    assert result2 == [PrefixedString(0), ImagFloat(1), ImagInteger(2)]
    assert parser2.combinator_data == {"imag_integer": ImagInteger(2)}

    # No match
    parser0 = Parser.from_code("5 6.0")
    result0 = parser0.opt(parser0.integer, parser0.integer)()

    parser1 = Parser.from_code("u'hello'")
    result1 = parser1.opt(parser1.prefixed_string, parser1.imag_float)()

    def parser2_func(parser_data, combinator_data):
        combinator_data["first"] = parser_data[0]

    parser2 = Parser.from_code("u'hello' .05im")
    result2 = parser2.opt(
        parser2.prefixed_string,
        parser2.imag_float,
        parser2.imag_integer,
        fn=parser2_func,
    )()

    assert result0 == Null()
    assert result1 == Null()
    assert result2 == Null()
    assert parser2.combinator_data == {}


"""
Work in progress tests below
"""

# print('',
#       result0,
#       result1,
#       result2,
#       parser2.combinator_data,
#       sep="\n\n>>>> ")

# def test_parse_power_expr_parses_power_expression_successfully():
#     # TODO: More complex examples
#     result0 = Parser.from_code("5^6").parse_power_expr()
#     result1 = Parser.from_code("5²").parse_power_expr()
#     result2 = Parser.from_code("5").parse_power_expr()
#     result3 = Parser.from_code("√5²").parse_power_expr()
#     # result4 = Parser.from_code("√5^5").parse_power_expr()

#     print('', result0, result1, result2, result3, sep='\n\n>>> ')

# def test_parse_unary_expr_root_expression_successfully():
#     # TODO: More complex examples
#     result0 = Parser.from_code("-6").parse_unary_expr()
#     result1 = Parser.from_code("-5²").parse_unary_expr()
#     result2 = Parser.from_code("√~5²").parse_unary_expr()
#     result3 = Parser.from_code("-√5^5").parse_unary_expr()
#     result4 = Parser.from_code("-~+5_00").parse_unary_expr()

#     print('', result0, result1, result2, result3, result4, sep='\n\n>>> ')

# def test_parse_mul_expr_multiply_expression_successfully():
#     # TODO: More complex examples
#     result0 = Parser.from_code("-5.0f").parse_mul_expr()
#     result1 = Parser.from_code("0xff*3//4").parse_mul_expr()
#     result2 = Parser.from_code("√~5f²").parse_mul_expr()
#     result3 = Parser.from_code("5^5*3").parse_mul_expr()
#     result4 = Parser.from_code("-5/-4*+3").parse_mul_expr()

#     print('', result0, result1, result2, result3, result4, sep='\n\n>>> ')
