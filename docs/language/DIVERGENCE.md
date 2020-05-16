### SYNTACTIC AND SEMANTIC DIVERGENCE FROM PYTHON

- Eval / exec
    - There is no of eval or exec in Raccoon.

        ```py
        eval('2 + 3')
        ```

- Declaration

    - Declaration of variables, classes and funcions must be statically determinable

        Because Raccoon needs to determine a class, function and variable at compile-time, it doesn't support dynamic loading of variables, classes or functions the way Python does. It also doesn't provide a lot of hooks found in builtin module

- Type annotations

    - Type annotations is used in semantic analysis. CPython doesn't take advantage of type annotations.

        ```py
        num: int = 50

        """
        ERROR

        num = "Hello"
        """
        ```

- Fields

    - Deleting fields isn't supported.

        ```py
        """
        ERROR

        del john.name
        """
        ```

    - `vars` return named tuples.

        ```py
        print(vars(john)) # (name='John', age=45)
        ```

    - After initial assignment, fields cannot change types

        ```py
        class Person:
            def __init__(self, name):
                self.name = name

        john = Person("John")
        """
        ERROR

        john.name = 54
        """
        ```

- List

    - Slices do not return list, instead they return a slice object

        ```py
        ls = [1, 2, 3, 4, 5, 6, 7]
        sl = [:5] # Slice[int]

        print(sl) # [1, 2, 3, 4]
        ```

- Tuples

    - A tuple can only be indexed with a signed integer literal.

        ```py
        tup = (1, 2, 3)
        tup[0]

        """
        ERROR

        tup[n]
        """
        ```

    - A tuple element can be modified in Raccoon.

        ```py
        tup = (1, 2, 3)
        tup[0] = 4
        ```

    - Directly or indirectly, a tuple can't be added to itself.

        Basically anything that makes assigning a reference/name with its previous tuple value possible is not allowed. Only identity assignment is allowed. It's a recursive problem, that static analyzers generally can't resolve and hate.

        ```py
        tup1 = (1, 2)
        tup2 = (5, 6)

        for i in range(x):
            tup3 = (1, *tup1)
            tup2 = (*tup3, *tup1)

        # Identity assignment is allowed
        tup3 = tup3
        tup3 = (*tup3)

        """
        ERROR

        for i in range(x):
            tup2 = (*tup2, *tup1)

        for i in range(x):
            tup2 = tup2 + tup1

        for i in range(x):
            tup3 = (*tup2, 1)
            tup2 = (tup3, tup1)
        """
        ```


- Functions

    - Raccoons doesn't support spreading any iterable except tuples and named tuples as arguments to a function.

        ```py
        dc = { 'name': 'John', 'age': 45 }
        ls = [1, 2, 3]
        tup = (1, 2, 3)
        named_tup = (one=1, two=2, three=3)

        some_func(*tup)
        some_func(**named_tup)

        """
        ERROR

        some_func(**dc)
        some_func(*ls)
        """
        ```

- Magic methods

    - Raccoon does not support `__new__` method since classes are statically created.

- Imports

    - Raccoon resolves imported modules at compile-time

        ```py
        name, age = "John", 45

        from objects import Person

        john = Person(name)
        ```

    - Imports in a module are not exposed to outside modules

        ```py
        # moudle.ra
        import another

        another.print()
        ```


        ```py
        import module

        """
        ERROR

        module.another.print() #
        """
        ```

- Variable

    - When a variable changes its type, Raccoon shadows it. It is essentially given a new memory address.

        ```py
        num = 10
        print(num)

        def func():
            global num
            num = 0.005 # This variable now points to another variable
            print(num)

        func()
        ```

    - Field types cannot be shadowed.

- Integers

    - `int`s are represented as 64-bit signed integers.

        This means ints overflow when they exceed `-4_611_686_018_427_387_904 < x < 4_611_686_018_427_387_903` bounds.

        ```py
        num = 4_611_686_018_427_387_902 + 1
        print(num) # -4_611_686_018_427_387_903
        ```

        NOTE: It is possible overflow checks may be added in the future.

