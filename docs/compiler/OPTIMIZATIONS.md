## CODEGEN
- Nillable types

    If we have a `Point|NoneType`, the generator represents it as `alloca %Point*`, and if Point exists,
    It is stored next to the Pointer for cache access improvement.

- Concurrency

    - Each functions can be a fork. Waits on compiling function when there is a dependency.
    - Each instantiation is completely parallelizable.
    - Each module can be compiled separately.

- Incremental compilation

    - Adding function and type impl frame structure so that untouched modules and dependencies don't get recompiled
    - Caching each module's AST. Checking for dependency changes from the AST.
    - Try the interpreter.

    #### IMPLEMENTATION

    - Every folder with source file has a .ram (Raccoon Metadata) file
    - This .ram file contains binary AST represntation of exported types or functions for each module in the folder


- Unused Imports

    - Don't import at import declaration point, instead wait until the import element is used.

- High-level Optimizations

    I decided agianst an MIR for now because I don't see the benefit for the use cases (in module and cross-module instantiation) I have in mind. Binaryen is AST-based and it doesn't have problems with optimizations.

    IR adds a layer of complexity. I can simply copy the AST nodes I need and operate on that.

- Frames

    Frames allows the sema to type check instantiationx faster, rather than walking the AST each time.

- Instantiation

    Because instantiation rely on frames and are pretty much self sufficient, they are parallelizable.
