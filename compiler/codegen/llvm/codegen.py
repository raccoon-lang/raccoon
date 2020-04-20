"""
This module generates LLVM IR from Raccoon lowered AST.
"""
from llvmlite import ir, binding as llvm
from compiler.options import CompilerOptions


class LLVMCodegenVisitor:
    """
    This class walks an AST and generates an LLVM module.
    """

    def __init__(self, ast, compiler_opts=CompilerOptions()):
        self.ast = ast
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

    def act(self):
        pass

    def start_visit(self):
        pass
