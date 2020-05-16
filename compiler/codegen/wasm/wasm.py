"""
This module generates WebAssembly binary from Raccoon lowered AST.
"""
from compiler import CompilerOptions
from ..codegen import Codegen


class WasmCodegen(Codegen):
    """
    """

    def __init__(self, compiler_opts=CompilerOptions()):
        self.module = []
        self.compiler_opts = compiler_opts
