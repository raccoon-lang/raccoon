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

    T is a type that implements `__plus__` method that takes 2 arguments 

- `(a: any T.0, b: any T.1)` reads as:

    a is a ref/val of some type T that implements a method `__plus__` where a is the first argument.
    
    b is a ref/val of some type T that implements a method `__plus__` where b is the second argument.

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
        a: any T.0 where [                    // a is something that implements T at pos 0 
            T returns any U.0 where [         // T returns something that implements U at pos 0
                U returns any V.0 where [     // U returns something that implements V at pos 0
                    V returns any W.0 where [ // V returns something that implements W at pos 0
                        W returns any X       // W returns X
                    ]
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
        V: impl __next__.1
    ](
        a: any T.0 where [            // a is something that implements T at pos 0 
            T returns any U.0 where [ // T returns something that implements U at pos 0
                U returns any V.0     // U returns something that implements V at pos 0
            ]
        ]
    )

`iterate_gift` as used above has the instantiation `iterate_gift(void) -> str`. `void` because `StringGiver` has no field, so no space is allocated for it.

As mentioned before, what you do with the arguments of an untyped function determines the `interface contract` and the kind of monormorphisation allowed.

## Common Fields

We have seen above that the methods you use with an argument determine the interface contract of an untyped function. This is also true for the fields of an argument.

```py
def who_am_i(something):
    print(f"I am {something.name}")
```

`who_am_i` will only work for arguments that have a name method. The interface contract of `who_am_i` looks like this:


    [ 
        T: impl [name],
        U: impl __str__.1, 
        V: str,
    ](
        a: any T where [        // a is something that implements T (a field) 
            T: any U.0 where [  // T is something that implements U at pos 0
                U returns V     // U returns V
            ]
        ]
    )

Notice the `impl [name]` syntax. It used to refer to a field. `impl func.x` is used for methods.

Also notice that we use `T: any U.0` syntax for fields just like arguments because they are values that must also conform to some implementation.

## Generics

Generics are useful for restricting an interface contract further because it allows certain conditional semantics that a developer may desire.

```py
@where(T: < Seq, U: < Seq) # Reads as where T is a subtype of Seq. Speculative syntax and type.
def any_common_elements(l: T, r: U) -> bool:
    for (a, b) in zip(a, b):
        if a == b:
            return true

    return false

any_common_elements([1, 2, 3], {4, 5, 3}) # true
```

## Intersection Types and Type Safety

Raccoon handles type safety differently. For example, when a function can return multiple types at runtime, Raccoon returns an intersection of both types.

```py
def unsafe():
    if cond():
        return StringGiver().gift()
    else:
        return IntGiver().gift()

t = unsafe()
```

`unsafe` as used above has the instantiation `def unsafe() -> int & str`.

`int & str` is implemented as a [tagged union](https://en.wikipedia.org/wiki/Tagged_union). On the other hand `dyn` objects are implemented as `[tag, ..fields]`in memory.

`int` and `str` are variants of `int & str`.

Intersection types are similar to `dyn AbstractClass`, except that they are used in places where the compiler can easily determine number of types like enum variants, unsafe return types, etc. 

```py
x: int & str = get_int_or_str()
double = x + x
```

In places where there can be potentially many types, we use dynamic dispatch. This is true for container types.

## Union Classes 

Union classes are analogous to C union types. Their memory layout is determined by their largest field.

```py
union class JSNumber:
    int: i64
    float: f64

JSNumber.float = 2.0
print('0x{0:x}'.format(JSNumber.int)) # 0x4000000000000000
```

## Enum Classes

Enum classes are intersection types and their variants normal classes.

```py
enum class PrimaryColor:
    Red(t: byte)
    Green(t: byte)
    Blue(t: byte)

    def to_byte(self): 
        return self.t # Okay because the variants all have common field type
```

The example above can be desugared into the following:

```py
abstract class AbstractPrimaryColor:
    pass

@implements(AbstractPrimaryColor)
data class Red(t: byte):
    pass
        
@implements(AbstractPrimaryColor)
data class Green(t: byte):
    pass
        
@implements(AbstractPrimaryColor)
data class Blue(t: byte):
    pass

typealias PrimaryColor = Red & Green & Blue

def to_byte(variant: PrimaryColor): # This function is monomorphisable.
    return variant.t
```

The only thing we didn't capture here is the `PrimaryColor.Variant` namespace.

In the examples above, notice that the enum's variants share a single method `to_byte` that apply to all variants. We could have also used match, which through exhaustion allows monomorphisation.

```py
def to_byte(variant: PrimaryColor): # This function will be monomorphised.
    return variant.t
    
def to_byte(variant: PrimaryColor): # This function can also be monomorphised.
    match variant:
       Red(t): return t
       Blue(t): return t
       Green(t): return t
```

Because enum variants are regular classes, we can have specialized method for them.

```py
def red_to_byte(color: PrimaryColor.Red): # This is a specialised function.
    return color.t
```

Methods and fields accessed on an intersection type must apply to all the variants.

```py
enum class Optional[T]:
    Some(t: T)
    None

    def unwrap(self): 
        return self.t # Error because None a variant of Optional[T] does not have a `t` field.
```

https://rust-lang.github.io/unsafe-code-guidelines/layout/enums.html

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

So the following is valid in Raccoon because all object share a root parent type. The type of this is `List[dyn _]` because it is not yet clear what functions the element use, which determines their `impl`.

```py
ls = [5, "Hello"]
```

The caveat however is that, operations like the one below, that you would expect to work won't compile. The compiler cannot determine at compile-time the type of an element at particular index at compile-time, so it does an exhaustive check to make sure the `__plus__` method can be used with `int` and `str` in any argument position.

```py
double = ls[0] + ls[0] # Error type of ls[0] can either be str or int and there is no __plus__(int, str) or __plus__(str, int)
```

##

You may wonder how the compiler resolves the type of `mixed` variable in the following example to a dynamically dispatched type.

```py
class Vec[T]:
    def __init__(self, capacity: int):
        self.length = 0
        self.capacity = capacity
        self.buffer = Buffer[T](capacity) 

    def append(self, item: T):
        if self.length >= capacity:
            self.resize()
        self.buffer.alloc(self.length + 1, item)
        self.length += 1
    
    # ...

mixed = Vec() # T resolves to `[ dyn __str__.0, ... ]`
mixed.append(1) # T is int here
mixed.append("Hello") # T is str here

print(mixed[0]) # Final resolution is based on this shared method.
```

The reason this works is because Buffer implements `dyn _`.

```py
# Buffer implementation for dynamic types. 
# `_` means the final type is decided by the total usage of the field.
@where(T: dyn _) 
class Buffer[T]:
    def alloc(self, position: int, item: T):
        # ...

# Buffer implementation for other types with known compile-time shape. 
# Concrete types instantiated from __impl__ and intersection types.
class Buffer[T]: 
    def alloc(self, position: int, item: T):
        # ...
```

`Buffer[T]` gets its final type from `Vec[T]`. And since Buffer allows a `T: dyn _`, the usage of the instance method `Vec.append.T` with different types `int` and `str` made it resolve into a `dyn _`. 

Any method argument that holds a value of such `T` will then be given a reference/pointer to the tagged value which will be stored on the heap. Which is the case for `append`'s `item` parameter. Raccoon does not support `dyn _` fields or variables.

Another thing worth noting is that even though the compiler resolves a `dyn _` to a dyn of field and method implementations (e.g. `[dyn __str__.0]`), the compiler does not forget (erase) the actual types in subsequent resolutions.

```py
values = [1, "Hello"] # [ dyn deep_copy.0, ... ]

# ...

def copy_first(ls): 
    return ls[0].deep_copy()

# copy_first can return int or str.
# new_copy has type `int & str`.
new_copy = copy_first(values) # def copy_first(dyn _) -> int & str 
```

This works because at the instantiation of `copy_first(values)`, the compiler still remembers the types behind `values: dyn _`. So it is able to check the return types of all the methods of `int & str`.

## Type Casting

Most times the compiler won't be able to determine the type of variant or `dyn` object at compile-time. So it is useful to have type casting functions.

```py
ls = [5, "Hello"]

int_value = cast[Int](ls[0])
str_value = cast[Int](ls[1-1]) # Raises an error because type cannot be casted.
```

```py
variant = get_color()
red = cast[PrimaryColor.Red](variant) # Raises an error if type cannot be casted.
```


## ref vs val

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

## Heap Allocation

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
class UniqueClosure[A, C]:
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
