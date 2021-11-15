## Interface Contract

The body of an untyped function defines its `interface contract`.

Observing the following example:

```py 
def add(a, b): 
    return a + b
```

`add` has the following interface contract: 

    [ T: impl __plus__.2 ](a: any T.0, b: any T.1)

- `[ T: impl __plus__.2 ]` reads as:

    T is a type that implements __plus__ method that takes 2 arguments 

- `(a: any T.0, b: any T.1)` reads as:

    a is a ref/val of some type T that implements a method `__plus__` a is the first argument.
    b is a ref/val of some type T that implements a method `__plus__` b is the second argument.

- `any` represents `ref` or `val` of the type.

When we then call `add`, given that the arguments satisfy the interface contract, we instantiate a concrete `add` at compile-time.

```py
x = add(1, 2)
```

`add` as used above has the instantiation `def add(int, int) -> int`.

The above illustration is an example of an `argument contract`. The arguments of `add` must **have types that can appear in certain positions of the `__plus__` function**.

On the other hand, there also a `return contract` that an instantiation may need to satisfy.

Say we have an abstract class with a method that allows the implementor to return any type.

```py
abstract class Giver:
    abstract def gift(self)

class StringGiver(Giver):
    def gift(self) -> str:
        return "string gift" # Has an str return type

class IntGiver(Giver):
    def gift(self) -> int:
        return 8080 # Has an int return type
```

The abstract class can then be used as part of a function's `interface contract`. 

```py
def iterate_gift(giver: Giver):
    for gift in giver.gift():
        print(f"{gift}")

iterate_gift(StringGiver()) # Okay because type returned by StringGiver.gift `str` implements __iter__ and __next__ which implements __str__ and so on.
iterate_gift(IntGiver()) # Error because type returned by IntGiver.gift `int` does not implement __iter__ and __next__.
```

Notice that `IntGiver` won't work with `iterate_gift` because while it satisfies its `argument contract`, it does not satisfy its `return contract`.

The `interface contract` of `iterate_gift` looks like this.

    [ 
        T: impl gift.1, 
        U: impl __iter__.1, 
        V: impl __next__.1,
        W: impl __str__.1, 
        X: str,
    ](
        a: ref T where [
            T returns U & V where [
                V returns W where [
                    W returns X
                ]
            ]
        ]
    )

There should always be a `base concrete type` resolution. Like `X: str` in the above example. You can think of it as a `base condition` needed to prevent a recursive function from hypothetically looping forever.

The only time a `base concrete type` may not be reached is when the value is returned.

```py
def iterate_gift(giver: Giver):
    return iter(giver.gift()).next()

s = iterate_gift(StringGiver()) # s has type `str` from the instantiation of iterate_gift.
```

Here `iterate_gift` has the following `interface contract`:

    [ 
        T: impl gift.1, 
        U: impl __iter__.1, 
        V: impl __next__.1,
    ](
        a: any T where [
            T returns U & V
        ]
    )

`iterate_gift` as used above has the instantiation `iterate_gift(void) -> str`. `void` because `StringGiver` has no field, so no space is allocated for it.

As mentioned before, what you do with the arguments of an untyped function determines the `interface contract` and the kind of monormorphisation allowed.


## Dynamic Dispatch

```py
givers = [StringGiver(), IntGiver()]

for giver in givers:
    giver.gift()
```

Let's assume `List` class is declared like this:

```py
class List[T]:
    # ...
```

It expects all its items to be of type `T`, but we have given it two concrete types, `StringGiver` and `IntGiver`. 

When designing a statically typed language, you quickly hit type safety issues like this with `homogenous container types`. Types that store multiple items of the same memory layout usually contiguously.

A language that does not support heterogeneity is no fun. Raccoon is not such language.

`T` in `List[T]` does not necessarily mean you can only store objects of the same concrete type in list. You can also store dynamically dispatched objects. So `dyn AbstractClass` instead of `Class` or `impl AbstractClass`.

This is done transparently by the compiler.

Just like with untyped or generic functions, where the usage of the argument determines the `interface contract`, the `interface contract` of `givers` in the above example, is determined by the intersection of the collective usage of the list elements. Therefore the compiler traces all usage of `givers` elements making sure they all have a common shared implementation.

In the example above, both `StringGiver` and `IntGiver` define a `gift` method which they implement from `Giver`. So `givers` has type `List[dyn gift.1]`. Notice that we didn't say `List[dyn Givers]` since they share a parent type, `Givers`. That is because the information is not useful as all objects share a common parent `Any` (not a finalised name).

So the following is valid in Raccoon because all object share a root parent type. The type of this is `List[dyn void]`

```py
ls = [5, "Hello"]
```

The caveat however is that, operations like the one below, that you would expect to work won't compile. The compiler cannot determine at compile-time the type of an element at particular index at compile-time, so it does an exhaustive check to make sure the `__plus__` method can be used with `int` and `str` in any argument position.

