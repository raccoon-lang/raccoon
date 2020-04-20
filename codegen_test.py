from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.codegen.llvm.codegen import LLVMCodegenVisitor

code = '''
def add(a: int, b: int) -> int:
    return a + b
'''


tokens = Lexer(code).lex()
ast = Parser(tokens).parse()
module = LLVMCodegenVisitor(ast).start_visit()

print(module)
