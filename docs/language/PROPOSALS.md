Each will be properly fleshed out as an RFC later.
However, it will be nice to have Raccoon not diverge from Python too much

## POSSIBLE ADDITIONS

- Calling C

    ```py
    @extern('C')
    def sleep(seconds: i32) -> i32
    ```

    `extern` block

    ```py
    @extern('C'):
        def sleep(seconds: i32) -> i32
        def echo(chars: ptr char, len: i32)

    ```

    When declaring a C function, types are required because the interface expects types

- Multiline lambda [In Progress]

    ```py
    map(
        lambda x:
            if x == 1:
                0
            else:
                5
        , array
    )

    map(
        lambda x:
            if x == 1:
                0
            else:
                5
        , array)

    map(
    lambda x:
        if x == 1:
            0
        else:
            5
    , array)

    map(lambda x:
        if x == 1:
            0
        else:
            5
    , array)

    map(
        (lambda x:
            if x == 1:
                0
            else:
                5),
        array
    )

    map((lambda x:
        if x == 1:
            0
        else:
            5
        ), array
    )

    map((lambda x:
        if x == 1:
            0
        else:
            5),
        array
    )

    map(
        (
            lambda x:
                if x == 1:
                    0
                else:
                    5
        ),
        array
    )

    map(
    (lambda x:
        if x == 1:
            0
        else:
            5),
    array)

    ```


- Coefficient expression [In Progress]

    ```py
    n = 2
    2n == 4
    (3)n == 6
    4(n) == 8
    ```


- Revamped type annotation & Generics [In Progress]

    ```py
    # Type anotation
    index: int = 9

    """
    ERROR

    index: int  # variable needs to be initialized.
    """

    # Type argument
    nums: list[int] = []

    # Optional type
    age: int? = 45

    # Function type
    fn: (int, int) -> int = sum

    # Tuple type
    value: (int, int) = (1, 2, 3)

    # Union type
    identity: int | str = 'XNY7V40'

    # Type relationship
    Person < Mammal
    Mammal > Person
    Person == Person

    # Generics
    class Person[T, U](A, B) where T < Person:
        def __init__(self, name: T, age: U):
            self.name = name
            self.age = age

    jane = Person[str, int]('Jane Doe', 45)

    class StaticArray[const N, T]:
        def __init__(self):
            self.buffer = Buffer[N, T]()
    ```

- More operators [In Progress]

    ```py
    class Num:
        # ...
        def __plus__(self, other):
            return Num(self.value + other.value)

        def __sqrt__(self):
            return Num(√(self.val))

        def __square__(self):
            return Num(self.val²)

    a, b = Num(2), Num(3)

    sum = a + b
    rooted = √a
    squared = a²
    ```

- Hygenic macro metaprogramming [In Progress]

    Raccoon's decorators are macros.

    ```py
    @foo("Hello world!")

    @foo "Hello world!"

    @foo:
        print("starting game")

    @debug
    def foo():
        print("starting game")


    @macro
    def foo(string: string):
        pass

    @macro
    def foo(block: block[statement]):
        @map:
            return $(statement ;)

    @macro
    def debug(fn: function):
        if "debug" in @flags:
            return fn
    ```

    When calling macros, you can omit the parentheses.

    Macros cannot reference variables outside their scope. Macros cannot have loops as well.

- Function declaration
    ```py
    def add(a: int, b: int) -> int
    def add(int, int) -> int
    def display(str)
    ```

- Type alias

    ```py
    alias IdentityFunc[T] = (T) -> T
    ```

- Character

    ```py
    ch0 = c'a'
    ch1 = c'\n'
    ch2 = c'\uff'
    ch3 = c'\890'

    string = ch0 + ch1

    if c'a' <= ch <= c'z':
        print(ch)
    ```

- Regex literal

    ```js
    regex = /\d+/
    ```

- None handling

    ```py
    def get_optional() -> char?:
        return c'name' if cond else None

    if identity := get_optional():
        print(identity)

    ch = get_optional()

    """
    ERROR

    ord(ch) # ord function exists for char but not NoneType
    """

    codepoint = ord(ch) if ch else None
    codepoint = ord(ch?)
    ```

- Additional reserved keywords

    ```py
    dyn, new, abstract, data, const, ref, ptr, val, match, let, var, interface, where, macro, typealias
    ```


- UFCS

    ```py
    ls = [1, 2, 3, 4]
    len(ls)
    ls.len()
    ```

- `const` keyword

    ```py
    const pi = 3.141

    def map(const array, const f):
        t = []
        for i in array:
            t.append(f(i))
        return t
    ```

