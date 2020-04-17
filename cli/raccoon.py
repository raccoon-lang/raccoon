#! /usr/bin/env pipenv run -- python3
import click
from argument_handler import ArgumentHandler


@click.command(options_metavar="[options]")
@click.option("--version", "-v", is_flag=True, help="Show Raccoon version")
@click.option(
    "-c",
    "--compile",
    "compile_string",
    nargs=1,
    help="Compile Raccoon code",
    type=str,
    metavar="<code>",
)
@click.option("--ast", is_flag=True, help="Output Raccoon AST")
@click.option("--tokens", is_flag=True, help="Output Raccoon lexed tokens")
@click.option("--sema", is_flag=True, help="Output Raccoon sematic analysis phase")
@click.argument(
    "program_file", nargs=1, required=False, type=click.Path(), metavar="[program file]"
)
def app(version, program_file, compile_string, ast, tokens, sema):
    """
    raccoon.py samples/test.co --ast
    """
    ctx = click.get_current_context()

    if version:
        click.echo("Raccoon 0.0.1")

    elif program_file:
        output_type = ArgumentHandler.get_output_type()
        ArgumentHandler.compile_file(program_file, output_type=output_type)

    elif compile_string:
        output_type = ArgumentHandler.get_output_type()
        ArgumentHandler.compile_code(compile_string, output_type=output_type)

    else:
        click.echo(ctx.get_help())
        ctx.exit()


if __name__ == "__main__":
    app()
