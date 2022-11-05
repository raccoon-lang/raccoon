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

- Multiline lambda expression

  ```py
  map(
      def (x):
          if x == 1:
              0
          else:
              5
      , array
  )

  map(
      (
          def (x):
              if x == 1:
                  0
              else:
                  5
      ),
      array
  )

  map(def (x):
      if x == 1:
          0
      else:
          5
  , array)

  map((
      def (x):
          if x == 1:
              0
          else:
              5
  ), array)
  ```

- Implicit returns

  ```py
  def foo(x):
      if x == 1:
          0
      else:
          5

  assert foo(1) == 0
  assert foo(2) == 5
  ```

- Updated type annotation & generics [In Progress]

  ```py
  # Type anotation
  index: int = 9

  """
  ERROR

  index: int  # variable needs to be initialized.
  """

  # Type argument
  nums: list[int] = []

  # Optional type (Undecided)
  age: int? = 45

  # Function type
  fn: def (int, int) -> int = sum

  # Tuple type
  value: (int, int) = (1, 2, 3)
  value: (int, *str) = (1, "hello", "world")

  # Intersection type
  identity: int & str = 'XNY7V40'

  # Type relationship
  Person < Mammal
  Mammal > Person
  Person == Person

  # Generics
  @where(N: ToStr, A: ToInt)
  class Person[N, A](Mammal):
      def init(self, name: N, age: A):
          self.name = name.to_str()
          self.age = age.to_int()

  jane = Person.[str, int]('Jane Doe', 45)

  class StaticArray[const N, T]:
      def init(self):
          self.buffer = Buffer[N, T]()
  ```

- More operators [In Progress]

  ```py
  class Num:
      @where(T: Integral)
      def init(self, value: T):
          self.value = value

      def plus(self, other):
          Num(self.value + other.value)

      def sqrt(self):
          Num(√(self.val))

      def sq(self):
          Num(self.val²)

  a, b = Num(2), Num(3)

  sum = a + b
  rooted = √a
  squared = a²
  ```

- Progressive Linting

  - Structural polymorphism can be made an error or warning

    ```py
    def foo(x): # error or warning
        x + x

    foo(1)
    foo("hello")
    ```

  - Non-zero-cost abstraction can be made an error or warning

    ```py
    def get_name(x):
        x.name # error or warning
    ```

    ```py
    data class Node(parent: Node?, children: [Node])  # error or warning
    ```

    ```py
    class Engine:
        def init(self):
            self.context = Context()
            self.module = Module(self.context) # error or warning
    ```

- Macro metaprogramming [In Progress]

  Raccoon's decorators are macros.

  ```py
  @test("Hello world!")

  @test "Hello world!"

  @test:
      print("Hello world!")

  @test(info)
  def foo():
      print("Hello world!")

  @macro
  def test(string: StrLiteral):
      @quote:
          print("starting game")

  @macro
  def test(block: Block):
      statements = block.statements
      @quote:
          @(statements)

  @macro
  def test(fn: Function):
      Function(
          name,
          generics,
          args,
          return_type,
          where_clause,
          body
      ) = fn

      @quote:
          def @(name) @(generics) ( @(args) ) -> @(return_type) @(where_clause):
              print(f"running {fn_name}")
              @(body.statements)
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
  type IdentityFunc[T] = (T) -> T
  ```

- Character

  ```py
  ch0 = 'a'
  ch1 = '\n'
  ch2 = '\uff'
  ch3 = '\890'

  string = ch0 + ch1

  if 'a' <= ch <= 'z':
      print(ch)
  ```

- Regex literal [In Progress]

  ```js
  regex = /\d+/;
  ```

- `?` operator [In Progress]

  ```py
  def get_surname(p: Person) -> Option[str]: # Also def get_surname(p: Person) -> str?
      (_, _, lastname) = p.get_names()?
      return lastname
  ```

- `!` operator [In Progress]

```py
def fetch_peer_addr(net: Network, id: [u8; 16]) -> Result[str]: # Also def fetch_peer_addr(net: Network, id: [u8; 16]) -> str!
    Peer { addr, .. } = net.fetch_peer(id)!
    return addr
```

- Additional reserved keywords

  ```py
  Self, union, enum, dyn, new, abstract, data, const, ref, ptr, val, match, let, mut, var, interface, where, macro, type
  ```

- UFCS

  ```py
  ls = [1, 2, 3, 4]
  len(ls)
  ls.len()
  ```

- `mut` keyword

  Raccoon variables are immutable by default.

  ```py
  def map(array, f):
      mut t = []
      for i in array:
          t.append(f(i))
      return t
  ```

- New versions of certain functions and objects by default

  ```py
  map, sum, filter, sum, join

  map(array, def (x): x + 1)
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
      case (x, y = 5, 10, *z): x # Tuple
      case (x, y = 5, 10, **z): x # NamedTuple
      case { x = 'x', y = 'y',  *z}: x # Set
      case { x = 'x', y = 'y', **z}: x # Dict
      case 10 | 11: x
      case 0..89: 10
      case other: other
      case _: 11
  ```

- `if-match` statement

  ```py
  if match Person(name, age) = x:
      print(name)
  else:
      print("Not a person")
  ```

- `match-else` statement

  ```py
  match Person(name, age) = x else:
      raise Exception("Not a person")

  print(name)
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

  cast.[Cat](animals[0]).meow()
  ```

- Overloading functions and methods based on arity and types

  ```py
  def add(a: str, b: str):
      a + '_' + b

  def add(a: int, b: int):
      a + b

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

- Updated range and index range

  ```py
  ls = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  print(ls[1..3]) # [2, 3, 4]
  ```

  ```py
  for i in 1..10:
      print(i)
  ```

- Underscore means discarded value or unprovided value

  ```py
  for _ in 1..11:
      print("Hello")

  f = add(2, _)
  ```

- Updated enums (ADTs)

  ```py
  enum class Option[T]:
      Some(value: T)
      None

  identity: Option[str] = Option.None

  match identity:
      case Some(value): value
      case err: err
  ```

- Updated abstract class syntax

  ```py
  abstract class Observable:
      def init(self):
          self.subscriptions: [Subscription]

      abstract def notify()
      abstract def add_subscription(sub: Subcription)
  ```

- Updated data class syntax

  Maybe look for another keyword

  ```py
  data class Pet(name, age):
      def debug(self, f):
          f.debug_class("Pet")
              .field("name", self.name)
              .field("age", self.age)

  data class Person(name: str, age: int, bases=(Specie))
  data class Identity[T](id: T)

  john = Person("John", 50)
  id = Identity(504)
  ```

- No special magic method syntax

  ```py
  class Person:
      def init(self, name, age):
          self.name = name
          self.age = age
  ```
