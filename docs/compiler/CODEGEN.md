## ASPECTS OF CODEGEN

- NAME MANGLING [WIP]

    Symbols used in the symbol table are already mangled.

    ```
    functools.map(int,(int)->str)->[str]
    functools.filter([int],(int)->bool)->[int]
    ```


- LOWERING

    #### FOR LOOPS
    
    ```py
    for x in iter:
        print(x)
    ```

    ```py
    x = iter.next()
    while type(x) != StopIteration:
        print(x)
        x = iter.next()
    ```

