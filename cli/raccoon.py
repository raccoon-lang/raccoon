#! /usr/bin/env pipenv run -- python3

"""
TODO:
    This module needs to work almost like the `python` command but with some extensions.
    For example, currently the -c option works differently from python's -c option.
"""

import click
from argument_handler import ArgumentHandler


@click.command(options_metavar="[options]")
@click.option("--version", "-v", is_flag=True, help="Prints toolchain version")
@click.option(
    "-c",
    "--compile",
    "compile_string",
    nargs=1,
    help="Compiles Raccoon code without running it",
    type=str,
    metavar="<code>",
)
@click.option("--ast", is_flag=True, help="Prints AST")
@click.option("--tokens", is_flag=True, help="Prints lexer tokens")
@click.option("--sema", is_flag=True, help="Prints semantic information")
@click.option("--ll", is_flag=True, help="Prints LLVM IR")
@click.option("--wasm", is_flag=True, help="Prints Webassembly code")
@click.option(
    "-vv", "--verbose", is_flag=True, help="Prints debug information"
)
@click.argument(
    "program_file", nargs=1, required=False, type=click.Path(), metavar="[program file]"
)
def app(version, program_file, compile_string, ast, tokens, sema, ll, wasm, verbose):
    """
    raccoon.py test.ra --ast
    """
    ctx = click.get_current_context()

    if version:
        click.echo("Raccoon 0.0.1")

    elif program_file:
        output_type = ArgumentHandler.get_output_type()
        compiler_opts = ArgumentHandler.get_compiler_options()
        ArgumentHandler.compile_file(program_file, output_type, compiler_opts)

    elif compile_string:
        output_type = ArgumentHandler.get_output_type()
        compiler_opts = ArgumentHandler.get_compiler_options()
        ArgumentHandler.compile_code(compile_string, output_type, compiler_opts)

    else:
        click.echo(ctx.get_help())
        ctx.exit()


if __name__ == "__main__":
    app()
