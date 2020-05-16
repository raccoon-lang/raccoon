#! /usr/bin/env pipenv run -- python3

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import TokenExtractionVisitor, SemanticVisitor
from compiler.codegen import LLVMCodegen

annotated_function_code = """
def add(a: int, b: int) -> int:
    return a + b

a = add(1, 2)

b = add(40, 3)
"""


declarations_code = """
glob = 500

def foo(a, b):
    global glob

    def closure(a):
        return a + b

    if a == b:
        x = 5
    else:
        x = 20

    return glob + a + b + x

class Foo:
    pass

class Bar(Foo):
    def __init__(self, hello):
        self.hello = hello
"""


def main():
    tokens = Lexer(declarations_code).lex()
    ast = Parser(tokens).parse()
    tokens = TokenExtractionVisitor(ast, tokens).start_visit()

    print('\nast >> ', ast)

    # Semantic and codegen
    llvm_codegen = LLVMCodegen()
    semantic_state = SemanticVisitor(ast, tokens, llvm_codegen).start_visit()

    print('\nsemantic_state >> ', semantic_state)


if __name__ == "__main__":
    main()
