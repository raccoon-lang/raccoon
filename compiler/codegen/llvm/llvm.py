"""
This module generates LLVM IR from Raccoon lowered AST.
"""
from llvmlite import ir, binding as llvm
from compiler import CompilerOptions
from compiler.codegen import Codegen


class LLVMCodegen(Codegen):
    """
    """

    def __init__(self, semantic_info):
        super().__init__(semantic_info)
        self.module = ir.Module()
        self.main = self.generate_main()
        self.generate_target_triple()
        self.target_initialize()

    def target_initialize(self):
        """
        Initialize LLVM for target.
        """
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

    def generate_main(self):
        int32 = ir.IntType(32)

        # Generate function signature
        fn_type = ir.FunctionType(
            int32, # return: int
            [
                int32, # argc: int
                ir.PointerType(ir.PointerType(ir.IntType(8))), # argv: ptr[ptr[i8]]
            ]
        )

        # Generate function.
        fn = ir.Function(self.module, fn_type, "main")
        fn.args[0].name = "argc"
        fn.args[1].name = "argv"

        # Add new basic blocks
        entry_bb = fn.append_basic_block("entry")
        exit_success_bb = fn.append_basic_block("exit.success")

        # Set basic block.
        builder = ir.IRBuilder(exit_success_bb)

        # Add return
        builder.ret(ir.Constant(int32, 0))

        # Move instruction pointer to entry bb.
        builder.position_at_start(entry_bb)

        return fn, builder, [exit_success_bb]

    def generate_target_triple(self):
        self.module.triple = llvm.get_default_triple()

    def generate_function(self):
        pass

    def add_passes(self):
        pass

    def generate(self):
        return self

    def dumps(self):
        return str(self.module)

