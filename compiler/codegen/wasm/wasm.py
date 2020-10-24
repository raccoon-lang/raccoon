"""
This module generates WebAssembly binary from Raccoon lowered AST.
"""
from compiler import CompilerOptions
from compiler.codegen import Codegen


class WasmCodegen(Codegen):
    """
    """

    def __init__(self, semantic_info):
        super().__init__(semantic_info)
        self.module = []
