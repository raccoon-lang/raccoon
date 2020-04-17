"""
"""
import subprocess
from os import path
import click
from compiler.lexer.lexer import Lexer
from sys import argv
from compiler.parser.parser import Parser
from compiler.semantic.semantic import SemanticAnalyzer


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
            "--sema",
            "--lowered_ast",
            "--tokens",
        ]

        # We can have multiple output types in args, we take the last one that shows.
        last_supported_output_types_in_args = "exe"

        for arg in argv:
            if arg in supported_output_types:
                last_supported_output_types_in_args = arg[2:]

        return last_supported_output_types_in_args

    @staticmethod
    def compile_code(code, optimization_level=0, display=False, output_type="exe"):
        """
        supported_output_types = [
            "exe",
            "ll",
            "wasm",
            "ast",
            "sema",
            "lowered_ast",
            "tokens",
        ]
        """

        if output_type == "tokens":
            result = Lexer(code).lex()

        elif output_type == "ast":
            result = Parser.from_code(code).program()

        elif output_type == "sema":
            tokens = Lexer(code).lex()
            parser = Parser(tokens)
            ast = parser.program()
            SemanticAnalyzer(parser, ast).analyze()
            result = None

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
