"""
This module generates LLVM IR from Raccoon lowered AST.
"""
from llvmlite import ir, binding as llvm
from compiler import CompilerOptions
from ..codegen import Codegen


class LLVMCodegen(Codegen):
    """
    """

    def __init__(self, compiler_opts=CompilerOptions()):
        self.module = None
        self.compiler_opts = compiler_opts
        self.target_initialize()

    def target_initialize(self):
        """
        Initialize LLVM for target.
        """
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
