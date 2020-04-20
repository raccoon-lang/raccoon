## IMPLEMENTATION

- ASPECTS

    ### THE MAIN SEMANTIC VISITOR

    The main semantic visitor is a visitor that walks the AST in a single pass and gathers informatation about the program to be later used.

    - SYMBOL TABLE

        Contains information about elements of the programs which can be used in type checking and inference

        ##### ELEMENTS
        - variables
        - functions and parameters
        - types
        - structures
        - function instantiations

        ##### OPTIMIZATIONS
        - Symbols refercence values from AST rather than store it in the table.
        - A single global symbol table for all scopes


    - DEPENDENCY GRAPH

        Dependency graph helps in checking for cyclic dependencies.

        ##### OPTIMIZATIONS
        - module import
        - class inheritance


        Optimizations:
            - Implement as hashset and check if element already exist, which can probably be done with symbol table


    - FRAMES [UNECESSARY - TO BE REMOVED]

        Frames are abstract definition of functions and types and they give the following benefits:
        - Reduce code bloat
        - Faster type inference
        - Reduce memory usage
        - Make linkable object files and static libraries possible

        Elements:
            - functions
            - types


        The compiler generates a frame like this for top-level function **called** at the top level
        ```
        Function foo
        - (1, 2, 3) { 1|None, 2|3, _ } -> 3
            - (2, 1) { 2, 1|str } -> 2
                - ...

        Types in `{}` reference types in `()`.
        Types after `->` reference types in `{}`
        Types in `()` reference types in the parent's `{}`
        `_` represents the return type of a child at that index.
        ```

        Then the compiler generates instantiations for the top-level frames
        ```py
        """
        Function foo
        (int, str) -> void :: foo
        (int, int) -> void :: foo
        (ref { _: int, _: int } :: [Car, Person], int) -> void :: foo # applies to [Car, Person]
        """
        ```

        After all instantiations have been collected, compiler walks the frame, typechecks each instantiation and generate code.

        This same approach goes for types **instantiated** at the top level.

        ```py
        """
        Type Car
        - { 1, 2, _ }
            - { _, 2 }
                - ...
        """
        ```

        And the instantiations

        ```py
        """
        Type Car
        { _: int, _: str } :: Car
        { _: int, _: int } :: [Car, Person]
        """
        ```

        Note that while type checking we are concerned with the types themselves, but when generating function instantiation code or storing type instantiations, we are concerned with the structure.

        Instantiations of multiple types may be associated with a single structure.

        Optimizations:
            - The instantiations can be hashed for fast lookup.
            - Instantiation generation and type check is parallelizable.

    - INSTANCES

        #### TYPES
        - Instance Frames - has incomplete type information
        - Concrete Instances - has complete type information

- LANGUAGE ELEMENTS
    - Indexing: x.y, y[0]
    - Calls: foo(x, y), +x, x + y
    - Control flow constructs: if, for, while, yield, return, raise, continue, break

- WHAT WE NEED FROM MISSING ELEMENTS
    - what type is it (variable)
    - does it exist (function, class, variables)
    - what arguments (function)


- CANONOICALIZING
    - hex, oct an bin literal to dec equivalent
    - None and False to 0
    - True to 1


- LOWERING
    ```py
    for x in iter:
        print(x)
    ```

    ```py
    x = iter.next()
    while x is not StopIteration:
        print(x)
        x = iter.next()
    ```


-------------------

- WIP
    Function
    - create function frame
        - check duplicate argument names
        - check recursive calls
        - unionizing types
        - create function isntances
        - create type instances

    ForStatement
    - type check variables


    ```py
    - (1, 2, 3) { 1|None, 2|3, MISSING(foo) } -> 3
    - (2, 1) { 2, 1|str } -> 2
    - ...
    ```

