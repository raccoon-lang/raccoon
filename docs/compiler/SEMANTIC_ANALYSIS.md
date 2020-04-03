# POLYMORPHISM
#### TYPES
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


#### AFFECTED ELEMENTS
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


#### POSSIBLE SOLUTIONS
- Type witness table
- Type inference algorithm
- Type interface and specialisations list
- Function interface and monomporphisations list
    - print({id}, {age})
        - print({id: int}, {age: int})
        - print({id: str}, {age: int})



# DECLARATION

#### TYPES
- ABSOLUTE CYCLIC DEPENDENCY

    When it is statically known that two elements directly or indirectly depend on each other.

    #### AFFECTED ELEMENTS
    - function calls
    - type instantiation
    - module import
    - inheritance


- USE BEFORE DECLARATION

    When a reference is used before it is declared.

    #### AFFECTED ELEMENTS
    - variables
    - types
    - functions


- CONFLICT RESOLUTION

    Conflict emerges when there are two occurence of a particular element

    #### AFFECTED ELEMENTS
    - inherited methods
    - function overloads
    - method overrides


- WRONG CONTEXT

    For certain tokens that the parser allowed through but exist in the wrong context

    #### AFFECTED ELEMENTS
    - yield statement
    - return statement
    - rest expression


#### POSSIBLE SOLUTIONS
- Dispatch table
- MRO algorithm
- Scope tree
- Call graph
- Import graph
- Inheritance tree


# RESTRICTIONS
#### TYPES
- TYPE RESTRICTION

    Type annotation prevents a constant/variable from being used in a way that does not conform to the type's blueprint.

    #### AFFECTED ELEMENTS
    - variables
    - classes
    - functions


- CONSTANT RESTRICTION

    Constant annotation prevents re-assigning to a constant.

    #### AFFECTED ELEMENTS
    - variables


# LOWERING
#### TYPES
- AST CONVERSION

    Abstract ASTs are converted to Low-level AST.

    #### AFFECTED ELEMENTS
    - Abstract ASTs

- MACRO EXPANSION

    Converts macros to Low-level AST at semantic analysis time.

    #### AFFECTED ELEMENTS
    - macros
