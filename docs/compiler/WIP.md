## THIS DOCUMENT IS STALE, CHECK [WIP2](#WIP2.md)

## IMPLEMENTATION

- PARTS

    ### TOKEN EXTRACTION VISITOR

    This visitor copies all the tokens referenced by the AST and makes freeing the old list of tokens possible.

    ### SEMANTIC VISITOR

    This visitor walks the AST in a single pass and gathers informatation about the program, checks for semantic errors and instantiates polymorphic types and functions.

    Like an interpreter, the analyzer runs through the syntax tree and expects that referenced symbols be declared/defined prior to their use. There are a few exceptions. Untyped list element type is the union of all the types passed into the list, so its type may not be known at the point of declaration. The nice thing about this however is that we always know the union type of the untyped list by the time we reach the scope's end.

    This declaration before use semantics saves us the ordeal of deferring and figuring out missing semantic information at a later point.


    - PRIMITIVE TYPES

        Primitive types are machine intrinsic types known to the compiler. Each primitive type has an associated integer value. This allows the compiler to reference them in terms of their integer value rather than their symbol which is more efficient.

        primitive types  | value
        -----------------|---------
        void             | 0
        int              | ? -> i32 or i64 depending on paltform
        i8               | 3
        i16              | 4
        i32              | 5
        i64              | 6
        uint             | ? -> u32 or u64 depending on paltform
        u8               | 11
        u16              | 12
        u32              | 13
        u64              | 14
        ptr              | 17


    - CONCRETE ABIS

        A concrete abi is a list of one or more primtive types or concrete abis.
        Since concrete abis are going to be stored in data stuctures (e.g. symbol table) and will be referenced multiple times later, we map each abi to an index in a custom hashtable.

        The concrete abi technically starts at index 20, to leave index space for primitive types.

        ```py
        concrete_abis = {"14.1.1", "1.4.15"}
        ```

    - TYPE IDS

        Type ids are needed for efficient type lookup at runtime (in the case of dynamic dispatch) and compile time (in the case of static dispatch).
        Conceptual types are mapped to index in a list because they are usually accessed more than they are stored. So fast access with lists is desirable.

        ```py
        type_ids = [TypeId(ast=t, parents=p, instances=i), ...]
        ```

        Conceptual types are given indices based on their order of definition and inheritance hierarchy. In a single program, a type gets ranked first if it is defined before another type or if it is the parent of another type.

        TODO: Needs work.

        ```py
        # TODO
        class A:
            def foo(self):
                return 1

        class B(A):
            pass

        class C(A):
            def foo(self):
                return 2

        class D(B, C):
            pass

        d = D()
        d.foo() # => 2

        class F:
            pass

        class E(C, B):
            pass

        e = E()
        e.foo() # => 2

        """
        A: 1
        B: 2
        C: 3
        D: 4
        E: 5
        F: 6
        """

        """

        """
        ```

    - IMPORTS

        imports is a map of elements imported from other modules. Imported elements are not resolved at declaration point, until they get to used in the current module's code.

        ```py
        imports = {
            "name": (path="module.com", alias=True),
        }
        ```

    - CONCEPTUAL TYPES

        Types are conceptual and some may not have a concrete abi until they are instantiated.


    - INSTANCES

        Instances are formed from giving a type's field layout or a function's signature layout a concrete abi.

        ```py
        function_instances = [1, 2, 3] # concrete_abi indices
        ```

    - FRAMES

        Frame captures a function's type flow which is usually determined by calls, ops and control flow constructs in the function's body.

        ```py
        def foo(a, b):
            x = bar(a, 500)
            y = b + x
            if cond:
                z = "Hello"
            else:
                z = y
            return z

        """
        Function Frame: Used for rapid type checking.

        def foo(a, b):
            x = bar(a, 500)
            y = b + x
            if cond:
                z = "Hello"
            else:
                z = y
            return z

        frame foo(0, 1): # no type annotation
            2: bar(0, int)
            3: +(2, 1)
            4: str | 3
            _: 5

        FunctionFrame(
            param_size=2,
            type_flow=[
                ("bar", [0, "lib.int"]),
                ("+", ["lib.i64", 1]),
                (".union", [12, 3]),
                (".return", [4]),
            ]
        )
        """
        ```

        Functions (frames) are mapped to index in a list because they are usually accessed more than they are stored. So fast access with lists is desirable.

        ```py
        function_frames = [FunctionFrame(ast=f, instances=i), ...]
        ```

    - SYMBOL TABLE

        Symbol table holds relevant information the about symbols in each scope.

        ```py
        symbol_table = [
            { # Scope 0
                "model": Symbol.Variable(
                    constant=False,
                    type="",
                    abi=1,
                ),
                "sum": Symbol.Function(index=0)
            },
            { # Scope 1
                "Array": Symbol.Type(index=0)
            }
        ]
        ```

    - IR

        Raccoon has a simple IR that gets generated at the end of each function and top-level walk. This IR is designed to allow fast codegen.

        The IR has the follwoing IR
        - simple basic blocks and phi isntruction; extended BBs may supported later.
        - simple linear instructions.
        - register-based SSA
        - linear instructions
        - ops are function calls
        - calling convention and abi information
        - function type flow information
        - structs, vectors, pointers and machine-intrinsic types
        - no signed / unsigned types. signedness is op-based
        - different types of call
            - regular function call
            - magic function call
            - intrinsic function call

        ```
        def foo(n):
            x = 0
            for i in range(n):
                x = x * i
            return x

        def foo(n: _):
            [type_flow]{...}

            entry:
            x: i32 = 0
            _2: generator = range(n: i32)

            header:
            _3: i32 = next(_2: generator)
            _4: i32 = phi((_x, entry), (_6, body))
            _5: i32 = cmp(0: i32, _3: i32)
            br(cmp: i32, body, exit)

            body:
            _6: i32 = intrinsic.mul(_4: i32, _5: i32)

            exit:
            _7: i32 = phi((_x, entry), (_6, body))
            ret _7



        ```

        ```
        ```

        Possibility of adding typeflow to the IR.

    - SEMANTIC CHECKS AND SPECIALIZATIONS

        Function Definition
        - Check argument name conflict
        - Create function frame

        Class Definition
        - Check for inheritance cycle

        Variable Definition
        - ...

        Function Call
        -

        ---


        - Saves function declarations
            - Checks for argument name conflict

        - Saves type declarations
            - Checks for inheritance cycle

        - Creates function frame
            - Unionizes variable types

        - Creates type frame
            - Resolves diamond problem

        - Declares function instances
            - Check argument positions and type restrictions

        - Declares type instances
            - Check recursive instantiation

        - Check elements in wrong context
            - Check for certain flow statements at top level

        - Tracks variable-object lifetimes

        - Create function instantiations
            - Check methods exist on types

        - Create function impl frame for lib

        - Create type impl frame for lib

        - Create type instantiations

        - Link modules

        - Magic method impl check

        - Semantic

