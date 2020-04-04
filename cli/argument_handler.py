"""
"""
import subprocess
from os import path
import click
from compiler.lexer.lexer import Lexer
from sys import argv
from compiler.parser.parser import Parser


class ArgumentHandler:
    """
    """

    @staticmethod
    def get_output_type():
        supported_output_types = [
            "--exe",
            "--ll",
            "--wasm",
            "--ast",
            "--lowered_ast",
            "--tokens",
        ]

        for arg in argv:
            if arg in supported_output_types:
                return arg[2:]

        return "exe"

    @staticmethod
    def compile_code(code, optimization_level=0, display=False, output_type="exe"):
        """
        supported_output_types = [
            "exe",
            "ll",
            "wasm",
            "ast",
            "lowered_ast",
            "tokens",
        ]
        """

        if output_type == "tokens":
            result = Lexer(code).lex()
        elif output_type == "ast":
            # result = Parser.from_code(code).subscript_index()
            # result = Parser.from_code(code).atom_trailer()
            # result = Parser.from_code(code).atom_expr()
            # result = Parser.from_code(code).test()
            # result = Parser.from_code(code).indentable_exprs_or_comprehension()
            # result = Parser.from_code(code).expr()
            # result = Parser.from_code(code).with_statement()
            # result = Parser.from_code(code).except_clause()
            # result = Parser.from_code(code).try_statement()
            # result = Parser.from_code(code).named_expr_or_test()
            # result = Parser.from_code(code).while_statement()
            # result = Parser.from_code(code).if_statement()
            # result = Parser.from_code(code).type_annotation()
            # result = Parser.from_code(code).intersection_type()
            # result = Parser.from_code(code).union_type()
            # result = Parser.from_code(code).class_arguments()
            # result = Parser.from_code(code).class_def()
            # result = Parser.from_code(code).lhs()
            result = Parser.from_code(code).func_def()
            # result = Parser.from_code(code).func_param()
            # result = Parser.from_code(code).lambda_param()
        else:
            click.echo("Unimplemented Output Type!")
            return

        if display or output_type in ["tokens", "ast"]:
            click.echo(result)

    @staticmethod
    def compile_file(
        file_path, optimization_level=0, display=False, output_type="exe",
    ):
        # Raccoon only supports UTF-8 encoded source files.
        with open(file_path, mode="r", encoding="utf-8") as f:
            ArgumentHandler.compile_code(
                f.read(), optimization_level, display, output_type
            )

    @staticmethod
    def run_compiled_file(file_path):
        """
        """

        abs_path = path.abs_path(file_path)
        subprocess.call(abs_path)