- StopIteration

    - StopIteration is expected to be returned rather than raised.

        ```py
        class list:
            def __iter__(self)
                return list_iterator(self)

        class list_iterator:
            def __init__(self, list):
                self.list = list
                self.counter = 0

            def __next__(self):
                if self.counter < len(list):
                    result = list[self.counter]
                    self.counter += 1
                    return result
                else:
                    return StopIteration()
        ```

        For loops use StopIteration to halt iteration on iterables. Generators are inherently interable.

- Concurrency

    - Global interpreter lock

        Raccoon is not affected by the GIL.

    - Async / await

        Async / await can be built on top of go-type green threads.

        ```py
        async def foo(id):
            sleep(3)
            print(f'Done sleeping {id}')

        foo(1)
        foo(2)
        foo(3)
        ```

    - Unawaited async function may not get executed in CPython

        NOTE: The following semantic documentation may change.

        Raccoon's async / await is very different from Python's. Unawaited asynchronous functions are executed on separate green threads.


- settrace

    - Raccoon doesn't support modifying variables before the frame is run

        ```py
        """
        ERROR

        import sys.settrace
        sys.settrace(value_changer)
        """
        ```

- Source file

    - Multiple encoding support. Unlike CPython, Raccoon only support UTF-8 files.


- Scoping rules

    - Variables declared in loops or if (unless the variable appear in all branches of the if statement) cannot be accessed outside the statement scope.

    ```py
    for i in iterable:
        x = 35
    """
    ERROR

    print(x)
    """

    while condition:
        y = 35
    """
    ERROR

    print(y)
    """

    if condition:
        z = 35
    elif condition2:
        z = 45
    """
    ERROR

    print(y)
    """

    if condition:
        z = 35
    else:
        z = 45

    print(z) # Okay
    ```

- Literal

    - Raccoon does not support upper case letters to signify literal base.

        ```py
        bin_n = 0b10101
        oct_n = 0o17867
        hex_n = 0x1FFFE

        """
        ERROR

        bin_n = 0B10101
        oct_n = 0O17867
        hex_n = 0X1FFFE
        """
        ```

    - Raccoon doesn't support the wide entire uppercase / reversed prefixes Python support in prefix strings.

        ```py
        r"Hello"
        u"Hello"
        f"Hello"
        b"Hello"
        rb"Hello"
        rf"Hello"

        """
        ERROR

        R"Hello"
        U"Hello"
        F"Hello"
        B"Hello"
        rB"Hello"
        Rb"Hello"
        RB"Hello"
        rF"Hello"
        Rf"Hello"
        RF"Hello"
        """
        ```

    - Raccoon uses `im` for imaginary numbers

        ```py
        imag = 3 + 4im
        ```

        - Instead of the 'j' suffix, Raccoon expects an 'im' suffix

- Generators

    - Generators are copyable and are passed by value

        ```py
        def get_nums():
            for i in range(10):
                yield i

        x = get_nums()
        y = x

        list(x) # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        list(y) # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ```

- Classes

    - Class bodies can't contain arbitrary expression. They can only contain bindings and function definitions.

    - Class base class parameters can only be identifiers.

        ```py
        class Test():
            test = 5
            """
            ERROR

            5 + 500
            lambda x: x
            match x:
                5 : 200
                _ : 300
            """

            def foo(self):
                pass

        """
        ERROR

        class Test(object=70):
            pass
        """
        ```


- Exception handling

    - except argument must be statically-known type.

        ```py
        try:
            raise TypeError()
        except TypeError as e:
            print(e)

        """
        ERROR

        get_error_class = lambda: TypeError

        try:
            raise TypeError()
        except get_error_class() as e:
            print(e)
        """
        ```

- Comprehension

    - `if` clauses in comprehensions are replaced by `where` clauses in Raccoon

        ```py
        odds = [i for i in range(10) where i % 2]
        ```

- Operators

    - Raccoon's xor operator is '^'

        ```py
        2 ^ 5 == 25
        ```

    - Raccoon's xor operator is '||'

        ```py
        0b101 || 0b011 == 0b001
        ```
