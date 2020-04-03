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
    def compile_string(code, optimization_level=0, display=False, output_type="exe"):
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
            result = Parser.from_code(code).rest_indentable_exprs()
        else:
            click.echo("Unimplemented Output Type!")
            return

        if display or output_type in ["tokens", "ast"]:
            click.echo(result)

    @staticmethod
    def compile_file(
        file_path, optimization_level=0, display=False, output_type="exe",
    ):
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

        # Corona only supports UTF-8 encoded source files.
        with open(file_path, mode="r", encoding="utf-8") as f:
            code = f.read()

            if output_type == "tokens":
                result = Lexer(code).lex()
            elif output_type == "ast":
                result = Parser.from_code(code).rest_indentable_exprs()
            else:
                click.echo("Unimplemented Output Type!")
                return

            if display or output_type in ["tokens", "ast"]:
                click.echo(result)

    @staticmethod
    def run_compiled_file(file_path):
        """
        """

        abs_path = path.abs_path(file_path)
        subprocess.call(abs_path)