- New versions of certain functions and objects by default

    ```py
    map, sum, filter, sum, join

    map(array, lambda x: x + 1)
    ```

- Explicit reference

    ```rust
    num2 = ref num
    num3 = num2
    ```

- Pointers

    ```nim
    num2 = ptr num
    num2 += 1
    num3 = val num2
    ```

- New named tuple syntax
    ```py
    named_tup = (name="James", age=10)
    named_tup.name
    ```

- Introducing more primitive types

    ```py
    u8, u16, u32, u64, usize
    i8, i16, i32, i64, isize
    f32, f64
    ```

- Match statement

    Does exhaustiveness checks.

    ```py
    match x:
        case Person(name, age): 1
        case [x, y = 5, z]: y # List
        case (x, y = 5, 10, *z): x # Tuple and NamedTuple
        case {x, y = 5, 10, *z}: x # Set
        # case { x: 'x', y: 'y',  **z}: x
        case 10 or 11 and 12: x
        case 0..89: 10
        case _: 11
    ```

- Partial application

    ```py
    add2 = add(2, _)
    add10 = add(_, 10)
    ```


- Cast function

    ```py
    animals = [Cat(), Dog(), ...]

    """
    ERROR

    animals[0].meow() # Need to cast to a type
    """

    cast[Cat](animals[0]).meow()
    ```

- Overloading functions and methods based on arity and types

    ```py
    def add(a: str, b: str):
        return a + '_' + b

    def add(a: int, b: int):
        return a + b

    def add(a, b, c):
        return a + b + c

    add("Hello", "world")
    add(1, 2)
    add(1, 2, 3)
    ```

- Abritary precision integer and float literal

    ```py
    integer: BigInt = b.123457890123456789012345678901234567890
    floating: BigFloat = b.123457890123456.789012345678901234e-567890
    ```

- Symbols

    ```py
    sym: Symbol = s'Hello'
    ```

- Hexadecimal, binary and octal floating point literal

    ```py
    decf = 12.3e+1
    hexf = 0x1f.3p+1
    octf = 0o16.3e+1
    binf = 0b11.3e+1
    ```

- Underscore meaning discarded value or unprovided value

    ```py
    for _ in (1:11):
        print("Hello")

        """
        ERROR

        print(_)
        """
    f = add(2, _)
    ```

- Revamped enums (ADTs)

    ```py
    enum class Option[T]:
        Ok(value: T)
        None

    identity: Option[str] = Option.None

    match identity:
        case Some(value): value
        case Err: raise Exception()
        case _: pass

    identity: int | str = 'XNY7V40'
    ```

- Revamped abstract classes

    ```py
    abstract class Observable:
        def __init__(self):
            self.subscriptions: [Subscription]

        abstract def notify()
        abstract def add_subscription(sub: Subcription)
    ```

- Revamped data classes

    Maybe look for another keyword

    ```py
    data class Pet(name, age):
        def __str__(self):
            return f"Pet(name={self.name}, age={self.age})"

    data class Person(name: str, age: int, bases=(Specie))
    data class Identity[T](id: T)

    john = Person("John", 50)
    id = Identity(504)
    ```

- Inline assembly

    ```py
    @asm(arch="x86", syntax="intel"):
        """
        mov eax, [ebx]      ; Move the 4 bytes in memory at the address contained in EBX into EAX
        mov [var], ebx      ; Move the contents of EBX into the 4 bytes at memory address var. (Note, var is a 32-bit constant).
        mov eax, [esi-4]    ; Move 4 bytes at memory address ESI + (-4) into EAX
        mov [esi+eax], cl   ; Move the contents of CL into the byte at address ESI+EAX
        """
    ```

- Goroutine-like green threads

    Replace async functions with goroutine-like green thread implementation.

    ```py
    import time

    c1: chan[str]
    c2: chan[str]

    def count(sec: int, c: chan[str]<-):
        while True:
            c <- f"Every {sec}s"
            time.sleep(sec)

    async count(1, c1)
    async count(2, c1)

    while True:
        # if-elif-else acts like select-case
        if msg := <- c1:
            print(msg)
        elif msg := <- c2:
            print(msg)
    ```

    OR

    ```py
    import time

    c1: Chan[str]
    c2: Chan[str]

    def count(sec: int, c: SendChan[str]):
        while True:
            send(c, f"Every {sec}s")
            time.sleep(sec)

    async count(1, c1)
    async count(2, c1)

    while True:
        # if-elif-else acts like select-case
        if msg := recv(c1):
            print(msg)
        elif msg := recv(c2):
            print(msg)
    ```
