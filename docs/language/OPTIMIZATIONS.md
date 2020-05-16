- Type Unsafety

    Union types that cannot be resolved to a single type at compile-time are considered type unsafe and they incur some runtime performance cost. There are different ways this can be introduced from method dispatch to list of Any. Here is an contrived example:

    ```py
    if runtime_condition():
        x = "String"
    else:
        x = 500

    type(x)  # x: int | str
    ```

    While the compiler will still statically check for safety at compile time, it will add runtime checks that makes your implementation just a tad slower. Type unsafety may be okay during prototyping but it is usually not desired in production systems. Ralint can check for these kind of problems.
