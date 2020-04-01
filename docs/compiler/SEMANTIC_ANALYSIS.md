# POLYMORPHISM

## FIELDS
#### CLASS INDEPENDENT

Similar field names and field types, but fields may be different positions.

    Dog {name: str, age: int}
        allows - Person {name: str, age: int}

#### TYPE INDEPENDENT

Similar types, but fields may have different types.

    Type {name: int, age: int}
        allows - Type {name: str, age: str}

#### POSITION INDEPENDENT

Similar fields, but field may be in different positions and fields may have different types.

    Super {name: int, age: int}
        allows - Sub {age: int, name: int}


### TYPES AFFECTED
- functions
    - function(Any) - 3
    - function(Dog { name: str}) - 1
    - function(Type) - 2
    - funtion(Super) - 3

- lists
    - list{Any} - 3
    - list{Dog { name: str}} - Not supported
    - list{Type} - 2
    - list{Super} - 3


### POSSIBLE SOLUTIONS
- Type witness table

--------------

## FUNCTIONS

### POSSIBLE SOLUTIONS
- Dispatch table
- MRO table

---------------




# DECLARATION
