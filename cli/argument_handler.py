"""
"""
import subprocess
from os import path
import click
import json
import re
from sys import argv
from compiler import CompilerOptions
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from utils import json_dumps


class ArgumentHandler:
    """
    Contains the handling logic of the different arguments passed to the
    program.
    """

    @staticmethod
    def get_compiler_options():
        compiler_opts = CompilerOptions()
        if "-vv" in argv or "--verbose" in argv:
            compiler_opts.verbose = True

        return compiler_opts

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
    def compile_code(code, output_type="exe", compiler_opts=CompilerOptions()):
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
            tokens = Lexer(code, compiler_opts).lex()
            result = json_dumps(tokens)

        elif output_type == "ast":
            ast = Parser.from_code(code, compiler_opts).parse()
            result = json_dumps(ast)

        elif output_type == "sema":
            tokens = Lexer(code, compiler_opts).lex()
            ast = Parser(tokens, compiler_opts).parse()
            semantic_info = SemanticAnalyzer(ast, tokens, compiler_opts).analyze()
            result = json_dumps(semantic_info)

        elif output_type == "ll":
            tokens = Lexer(code, compiler_opts).lex()
            ast = Parser(tokens, compiler_opts).parse()
            semantic_info = SemanticAnalyzer(ast, tokens, compiler_opts).analyze()
            # llvm_module = LLVMCodegenVisitor(lowered_ast, compiler_opts).start_visit()
            # result = llvm_module
            result = None

        elif output_type == "wasm":
            result = None

        else:
            click.echo("Unimplemented Output Type!")
            return

        click.echo(result)

    @staticmethod
    def compile_file(file_path, output_type="exe", compiler_opts=CompilerOptions()):
        # Raccoon only supports UTF-8 encoded source files.
        with open(file_path, mode="r", encoding="utf-8") as f:
            ArgumentHandler.compile_code(f.read(), output_type, compiler_opts)

    @staticmethod
    def run_compiled_file(file_path):
        """
        Runs a compiled
        """

        abs_path = path.abspath(file_path)
        subprocess.call(abs_path)
        # TODO: Run executable
