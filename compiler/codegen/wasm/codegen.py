"""
This module generates WebAssembly binary from Raccoon lowered AST.
"""
from compiler.options import CompilerOptions


class WasmCodegenVisitor:
    """
    This class walks an AST and generates wasm binary.
    """

    def __init__(self, ast, compiler_opts=CompilerOptions()):
        self.ast = ast
        self.wasm_binary = []
        self.compiler_opts = compiler_opts

    def act(self):
        pass

    def start_visit(self):
        pass
