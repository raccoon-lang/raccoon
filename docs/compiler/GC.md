

## GARBAGE COLLECTION

- Automatic Reference Counting (ARC)

    Swift uses a reference counting system to determine when to deallocate a variable. In release mode, it deallocates after the last expression it is used.

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

- Static Reference Tracking (SRT) [WIP]

    I'm proposing a different style of ARC that is not susceptible to reference cycles and perhaps more efficient because ref counting is done at compile-time. I'm going to call it `Static Reference Tracking` for now because I am not aware of any literature on it.

    Static Reference Tracking (SRT) is a deallocation technique that tracks objects' lifetimes at compile-time and can break reference cycles statically.

    ```
    foo {
        a      = Obj1()
        b      = Obj2()
        c      = Obj3()
        d      = Obj4()

        free_owned_deallocatable :: b

        c <- a = Obj3() <- Obj1()

        set_global_deallocatable_ptr :: has objects it needs inner functions to deallocate

        bar (c, a, d) { // function call; knows nothing about parent function
            a <- c = Obj1() <- Obj3() :: reference cycle!
            e      = Obj5()

            free_owned_deallocatable :: e

            qux (d) { // function call; knows nothing about parent function
                free_transferred_deallocatable :: d
            }

            # Transferred deallocatables are freed at the end of the scope.
            # It is costly to deallocate them in the middle of the function because it has checks.
            free_transferred_deallocatable :: a, c
        }
    }
    ```

    `free_transferred_deallocatable` deallocates what it needs to and increments the ptr.

    ##### GLOBAL DEALLOCATABLE LIST

    Each thread/coroutine has its own global deallocatable list.

    ```
    GLOBAL_DEALLOCATABLE_PTR -> GLOBAL_DEALLOCATABLE_LIST
    GLOBAL_DEALLOCATABLE_LIST {
        foo:
            (object: ptr _, len: uint, next_deallocate: ptr _), :: d
            (object: ptr _, len: uint, next_deallocate: ptr _), :: a
            (object: ptr _, len: uint, next_deallocate: ptr _), :: c
        ...
    }
    ```

    In this case, `foo` lays out how it wants inner functions to deallocate its objects.

    ##### CAVEATS
    - Inner functions cannot deallocate arguments until scope ends.

        One possible solution will be to take advantage of a `free_owned_deallocatable` call and sneak a `free_transferred_deallocatable` in.
        Also assigning to None, like `c = None`, can be used to signify that we want to have a `free_transferred_deallocatable` early in the code.

    - Guarantees are broken if Raccoon code interoperates with non-Raccoon code.

    - Objects shared between threads will need runtime reference counting of forks.

        - In this case, the commpiler may note thread boundaries and apply an ownership semantics similar to Rust.


    ##### HOW IT PREVENTS REFERENCE CYCLES

    The compiler tracks every variable in the program. It is able to determine if two object reference each other from the variables.
    With this information, the compiler can determine when the two objects are no longer referenced and deallocate them together.

    Creating statically-unknown number of objects dynamically isn't an issue for SRT because objects are bound to statically-known names at compile-time with the exception of temporary objects whose lifetimes are well-defined and statically determinable. The compiler can know when two object reference each other from their names and it can determine when the two objects are no longer referenced and deallocate them together.

    ##### POINTER ALIASING

    Raw pointer aliasing affects all dellocation techniques. SRT, Tracing GCs, ARC, ownership semantics, etc. That is why we have references. They are an abstraction over pointers, something our GCs understand. Raw pointer misuse is a problem for any GC technique.

    ##### REFERENCE INTO A LIST

    If there is a reference to a list item, the entire list is not freed until all references to it and/or its elements are dead.

    ```py
    scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    fourth = scores[3]

    some = scores[3:7]
    ```


##### REFERENCES

https://stackoverflow.com/questions/48986455/swift-class-de-initialized-at-end-of-scope-instead-of-after-last-usage

https://forums.swift.org/t/should-swift-apply-statement-scope-for-arc/4081

