from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.codegen import LLVMCodegenVisitor

code = '''
def add(a: int, b: int) -> int:
    return a + b
'''


tokens = Lexer(code).lex()
ast = Parser(tokens).parse()
module = LLVMCodegenVisitor(ast).start_visit()

print(module)
