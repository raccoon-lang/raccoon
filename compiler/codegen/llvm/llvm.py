"""
This module generates LLVM IR from Raccoon lowered AST.
"""
from llvmlite import ir, binding as llvm
from compiler import CompilerOptions
from compiler.codegen import Codegen


class LLVMCodegen(Codegen):
    """
    """

    def __init__(self, compiler_opts=CompilerOptions()):
        self.module = ir.Module()
        self.compiler_opts = compiler_opts
        self.target_initialize()

    def target_initialize(self):
        """
        Initialize LLVM for target.
        """
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

    def generate_function_signature(self):
        pass

    def generate_function(self):
        pass

    def add_passes(self):
        pass

    def dumps(self):
        return str(self.module)