```py
double = ls[0] + ls[0] # Error type of ls[0] can either be str or int and there is no __plus__(int, str) or __plus__(str, int)
```

## Intersection Types and Type Safety

Raccoon handles type safety differently. When a function can return multiple types at runtime. Raccoon returns an intersection of both types.

```py
def unsafe():
    if cond():
        return StringGiver().gift()
    else:
        return IntGiver().gift()

t = unsafe()
```

`unsafe` as used above has the instantiation `def unsafe() -> int & str`.

`int & str` is a C-like union type. This is purportedly optimizable by LLVM.

Intersection types are similar to `impl X` interfaces, except that they can only be resolved at runtime and they are only used with function return types. In other places, we use dynamic dispatch.

```py
x: int & str = get_int_or_str()
double = x + x
```

### ref vs val

By default, primitive types are passed around by value.

```py
salary = 4500 # salary statically refers to a location on the stack.
new_salary = salary # value 5 of salary is copied.
foo(salary) # value 5 of salary is copied.
```

By default, complex types are passed around by reference.

```py
john = Person(name="John", age=55)  # john also statically refers to a location on the stack.
same_person = john # however instead of copying the value of John, a reference (or a pointer) to the value is created.
foo(john) # same applies here.
```

You can change that behavior by using `ref` and `val` respectively.

### Heap Allocation

By default, objects are allocated on the stack.

```py
salary = 4500 # Allocated on the stack
john = Person(name="John", age=55) # Allocated on the stack
```

To allocate on the heap, we need the `new` keyword which uses the default allocator.

```py
salary = new 4500 # Allocated on the heap. Represents a pointer to such allocation.
john = new Person(name="John", age=55) # Allocated on the heap. Represents a pointer to such allocation.
```

Where do you use `new`? Use heap allocated object when:
- the object has a very large shape that could easily exhaust the stack.
- you cannot statically determine the shape of object at compile-time. A flexible linked list implementation for example.

## Sync and Send

The concept of `Send` and `Sync` is borrowed from Rust.

Heap-allocated objects are not `Sync` by default. 

Most types are `Send` unless they specify that they are `!Send` by implementing `!Send`, a special compiler abstract class.

When sharing ownership of objects across threads use the `new` keyword switches its underlying implementation from `Box[T]` to either `Arc[T]` or `Arc[Mutex[T]]`, depending on the context.

The contexts are well-defined, but that has to be in another write-up.

`Arc[Mutex[T]]` makes `!Sync` object `Sync` but it does not make `!Send` objects `Send`.

```py
box_total = new 4600 # `new` is `Box[T]`
arc_total = new 4500 # `new` is `Arc[Mutex[int]]` 
Thread.spawn(
    lambda:
        arc_total = 4300 # captured by lambda.
)
```

Here, `Thread.spawn` instantiation contains a lambda that captures its environment, making it a closures. 

`Thread.spawn` can require the its lambdas to be `Send`. It should look roughly like this.

```py
class Thread:
    # ...
    @where(F: Send & def() -> void)
    def spawn(f: F):
        # ...
```

## Function Abstract Classes

Each function and closure instantiation has a unique concrete type. But they all implement abstract classes based on the instantiation signature.

For example, the following two function instantiations implement the same abstract class. `impl def(str, int) -> str`.

```py
s = foo("hello", 2) # returns str
s = bar("bar", 400) # returns str
```

Just like regular abstract classes, we don't specify the `impl` part of the signature when writing the signature out.

```py
async def timeout(seconds: int, cb: def() -> void):
    await sleep(seconds)
    cb()
```

Note the `def` part in the signature. This lets us prevent the ambiguous signature `cb: ()` which can be mistaken for a tuple.

## Closures and Captures

Closures are funtions until they capture their environment. Closures that capture their environments have a different signature.

They are essentially a class with an associated function.

```py
@where(F: def(T) -> U)
def map[T, U, F](arr: [T], f: F) -> [U]:
    # ...

arr = map([1, 2, 3], lambda i: i + 1)

lis = map([1, 2, 3], lambda i: sum(arr) + i)
```

In the example above, the first lambda implements `impl def(int) -> int`.

The second one captures a variable from a parent scope, so it implements `impl Closure[[int], impl def([int], int) -> int]`.

A concrete type is contructed for it like this:

```py
@where(A: [int], C: Closure[A, def(A, int) -> int])
class UniqueClosure[C]:
    def __init__(self, capture: A, fn: F):
        self.capture = capture
        self.fn = fn

    def __call__(self, i):
        self.fn(self.capture, i)
```

Which then desugars to:

```py
lis = map([1, 2, 3], UniqueClosure(arr, lambda capture, i: sum(capture) + i))
```

This idea of desugaring to concrete types is also explored with coroutines and async/await.

## Async / Await

Should have similar semantics as coroutines in the language but instead of yielding to the user, it yields to the executor.

The standard library should provide a nice default multithreaded task scheduler just like it does with heap allocator.

Reference Rust's future implementation and Tokio's scheduler implementation.
