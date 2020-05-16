"""
Properties of IR:

- linear instructions
- register-based SSA
- basic-blocks with phi merging
- ops are function calls
- calling convention and abi information
- function type flow information
- structs, vectors, pointers and machine-intrinsic types
- no signed / unsigned types. signedness is op-based


Example:

```
def foo(name: { }, age: i64):
    _type_flow = () {}
    _1 = intrinsic.add(age: i64, 1: i64)
    _2 = __plus__(age: i64, 0: i64)
    ret _2
```

"""


class IL:
    """
    """
    pass


class Function(IL):
    def __init__(self):
        pass