- IDEOLOGY

    ### LANGUAGE ELEMENTS

    These are the basic concepts of execution in a language. Other concepts are an abstraction over these.

    - **Variables**: x, foo
    - **Indexing**: x.y, y[0]
    - **Calls or Ops**: foo(x, y), +x, x + y
    - **Control Flow**: if, for, while, yield, return, raise, etc.

    ### MISSING SEMANTIC INFORMATION

    - What type does a symbol have/return (variable, call, indexing, control flow)

    - Does symbol exist? Raccoon deos not have to deal with this issue because of its declaration before use rule.

---

#### EXAMPLE SEMA AND CODEGEN

- Function
- Assignment
- BinOp
- Call
- Return
- Loop

```py
def add(a: int, b: int) -> int:
    c = a + b
    return c

a = add(1, 2)
b = add(1.0, 3.0)
```

- semantic phase
- codegen phase
    - llvm
    - wasm


sematic state
- symbol_table
- concrete_abis
- imports

- codegen
- compiler_opts
- current_path
- current_scope_level

---

#### SOLVING DYNAMIC DISPATCH


Dynamic Dispatch
- Allocation of memories
- Setting of pointers




if else check for dispatch


if type(x) == B:
    m = x.m
    y = x.y

type(d) == B
type(d) == C






1
2 - Base : 2 - 5
3
4
5 - Derived


super_types = [
    B {
        child_addresses = []
    }
]



Each type hold static array of 64-bit bitflags.
The bitflags represent every multiple inheritance point in the program

child type = [x, y, z]

A conceptual post-order list of inheritance is kept.
Every MI point starts a fork below the existing list.

A super type belongs to a set of MI forks
A sub type belongs to a set of MI





