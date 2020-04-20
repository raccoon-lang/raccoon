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
        - function(Dog { name: str }) - 1
        - function(Type) - 2
        - funtion(Super) - 3

    - lists
        - list[Any] - 3
        - list[Dog { name: str }] - Not supported
        - list[Type] - 2
        - list[Super] - 3


    ##### POSSIBLE SOLUTIONS
    - Value witness table
    - Type inference algorithm
    - Type interface and instatiation list
    - Function interface and instantiation list
        -  ({ id: _ }, { age: _ }) :: print
            - ({ id: int }, { age: int }) :: print
            - ({ id: str }, { age: int }) :: print



- DECLARATION

    ##### TYPES
    - ABSOLUTE CYCLIC DEPENDENCY

        When it is statically known that two elements directly or indirectly depend on each other.

        ##### AFFECTED ELEMENTS
        - module import
        - inheritance
        - reference (cycle)
        - constructor


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
        - inherited fields
        - overriden inherited method
        - function overloads
        - function arguments


    - WRONG CONTEXT

        For certain tokens that the parser allowed through but exist in the wrong context

        ##### AFFECTED ELEMENTS
        - yield statement
        - return statement
        - rest expression


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

    - EFFECTS [FUTURE]

        Making each function have an implicit effect and being able check the effect of any function.

        Examples of effects:
        - Exceptions
        - File access
        - Network access


- CONSISTENCY

    ##### TYPES
    - PARAMETER TYPE AND RETURN TYPE

        If a function has a parameter type restrictions, it must also have a return type and vice versa. If the function returns nothing, the return type can be ommitted.

        ##### AFFECTED ELEMENTS
        - functions

    - RECURSIVE REDUCTION OR EXPANSION

        When a static construct is able to break static guarantees like its length through recursion or loops.

        ##### AFFECTED ELEMENTS
        - tuple added to itself
        - recursive varargs function

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

- EXTENSIONS [FUTURE]

    Allowing some aspects of the compiler be extended to third party code

    Features like:
    - SRT
    - Effects


## NOTES

- Philosophy

    Raccoon has certain worldviews that make the semantic analysis phase easier to understand and implement.

    - A method, in Raccoon implementation, is a regular function, a method, a closure or an operator.

        Each method can be instantiated multiple times by calling them and each instantiation has an abi.

    - Every object has a structure and classes are how we describe or classify those structures. We only think in terms of classes when we need to compare an object's structure with a class' blueprint structure.

    - Global variables are variables that persist throughout the lifetime of a program. Global variables include variables declared at the top-level, class fields and variables from a parent scope referenced by a closure.

    - Inheritance / variance is an abstraction we only care about for validation/type-checking purposes. Relationship between objects are only seen in terms of how similar their structures are.

    - Field conflict in multiple inheritance is seen as a structural problem rather than a type one.

        As mentioned earlier, types are only important for type checking type annotations and the language is largely driven by structural inferences and instantiations based on those structure. So conflict like this is seen as a structure problem. Sub classes choose a general structure for themselves so that they won't have conflicting fields.


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

    - Slice

        A slice is a view into a list so it holds a reference to a list and has the same lifetime as the list.

        ```py
        ls = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        sl = ls[1:4] # sl: Slice[int]
        ```

        ##### IMPLEMENTATION

        ```py
        """
        { start: uint, end: uint, list: ptr _ } :: Slice

        Can be optimized

        { start: ptr _, len: uint }
        """
        ```


