There will be two ways of generating webassembly binary:
- Via LLVM (basically for free), which will be slow and can benefit from optimizations.
- With this implementation, which is meant to be fast direct codegen with zero optimization and is suitable for the intrepreter.

