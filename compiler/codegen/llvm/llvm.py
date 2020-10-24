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
        super().__init__()
        self.module = ir.Module()
        self.compiler_opts = compiler_opts
        self.raccoon_main = self.generate_raccoon_main()
        self.target_initialize()

    def target_initialize(self):
        """
        Initialize LLVM for target.
        """
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

    def generate_raccoon_main(self):
        fn_type = ir.FunctionType(
            ir.IntType(self.word_size),
            [
                ir.IntType(self.word_size), # argc: int
                ir.PointerType(ir.PointerType(ir.IntType(8))), # argv: ptr[ptr[i8]]
            ]
        )

        fn = ir.Function(self.module, fn_type, "__raccoon_main__")
        fn.args[0].name = "argc"
        fn.args[1].name = "argv"

        builder = ir.IRBuilder(fn.append_basic_block("entry"))
        return builder, fn

    def generate_function_signature(self):
        pass

    def generate_function(self):
        pass

    def add_passes(self):
        pass

    def dumps(self):
        return str(self.module)