- Lists

    - Uninitialized list

        ```py
        ls = [] # ls: [str]

        def func(ls):
            ls.append('hi')

        func(ls)
        ```

        If a list is uninitialized, we wait until it is first used. Its type is inferred based on how it is used.

        However if one needs an any list, the type needs to be specified upfront.

        ```py
        ls: [Any] = []

        ls.append(Person("John"))
        ls.append(Cat("Sam"))
        ```

        An empty list can be used. It has a type `[Any]`.

        ```py
        ls = []

        print(ls, type(ls)) # [], [Any]
        ```



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
        john: { name: str, age: int }
        """
        ```


- Generators

- Closures

    `closure(*args) = func(*args, ptr env)`

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

        Functions are actually instantiations with abis and any number of types can conform to the instantiation abi.

        ```py
        """
        cat: { name: str } :: Cat
        john:  { age: int, name: str } :: Person
        hibiscus: { name: int, age: int } :: Plant
        elephant: { name: int } :: Herbivore
        """

        print_name(cat)
        print_name(john)
        print_name(hibiscus)
        print_name(elephant)

        """
        INSTANTIATIONS

        (ref { _: str }) -> void :: foo
        (ref { _: int, _: str }) -> void :: foo
        (ref { _: int, ... }) -> void :: foo
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
                get_name: (Cat) -> str
                """
                ```

            - List

                ```py
                pets: [Pet] = []

                print(pets)

                pets.append(Cat())
                pets.append(Dog())

                print(pets[0])

                """
                pets: list[Cat | Dog]
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

                cars: list[Vehicle] = [Toyota(), Mazda()]

                cars[0].clone()

                """
                animals: list[Cat | Dog]
                """
                ```

        * Contravariance

            - Functions
                ```py
                alias IdentityFunc[T]: (T) -> T

                def identity_animal(x: Animal):
                    return x

                def identity_cat(x: Cat):
                    return x

                compare: IdentityFunc[Cat] = identity_animal

                """
                ERROR

                compare: IdentityFunc[Animal] = identity_cat
                """
                ```
        * Any

            If a union of types do not share a common ancestor apart from object, it is classified `Any`.
            Note that Any is a user-facing concept only. The compiler still keeps union of possible types.

            Any has the abi `{ type_id: uint, obj: ptr _ }`.

            - List

                ```py
                def encounter(a, b):
                    print(f"{a.name} meets {b.name}")

                objects: [Any] = [Cat(), Person(), ...]

                pet_1 = pets[index_1]
                pet_2 = pets[index_2]

                encounter(pet_1, pet_2) # (Any, Any) -> void or (Cat | Person | ..., Cat | Person | ...) -> void
                ```


        ##### IMPLEMENTATION

        Variables with union types don't make it far because to use them with any function require that any field or method accessed through them exists across the types.

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

        identity -= 5 # str does not implement a `-` operand
        """

        if type(identity) == int:
            identity = 5
        else:
            identity = 7

        """
        identity: int
        """
        ```

        A collection of Any

        ```py
        def encounter(a, b):
            print(f"{a.name} meets {b.name}")

        objects: [Any] = [Cat(), Person(), ...]

        pet_1 = pets[index_1]
        pet_2 = pets[index_2]

        encounter(pet_1, pet_2)

        """
        objects: list {
            len: uint,
            capacity: uint,
            ... {
                0: ptr { type_id: uint, cat: ptr _ },
                1: ptr { type_id: uint, person: ptr _ },
                ...
            }
        }

        def encounter(
            a: { type_id: uint, obj: ptr _ },
            b: { type_id: uint, obj: ptr _ },
        ):
            # type_ids are localized to benefit from computed gotos.
            @goto a.type_id:
                @label "::Dog":
                    a = * unsafe_cast.[Dog](obj)
                @label "::Person":
                    a = * unsafe_cast.[Person](obj)
                ...

            @goto b.type_id:
                @label "::Dog":
                    a = * unsafe_cast.[Dog](obj)
                @label "::Person":
                    a = * unsafe_cast.[Person](obj)
                ...

            print(f"{a.name} meets {b.name}")
        """

    #### IMPLEMENTATION

    Raccoon is all about structural typing. It sees type unsafety and covariance as union types and inheritance as intersection types.

- Introspection

    #### IMPLEMENTATION

    Raccoon supports some level of introspection. The type of an object can be introspected for example. Since types of variables are known at compile time, specialized functions are generated for introspect-like behavior.


    ```py
    def __type__(obj: int):
        return int
    ```
