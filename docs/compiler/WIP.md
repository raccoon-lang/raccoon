## IMPLEMENTATION

- PROCESS

    - Lex
    - Parse
    - Shed cache and irrelevant tokens
    - ...
    - Create functions instantiations  and structures
    - Create frames
    - ...
    - Lower AST to LL AST
    - Generate LLVM


    ### THE BIG WALK

    The Big Walk is a single pass on the AST that gather informatation about the program to be later used

    - SYMBOL TABLE

        Contains information about elements of the programs which can be used in type checking and inference

        - variables
        - functions and parameters
        - types
        - structures
        - function instantiations

        Optimizations
            - Symbols refercence values from AST rather than store it in the table.
            - A single global symbol table for all scopes


    - DEPENDENCY GRAPH

        Dependency graph helps in checking fro cyclic dependencies.

        - function call
        - module import
        - class inheritance


        Optimizations
            - ...


    - CFG

        Control flow graph is needed for type inference. It is used to create a frame.

        Optimizations
            - ...



    - FRAMES

        Frames are abstract definition of a function and type, added to a library or object
        for helping with future linkage.

        - functions
        - types


        The compiler generates a frame like this for top-level function **called** at the top level
        ```
        Function Foo
        - (1, 2, 3) { 1|None, 2|3  } -> 1
            - (1, 2) { 1 } -> 2
                - ...
        ```

        Then the compiler generates instantiations for the top-level frames
        ```
        Function Foo
        foo(int, str)
        foo(int, int)
        ```

        After all instantiations have been collected, compiler walks the frame, typechecks and generate code at the same time. The compiler can parallelize this task.


        This same approach goes for types **instantiated** at the top level.

        Optimizations
            - The instantiations can be hashed for fast lookup.

- CODE

    ```py
    def get_relevant_tokens(parser, ast):
        """
        Gets tokens referenced by AST by walking accross the AST tree.
        """
        from copy import deepcopy

        tokens = {}
        walker = ast
        tree_position_indices = []

        for (name, value) in vars(walker).items():
            if name == "index":
                tokens[value] = deepcopy(parser.tokens[value])

            obj = value

        return tokens

    def reset_parser(self):
        """
        Frees resources like cache and tokens and reset fields.
        """

        self.tokens = []
        self.tokens_length = len(tokens)
        self.cursor = -1
        self.row = 0
        self.column = -1
        self.cache = {}
        self.combinator_data = {}
        self.revert_data = (self.cursor, *self.get_line_info())

        return (ast, tokens)

    def get_tokens(self, code):
        """
        Tokenizes code and stores the generated tokens.
        """

        from ..lexer.lexer import Lexer

        self.tokens = Lexer(code).lex()
    ```
