## AREAS OF SEMANTIC ANALYSIS

- POLYMORPHISM

    ##### TYPES
    - CLASS INDEPENDENT

        Similar field names and field types, but fields may be different positions.

            Dog {name: str, age: int}
                allows - Person {name: str, age: int}

    - TYPE INDEPENDENT

        Similar types, but fields may have different types.

            Type {name: int, age: int}
                allows - Type {name: str, age: str}

    -  POSITION INDEPENDENT

        Similar fields, but field may be in different positions and fields may have different types.

            Super {name: int, age: int}
                allows - Sub {age: int, name: int}


    ##### AFFECTED ELEMENTS
    - function applications
        - function(Any) - 3
        - function(Dog { name: str}) - 1
        - function(Type) - 2
        - funtion(Super) - 3

    - lists
        - list{Any} - 3
        - list{Dog { name: str}} - Not supported
        - list{Type} - 2
        - list{Super} - 3


    ##### POSSIBLE SOLUTIONS
    - Type witness table
    - Type inference algorithm
    - Type interface and specialisations list
    - Function interface and monomporphisations list
        - print({id}, {age})
            - print({id: int}, {age: int})
            - print({id: str}, {age: int})



- DECLARATION

    ##### TYPES
    - ABSOLUTE CYCLIC DEPENDENCY

        When it is statically known that two elements directly or indirectly depend on each other.

        ##### AFFECTED ELEMENTS
        - function calls
        - type instantiation
        - module import
        - inheritance


    - USE BEFORE DECLARATION

        When a reference is used before it is declared.

        ##### AFFECTED ELEMENTS
        - variables
        - types
        - functions


    - CONFLICT RESOLUTION

        Conflict emerges when there are two occurence of a particular element

        ##### AFFECTED ELEMENTS
        - inherited methods
        - function overloads
        - method overrides
        - function arguments
        - class fields


    - WRONG CONTEXT

        For certain tokens that the parser allowed through but exist in the wrong context

        ##### AFFECTED ELEMENTS
        - yield statement
        - return statement
        - rest expression


    ##### POSSIBLE SOLUTIONS
    - Dispatch table
    - MRO algorithm
    - Scope tree
    - Symbol table
    - Dependency graph
    - Import graph
    - Control flow graph
    - Inheritance tree


- RESTRICTIONS

    ##### TYPES
    - TYPE RESTRICTION

        Type annotation prevents a constant/variable from being used in a way that does not conform to the type's blueprint.

        ##### AFFECTED ELEMENTS
        - variables
        - classes
        - functions


    - CONSTANT RESTRICTION

        Constant annotation prevents re-assigning to a constant.

        ##### AFFECTED ELEMENTS
        - variables

    - ARGUMENT POSITION

        There are a bunch of rules that affect how arguments are positioned based on parameter specification.

        ##### AFFECTED ELEMENTS
        - arguments

- LOWERING

    ##### TYPES
    - AST CONVERSION

        Abstract ASTs are converted to Low-level AST.

        #### AFFECTED ELEMENTS
        - Abstract ASTs

    - MACRO EXPANSION

        Converts macros to Low-level AST at semantic analysis time.

        #### AFFECTED ELEMENTS
        - macros



## NOTES

- Philosophy

    Raccoon has certain worldviews that make the semantic analysis phase easier to understand and implement.

    - A function, in Raccoon implementation parlance, is a regular function, a method, a closure or an operator.
    - Every object has a structure and classes are how we describe or classify those structures. We only think in terms of classes when we need to compare an object's structure with a class' blueprint structure.
    - Inheritance / variance is an abstraction we only care about for validation/type-checking purposes. Relationship between objects are only seen in terms of how similar their structures are.
    - Global variables are variables that persist throughout the lifetime of a program. Global variables include variables declared at the top-level, class fields and variables from a parent scope referenced by a closure.

