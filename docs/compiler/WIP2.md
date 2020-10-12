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

    ```py
    symbol_table = [
        { # scope 0
            "typed": {
                "var": SymbolInfo(...),
                "func": SymbolInfo(...)
            },
            "untyped": {
                "ls": SymbolInfo(...),
            }
        },
        { # scope 1
            "typed": {
                "var": SymbolInfo(...),
                "func": SymbolInfo(...)
            },
            "untyped": {
                "ls": SymbolInfo(...),
            }
        }
    ]
    ```

    **SymbolInfo**

    It contains information about each symbol. Some of the information include:

    - INSTANCES

        For types and functions alike, an instantiation list is maintained for when codegen needs to happen. Instance is the concrete type signature or field layout of a function call or type instantiation.

        ```py
        func_instances = [
            [1, 2, 5, 5]
        ]
        ```

    - IMPORTS

        Imports is a map of elements imported from other modules. Imported elements are not resolved at declaration point, until they get to used in the current module's code.

        ```py
        {
            "name": SymbolInfo(
                path="module.com",
                alias=True
            ),
        }
        ```

- CONCRETE TYPE INDEX, INHERITANCE LISTS, SUBTYPE RANGE AND OVERRIDES

    Each type gets two indices for easy identification. The first index points to the corresponding inheritance list and the second index (which is the type index) is used to identify the type within its inheritance tree.

    An inheritance list represents a single inheriatance tree and it is updated when a class is added to the tree. The types are stored in a pre-order manner in the inheritance list.

    Each type index has an associated subtype range which is useful for type-checking and dynamic dispatch.

    In addition to the subtype ranges, a type index also has an associated overriden methods

    ```py
    lists = [
        [ # inheritance index 0
            { # type index 0
                "subtype_range": (0, 2)
                "overrides": [...]
            },
        ]
    ]
    ```

    The first set of inheritance lists are reserved for primitive types.

    **Primtive Type Indices**

    primitive types  | value
    -----------------|---------
    void             | 0.0
    int              | ? -> i32 or i64 depending on paltform
    i8               | 3.0
    i16              | 4.0
    i32              | 5.0
    i64              | 6.0
    uint             | ? -> u32 or u64 depending on paltform
    u8               | 11.0
    u16              | 12.0
    u32              | 13.0
    u64              | 14.0
    ptr              | 17.0

    Before codegen, the lists are merged into one, updating the type indices as well as their range.


- GLOBAL DEALLOCATABLE LIST



----------

### SEMANTIC PROCESS

```py
symbol_table = [
    { # scope 0
        "typed": {
            "var": SymbolInfo(
                ast_ref=()
            ),
            "func": SymbolInfo(
                ast_ref=(),
            )
        },
        "untyped": {
            "ls": SymbolInfo(
                ast_ref=(),
                list_type_indices=[]
            ),
        }
    },
]
```


#### Top Level

#### Function Definition

**Start of Function**
- Check function name conflict with existing
- Check params names conflict with each other
- Check params types exist
- Check generics annotation names conflict with each other
- Check generics annotation names conflict with existing names
- ...

**Body of Function**
-



