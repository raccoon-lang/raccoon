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


    - FRAMES

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

- PROCESS

    Semantic Analysis Structure
    TODO: To be documented properly

    ```
    token_extraction_visitor

        get_referenced_tokens

        reset_parser

    main_semantic_visitor

        canonicalize_literal

        create_symbol_table

        save_variable_declaration

        save_function_declaration
            check_argument_name_conflict

        save_type_declaration
            check_cyclic_dependency

        create_function_frame
            unionize_var_types
                type_check_if_statement
                type_check_while_statement
                type_check_for_statement
                type_check_comprehension

        create_type_frame
            resolve_diamond_problem

        declare_function_instance
            check_argument_position_and_types

        declare_type_instance

        track_lifetimes

    instantiation_visitor

        instantiate_function_declaration
            check_method_exist

        instantiate_type_declaration

        create_function_impl_frame # LIB

        create_type_impl_frame # LIB

    lower_ast

    link_modules

    generate_llvm_module
    ```


- WIP CODE

    ```py
    visitation
    symbol_table = {

    }

    scope
    ```

    ```py
    class FunctionFrame:
        def __init__(self, arg_types, body_types, return_type, sub_frames=None):
            self.arg_types = arg_types
            self.body_types = body_types
            self.return_type = return_type
            self.sub_frames = sub_frames

    class TypeFrame:
        def __init__(self, body_types):
            self.body_types = body_types
    ```