- Analysis artifacts

    - Scope tree

        - Object end-of-lifetime (EOL) list

            Each scope contain a list of objects' EOL.
            Starting from the declaration scope, each object's EOL point is adjusted as new references to it are encountered in the declaration scope or in a parent's scope.

        - Type frames

            A type frame is created for each function.
            This type frame holds a list of functions called in the function's scope.
            To instantiate a type frame, we need to validate that the types in the scope truly have an associated function instantiation. Validations for existing instantiations are skipped.

            An instantiation [shouldn't clone the AST](https://github.com/crystal-lang/crystal/issues/4864#issue-251536917).

        - Type method resolution order (MRO) lists (C3 linearization)

        - Type instantiations

        - Function instantiations

- Indices and Slices

    - Negative indices
        ```py
        subarray = array[:-2]
        value = array[:-2]
        ```

        ##### IMPLEMENTATION

        Since bound checks are going to be made anyway, we should find a way to make positive indices as fast as they would have been and negative indices a check slower.

        ```py
        value = 0

        if -1 < index > len(array): # positive indices
            value = array[index]
        elif 0 > index >= -len(array): # negative indices
            value = array[len(array) + index]
        else: # out of bounds indices
            raise OutOfBoundsError('...')
        ```

- Lists

    - Uninitialized list
        ```py
        ls = []

        """
        ERROR

        print(ls)
        """

        def func(ls):
            ls.append('hi')

        func(ls)
        ```

        ##### IMPLEMENTATION

        If a list is uninitialized, we wait until it is first used. Its type is inferred based on how it is used.

        If it is passed as an argument to a function, its type is determined by the argument type, otherwise it is determined by its usage in the function's body.

- Variable

    - No special declaration syntax
        ```py
        num = 45
        print(num)

        def func():
            nonlocal num
            num = 56
            print(num)

        func()
        ```


    - Shadowing
        ```py
        num = 45
        num = "hi"
        ```

        #### IMPLEMENTATION

        A local variable can be shadowed. In the above example, the second `num` is a totally different variable from the first `num`. However, global variables and fields cannot be shadowed.


- Fields

    - Adding new fields
        ```py
        class Person:
            def __init__(self, name):
                self.name = name

        john = Person("John")
        john.age = 45
        ```

        ##### IMPLEMENTATION

        The fields of an object is the collection of fields attached to the object through its entire lifetime. The only exception is global variables. They can't be given new fields.

        ```py
        """
        john: Object [ name: str, age: int ]
        """
        ```


- Generators

- Closures

    `closure = func(*args, ref env)`

    ```py
    def higher_order():
        x = 0

        def closure():
            x = 10
    ```

    Variables referenced within the closure can be optimized (moved into the closure) if not used, referenced or returned by parent function or sibling closures. This way, the `env` reference can be omitted.

- Decorators

- Callable objects

- Type inference

- Typing

    - Duck typing
        ```py
        def foo(bar):
            bar.name
        ```

        ##### IMPLEMENTATION

        Structural typing can be used in place of duck typing. In fact, Raccoon sees type and object relationships structurally.

        Functions are actually instantiations with abis that conform to argument binary structures.

        ```py
        """
        cat: Cat [ name: str ]
        john: Person [ age: int, name: str ]
        hibiscus: Plant [ name: int, age: int ]
        elephant: Herbivore [ name: int ]
        """

        foo(cat)
        foo(john)
        foo(hibiscus)
        foo(elephant)

        """
        INSTANTIATIONS

        foo: (Object [ str ])
        foo: (Object [ *, str ])
        foo: (Object [ int, * ])
        """
        ```

    - Type unsafety
        * Type union
            ```py
            identity: int | str

            if condition:
                identity = 45
            else:
                identity = 'XNF452423'

            """
            identity: int | str
            """
            ```

        * Covariance

            A subtype value can be assigned where a supertype value is expected.

            - Variables and fields
                ```py
                animals: Animal

                if condition:
                    animals = Cat()

                """
                animals: Animal | Cat
                """
                ```

            - Function arguments
                ```py
                def get_name(animal: Animal):
                    return animal.name

                cat: Cat = Cat()

                get_name(cat)

                """
                get_name: (Object [ str, * ])
                """
                ```

            - List elements
                ```py
                animals: Animal = []

                animals.append(Cat())
                animals.append(Dog())

                print(animals[0])

                """
                animals: list{Cat | Dog}
                """
                ```

            - Inheritance
                ```py
                class Vehicle:
                    # ...
                    def clone(self) -> Vehicle:
                        return Vehicle(*self.fields)

                class Toyota(Vehicle):
                    # ...
                    def clone(self) -> Toyota:
                        return Toyota(*vars(self))

                cars: list{Vehicle} = [Toyota(), Mazda()]

                cars[0].clone()

                """
                animals: list{Cat | Dog}
                """
                ```

        * Contravariance

            - Functions
                ```py
                typealias IdentityFunc{T}: (T) -> T

                def identity_animal(x: Animal):
                    return x

                def identity_cat(x: Cat):
                    return x

                compare: IdentityFunc{Cat} = identity_animal

                """
                ERROR

                compare: IdentityFunc{Animal} = identity_cat
                """
                ```


        ##### IMPLEMENTATION

        Variables with uncertain types don't make it far because to use them with any function require that any field or method accessed through them exists across the types.

        ```py
        identity: int | str

        if condition:
            identity = 45
        else:
            identity = 'XNF452423'

        """
        identity: int | str
        """

        """
        ERROR!

        identity -= 5 # str doesn't have a `-` operand
        """

        if type(identity) == int:
            identity = 5
        else:
            identity = 7

        """
        identity: int
        """
        ```

        ```py
        animals: Animal = [Cat(), Dog()]

        """
        animals: list [
            len: usize,
            capacity: usize,
            buffer: ref buffer [
                0: ref Object [type: usize, cat: Cat],
                1: ref Object [type: usize, cat: Dog],
                ...
            ]
        ]
        """

        animal = animals[0]

        """
        animal: Cat | Dog
        """

        if animal := cast{Cat}(animal):
            animal.meow()
        ```

    #### IMPLEMENTATION

    Raccoon is all about structural typing. It sees type unsafety and covariance as union types and inheritance as intersection types.

- Introspection

    #### IMPLEMENTATION

    Raccoon supports some level of introspection. The type of an object can be introspected for example. Since types of variables are known at compile time, specialized functions are generated for introspect-like behavior.


    ```py
    def __type__(obj: int):
        return int
    ```
