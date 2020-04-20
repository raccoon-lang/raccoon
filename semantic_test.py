from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.semantic import (
    TokenExtractionVisitor,
    MainSemanticVisitor
)

annotated_function_code = '''
def add(a: int, b: int) -> int:
    return a + b

a = add(1, 2)

b = add(40, 3)
'''


declarations_code = '''
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
'''

tokens = Lexer(declarations_code).lex()
ast = Parser(tokens).parse()
tokens = TokenExtractionVisitor(ast, tokens).start_visit()
semantic_values = MainSemanticVisitor(ast, tokens).start_visit()
