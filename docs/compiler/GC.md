

## GARBAGE COLLECTION
In Swift, variables are deallocated in their declaration stack frames or parents of that. Never a child frame of the declaration scope. Raccoon takes a similar approach.

- Automatic Reference Counting (ARC)

    Typical ARC implementation cannot break reference cycles.

    ```py
    parent = Parent()

    """
    Parent_0 = 1
    """

    child = Child()

    """
    Parent_0 = 1
    child = 1
    """

    parent.child = child

    """
    Parent_0 = 1
    Child_0 = 2
    """

    child.parent = parent

    """
    Parent_0 = 2
    Child_0 = 2

    DEALLOCATION POINT
    ==================

    > Parent_0 decrements .child refs to 1
    Parent_0 = 1

    > Child_0 decrements .parent refs to 1
    Child_0 = 1

    problem:
    - both are still not destroyed
    """

    print('Hello!')
    ```

    Since lifetimes can be tracked statically, I don't see the runtime benefit of ARC.

- Static Reference Tracking (SRT)

    SRT is a deallocation technique that tracks objects' lifetimes at compile-time and can break reference cycles.

    - Non-concurrent programs

        ```py
        parent = Parent()

        """
        Parent_0 [ &parent ]
        """

        child = Child()

        """
        Parent_0 [ &parent ]
        Child_0 [ &child ]
        """

        parent.child = child

        """
        Parent_0 [ &parent ]
        Child_0 [ &child, &parent ]
        """

        child.parent = parent

        """
        Parent_0 [ &parent, &child ]
        Child_0 [ &child, &parent ]

        DEALLOCATION POINT
        ==================

        > unrefer parent (*parent = null)

        Parent_0 [ null, &child ]
        Child_0 [ &child, null ]

        > unrefer child (*child = null)

        Parent_0 [ null, null ]
        Child_0 [ null, null ]

        > deallocate objects with only null references

        problem:
        - uses more memory than ARC
        """

        print('Hello!')
        ```

    - Concurrent programs

        Ordinary SRT is not well-suited for concurrent programs because there is no statically known order to how threads execute.

        ```py
        async def foo(parent, child):
            print(parent, child)

        parent = Parent()
        child = Child()
        parent.child = child
        child.parent = parent

        for i in range(2):
            """
            increment Parent_0 (.forks += 1) [ &parent, &child ]
            increment Child_0 (.forks += 1) [ &child, &parent ]
            """
            foo(parent, child)

        print(parent, child)

        """
        COROUTINES

            0     1     2
            =================
            __main__
            |
            ---- foo
            |     |
            ---------- foo
            |     |     |
            .     .     .

        DECREMENT IN MAIN COROUTINE

        end of reference parent (*parent = null)
        end of reference child (*child = null)

        decrement Parent_0 (.forks -= 1) []
        decrement Child_0 (.forks -= 1) []

        DECREMENT IN OTHER COROUTINES

        Each forked coroutine will have an epilogue that decrements the objects they reference.
        """
        ```

        In this case, the main coroutine can't release the `parent` and `child` objects
        because they are referenced in the `foo` coroutines. Here we have to maintain a fork count to track the object's lifetime associated with each coroutine that referenced it.


    #### NOTES ON STATIC REFERENCE TRACKING

    **Creating statically-unknown number of objects dynamically**

    Creating statically-unknown number of objects dynamically isn't an issue for SRT because objects are bound to statically-known names at compile-time. With the exception of temporary objects whose lifetimes are well-defined and statically determinable.

    The issue of garbage collection comes into play when we are able to extend an objects lifetime beyond the declaration stack frame. This is amenable to static analysis, however, because such objects are required to be associated with statically-known names.

    ```py
    for i in range(some_number):
        """ Creation of temporary object """
        foo(Value())
        """ Destruction of temporary object """
    ```

    **Pointer aliasing**

    Raw pointer aliasing affects all dellocation techniques. SRT, Tracing GCs, ARC, ownership semantics, etc. That is why we have references. They are an abstraction over pointers, something our GCs understand. Raw pointer misuse is a problem for any GC technique.

    **Reference into a list**

    If there is a reference to a list item, the entire list is not freed until all references to it and/or its elements are dead.

    ```py
    scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    fourth = scores[3]

    some = scores[3:7]
    ```

    **Conditional deallocation**

    In a situation where the compiler cannot statically determine precisely the deallocation point of an object, probably due to runtime conditions, the compiler will choose the farthest deallocation point considering every possible condition branch.

    ```py
    def foo():
        string = "Hello"

        if some_runtime_condition:
            return "Hi"
        else:
            return string

    greeting = foo()
    print(greeting)
    print(greeting)

    """
    DEALLOCATION POINT
    ==================

    > deallocate string

    Dealloction of string will be at the top-level. Because it is the farthest deallocation point of all condition branches.
    """
    ```
