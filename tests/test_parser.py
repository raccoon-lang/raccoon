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
    Operator,
    UnaryExpr,
    BinaryExpr,
    IfExpr,
    FuncParam,
    FuncParams,
    FuncExpr,
    TupleRestExpr,
    NamedTupleRestExpr,
    ComprehensionFor,
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
        -1: {"prefixed_string": (PrefixedString(0), 0),},
        0: {"imag_float": (ImagFloat(1), 1),},
        1: {"integer": (None, 2)},
    }

    parser1.p(parser1.prefixed_string, parser1.imag_float, parser1.identifier)()

    assert parser1.cache == {
        -1: {"prefixed_string": (PrefixedString(0), 0),},
        0: {"imag_float": (ImagFloat(1), 1),},
        1: {"integer": (None, 2), "identifier": (Identifier(2), 2)},
    }

    # Check to see if parser reuses cache instead of making repeated calls
    parser2 = Parser.from_code("u'hello' .05im _wr2t4gdbeYFS")
    imag_float = MagicMock(return_value=ImagFloat(1), __name__="imag_float")

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


def test_power_expr_function_parses_power_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5^6").power_expr()
    result1 = Parser.from_code("5²").power_expr()
    result2 = Parser.from_code("5").power_expr()
    result3 = Parser.from_code("√5²").power_expr()
    result4 = Parser.from_code("√5^5").power_expr()

    assert result0 == BinaryExpr(Integer(0), Operator(1), Integer(2))
    assert result1 == UnaryExpr(Integer(0), Operator(1))
    assert result2 == Integer(0)
    assert result3 == UnaryExpr(UnaryExpr(Integer(1), Operator(2)), Operator(0))
    assert result4 == UnaryExpr(
        BinaryExpr(Integer(1), Operator(2), Integer(3)), Operator(0)
    )


def test_unary_expr_function_parses_root_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("-6").unary_expr()
    result1 = Parser.from_code("-5²").unary_expr()
    result2 = Parser.from_code("~√5²").unary_expr()
    result3 = Parser.from_code("-√5^5").unary_expr()
    result4 = Parser.from_code("-~+5_00").unary_expr()

    assert result0 == UnaryExpr(Integer(1), Operator(0))
    assert result1 == UnaryExpr(UnaryExpr(Integer(1), Operator(2)), Operator(0))
    assert result2 == UnaryExpr(
        UnaryExpr(UnaryExpr(Integer(2), Operator(3)), Operator(1)), Operator(0)
    )
    assert result3 == UnaryExpr(
        UnaryExpr(BinaryExpr(Integer(2), Operator(3), Integer(4)), Operator(1)),
        Operator(0),
    )
    assert result4 == UnaryExpr(
        UnaryExpr(UnaryExpr(Integer(3), Operator(2)), Operator(1)), Operator(0)
    )


def test_mul_expr_function_parses_multiply_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("-5").mul_expr()
    result1 = Parser.from_code("0xff*3//4").mul_expr()
    result2 = Parser.from_code("5%5^3").mul_expr()
    result3 = Parser.from_code("5²/-4@+3").mul_expr()

    assert result0 == UnaryExpr(Integer(1), Operator(0))
    assert result1 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        UnaryExpr(Integer(7), Operator(6)),
    )


def test_sum_expr_function_parses_sum_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").sum_expr()
    result1 = Parser.from_code("0xff+3-4").sum_expr()
    result2 = Parser.from_code("5-5*3").sum_expr()
    result3 = Parser.from_code("5²/-4--5*+3").sum_expr()

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    assert result1 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        BinaryExpr(
            UnaryExpr(Integer(7), Operator(6)),
            Operator(8),
            UnaryExpr(Integer(10), Operator(9))
        )
    )


def test_shift_expr_function_parses_shift_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").shift_expr()
    result1 = Parser.from_code("0xff>>3<<4").shift_expr()
    result2 = Parser.from_code("5>>5*3").shift_expr()
    result3 = Parser.from_code("5²+-4<<-5*+3").shift_expr()

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    assert result1 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        BinaryExpr(
            UnaryExpr(Integer(7), Operator(6)),
            Operator(8),
            UnaryExpr(Integer(10), Operator(9))
        )
    )


