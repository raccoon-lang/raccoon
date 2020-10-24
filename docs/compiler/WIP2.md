### CHANGES

I decided to simplify the compiler's implementation. The post-syntactic phase of the compiler will use AST for semantic analysis and code generation.

Here are some things that have been removed from this iteration.

- **Frame**

    It is an pipeline optimization for speeding up type checking, but it will also consume memory. I decided to type check using the AST instead.

- **IR**

    Decided to use the AST for every phase until the there is a need to use something else.

- **Multiple Inheritance**

    It requires a costly vtable and each type having an associated supertype list for dynamic type checking. It makes type checking and dynamic dispatch an expensive operation.

I have outlined the entire processes of the new implementation below.

### TOKEN EXTRACTION VISITOR

This visitor copies all the tokens referenced by the AST and makes freeing the old list of tokens possible.

#### SEMANTIC VISITOR

- SYMBOL TABLE

    Symbol table is a stack of scopes. Each scope is a table of symbols and their information.

    Stack is chosen because, scopes are likely not to be highly nested.

    ```py
    symbols = [
        { # scope 0
            "name": "",
            "typed": {
                "var": SymbolInfo(
                    kind=SymbolKind.Variable,
                    ast_ref=()
                ),
                "func": SymbolInfo(
                    kind=SymbolKind.Variable,
                    ast_ref=(),
                ),
                "Person": SymbolInfo(
                    kind=SymbolKind.Class,
                    ast_ref=(),
                    instances=[
                        [(0, 1), (2, 0)]
                    ]
                )
            },
            "untyped": {
                "ls": SymbolInfo(
                    kind=SymbolKind.Variable,
                    ast_ref=(),
                    element_types=[(0, 1)]
                ),
            }
        },
    ]
    ```

    Untyped refers to list or buffer types whose element type is not know until the end of the [function] scope.

    **SymbolInfo**

    It contains information about each symbol. Some of the information include:

    - INSTANCES

        For types and functions alike, an instantiation list is maintained for when codegen needs to happen. Instance is the concrete type signature of a function call or field layout of a type instantiation.

        ```py
        func_instances = [
            [1, 2, 5, 5]
        ]
        ```

        ```py
        type_instances = [
            [(0, 1), (0, 2)]
        ]
        ```

        Each function instance is stored as the field layout of the argument and return types.

        Type annotations only specify constraints. The instances represent the field layout

        ```py
        class Thing:
            def __init__(self, id, value):
                self.id = id
                self.value = value

        Thing("id", 2.0) # Thing: {ptr[int],int,int|f64}
        Thing(1.0, 2)    # Thing: {f64|int}
        ```

    - IMPORTS

        Imports is a map of elements imported from other modules. Imported elements are not resolved at declaration point, until they get to used in the current module's code.

- TYPE ID, INHERITANCE LISTS, SUBTYPE RANGE AND OVERRIDES

    Each type id contains two indices for easy identification. The first index points to the corresponding inheritance list and the second index (which is the type index) is used to identify the type within its inheritance tree.

    An inheritance list represents a single inheriatance tree and it is updated when a class is added to the tree. The types are stored in a pre-order manner in the inheritance list.

    Each type id has an associated subtype range which is useful for type-checking and dynamic dispatch.

    In addition to the subtype ranges, a type id also has an associated overriden methods

    ```py
    inheritance_lists = [
        [ # inheritance index 0
            TypeInfo("int", subtype_range=(0,1), overrides=["__plus__"]) # type index 0
        ]
    ]
    ```

    The first set of inheritance lists are reserved for primitive types.

    **Primtive Type Indices**

    primitive types  | value
    -----------------|---------
    void             | 0.0
    int              | 1.0 -> i32 or i64 depending on paltform
    i8               | 2.0
    i16              | 3.0
    i32              | 4.0
    i64              | 5.0
    uint             | 6.0 -> u32 or u64 depending on paltform
    u8               | 7.0
    u16              | 8.0
    u32              | 9.0
    u64              | 10.0
    f32              | 11.0
    f64              | 12.0

    Before codegen, the lists are merged into one, updating the type indices as well as their range.


- GLOBAL DEALLOCATABLE LIST

----------

### SEMANTIC PROCESS

```py
symbols = [
    { # scope 0
        "typed": {
            "var": SymbolInfo(
                kind=SymbolKind.Variable,
                ast_ref=()
            ),
            "func": SymbolInfo(
                kind=SymbolKind.Variable,
                ast_ref=(),
            ),
            "Person": SymbolInfo(
                kind=SymbolKind.Class,
                ast_ref=(),
                type_id=(13,1),
                instances=[
                    [(0, 1), (2, 0)]
                ]
            )
        },
        "untyped": {
            "ls": SymbolInfo(
                kind=SymbolKind.Variable,
                ast_ref=(),
                element_types=[(0, 1)]
            ),
        }
    },
]
```

The `SemanticVisitor` visits all ast nodes, checks for semantic consistency, gather semantic information and finally generates code. This is possible because requires declaration of symbols before usage.


### Prelude

```py
class str:
    def __init__(self, capacity: int = 10):
        self.buffer = malloc[i8](10)
        self.capacity = capacity
        self.len = 0
```


### Semantic Objects
- Class Definition
- Function Definition
- Assignment
- Import
- Accesses
    - Index
    - Field
- Control Flow
    - If/Else/Elif
    - Yield
    - Return
    - Assert
    - Pass
    - Break
    - Continue
    - Raise
    - With
    - Try/Except/Else/Finally
    - For
    - While
- Operations
    - Function Call
    - Comprehension
    - Operator
    - Named Expression
    - Constructions
        - List
        - Dict
        - Set
        - Tuple
        - Namedtuple
    - Literal
        - Bool
        - Integer
        - Float
        - ImagFloat/ImagInteger
        - String
        - ByteString
    - Type ?


#### Function Signature

**Semantic Checks**
- Check params names do not conflict with each other  ✅
- Check params types exist
- Check generics annotation names do not conflict with each other
- Check generics annotation names do not conflict with existing names

**Type Checks**
- Type check default values against their type annotations

**Symbol Table Update**
- Save function in symbol table ✅
- Create a new scope in symbol table  ✅
- Save typed params in symbol table ✅
- Save untyped list param in symbol table

**Allowed Semantics**
- Function name can conflict with existing allowing shadowing
- Function param names can conflict with existing allowing shadowing

#### Function Body


#### Class Definition
