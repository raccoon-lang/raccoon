TODO: An interpreter that interprets wasm and JIT-compiles hot functions.
TODO: A library for interoperating with it.
TODO: Solve GIL, we don't mind slower code.

NOTE: To be started when compiler has been bootstrapped.


OPT:
    - Each function maps to a single varargs function that gets reused
        - interpreter state is a global value.
    - Static array on stack for fast allocations