def test_and_expr_function_parses_and_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").and_expr()
    result1 = Parser.from_code("0xff&3&4").and_expr()
    result2 = Parser.from_code("5&5>>3").and_expr()
    result3 = Parser.from_code("5²<<-4&-5-+3").and_expr()

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    assert result1 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        BinaryExpr(
            UnaryExpr(Integer(7), Operator(6)),
            Operator(8),
            UnaryExpr(Integer(10), Operator(9))
        )
    )


def test_xor_expr_function_parses_xor_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").xor_expr()
    result1 = Parser.from_code("0xff||3||4").xor_expr()
    result2 = Parser.from_code("5||5&3").xor_expr()
    result3 = Parser.from_code("5²&-4||-5<<+3").xor_expr()

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    assert result1 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        BinaryExpr(
            UnaryExpr(Integer(7), Operator(6)),
            Operator(8),
            UnaryExpr(Integer(10), Operator(9))
        )
    )


def test_or_expr_function_parses_or_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").or_expr()
    result1 = Parser.from_code("0xff|3|4").or_expr()
    result2 = Parser.from_code("5|5||3").or_expr()
    result3 = Parser.from_code("5²||-4|-5<<+3").or_expr()

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    assert result1 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        BinaryExpr(
            UnaryExpr(Integer(7), Operator(6)),
            Operator(8),
            UnaryExpr(Integer(10), Operator(9))
        )
    )


def test_comparison_expr_function_parses_comparison_expression_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").comparison_expr()
    result1 = Parser.from_code("0xff<3>4==5<=0b101>=0o767").comparison_expr()
    result2 = Parser.from_code("5 is 5|3").comparison_expr()
    result3 = Parser.from_code("5²*-4!=-5<<+3").comparison_expr()
    result4 = Parser.from_code("5|5 not in 3").comparison_expr()
    result5 = Parser.from_code("5-5 is not 3").comparison_expr()

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    assert result1 == BinaryExpr(
        BinaryExpr(
            BinaryExpr(
                BinaryExpr(
                    BinaryExpr(Integer(0), Operator(1), Integer(2)),
                    Operator(3),
                    Integer(4)
                ),
                Operator(5),
                Integer(6)
            ),
            Operator(7),
            Integer(8)
        ),
        Operator(9),
        Integer(10),
    )
    assert result2 == BinaryExpr(
        Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    )
    assert result3 == BinaryExpr(
        BinaryExpr(
            UnaryExpr(Integer(0), Operator(1)),
            Operator(2),
            UnaryExpr(Integer(4), Operator(3)),
        ),
        Operator(5),
        BinaryExpr(
            UnaryExpr(Integer(7), Operator(6)),
            Operator(8),
            UnaryExpr(Integer(10), Operator(9))
        )
    )
    assert result4 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3, 4), Integer(5),
    )
    assert result5 == BinaryExpr(
        BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3, 4), Integer(5),
    )


def test_not_test_function_parses_not_test_successfully():
    # TODO: More complex examples
    result0 = Parser.from_code("5²").not_test()
    result1 = Parser.from_code("0xff&3&4").not_test()
    result2 = Parser.from_code("5&5>>3").not_test()
    result3 = Parser.from_code("5²<<-4&-5-+3").not_test()

    print('', result0, result1, result2, result3, sep="\n\n>>>> ")

    assert result0 == UnaryExpr(Integer(0), Operator(1))
    # assert result1 == BinaryExpr(
    #     BinaryExpr(Integer(0), Operator(1), Integer(2)), Operator(3), Integer(4)
    # )
    # assert result2 == BinaryExpr(
    #     Integer(0), Operator(1), BinaryExpr(Integer(2), Operator(3), Integer(4))
    # )
    # assert result3 == BinaryExpr(
    #     BinaryExpr(
    #         UnaryExpr(Integer(0), Operator(1)),
    #         Operator(2),
    #         UnaryExpr(Integer(4), Operator(3)),
    #     ),
    #     Operator(5),
    #     BinaryExpr(
    #         UnaryExpr(Integer(7), Operator(6)),
    #         Operator(8),
    #         UnaryExpr(Integer(10), Operator(9))
    #     )
    # )
