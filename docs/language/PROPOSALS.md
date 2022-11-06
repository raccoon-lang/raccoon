## POSSIBLE ADDITIONS

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

  Raccoon's types are not erased, so they are available at runtime.

  ```py
  # Type anotation
  index: int = 9

  # Type argument
  nums: list[int] = []

  # Optional type
  age: int? = 45

  # Result type
  age: int! = get_age()

  # Function type
  fn: def (int, int) -> int = sum

  # Tuple type
  value: (int, int) = (1, 2, 3)
  value: (int, *str) = (1, "hello", "world")

  # Intersection type
  identity: int & str = "XNY7V40"

  # Type comparison
  Dog < Pet
  Pet > Dog
  Dog == Dog

  # Generics
  @impl(Sequence).where(N: int)
  enum class TinyList[T, const N]:
      Inline([T, N])
      Heap([T])
  ```

  You can omit the type of a function

  ```py
  def foo(x):
      x + 1

  y = foo(1)
  ```

  But when you specify the argument types, you must also specify the return type

  ```py
  def foo(x: int) -> int:
      x + 1

  y = foo(1)
  ```

- More operators [In Progress]

  ```py
  @where(T: Number)
  class Num[T]:
      def init(self, value: T):
          self.value = value

      def plus(self, other):
          Num(self.value + other.value)

      def sqrt(self):
          Num(√(self.value))

      def square(self):
          Num(self.value²)

  a, b = Num(2), Num(3)

  sum = a + b
  rooted = √a
  squared = a²
  ```

- Macro metaprogramming [In Progress]

  Raccoon's decorators are macros and they are unhygenic.

  ```py
  @macro
  def test(attr: TokenStream[Attr]) -> AST:
      # ...
      pass

  @macro
  def test(block: Tree[Block]) -> AST:
      # ...
      pass

  @macro
  def test(attr: TokenStream[Attr], block: TokenStream[Block]) -> AST:
      # ...
      pass

  @macro
  def test(attr: TokenStream[Attr], fn: Tree[Fn]) -> AST:
      Fn {
          name,
          generics,
          args,
          return_type,
          where_clause,
          body
      } = tree.value

      @quote:
          def @(name) @(generics) ( @(args) ) -> @(return_type) @(where_clause):
              print(f"running {fn_name}")
              @(body.statements)
  ```

  There are multiple ways of using a macro depending on the type of the argument.

  ```py
  @test("Hello world!")

  @test:
      print("Hello world!")

  @test(first):
      print("Hello world!")

  @test(info)
  def foo():
      print("Hello world!")
  ```

  You can also chain macros

  ```py
  @base(Pet).impl(Debug)
  pub data class Dog(name: str, age: int):
      def debug(self, fmt):
          fmt.debug_class("Dog")
              .field("name", self.name)
              .field("age", self.age)
              .finish()
  ```

- Function declaration syntax

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

  Regex literal with `/.../` syntax is notoriously hard to lex.
  In Racoon's case we need to make sure no expression-type token comes before it.
  Although this makes the lexer more complicated.

- The no_wrap macro

  You can define your enum so that a particular variant does not need to be wrapped to be passed as a value to the enum.
  This only works for variants with a single field and can only be applied to one variant under an enum.
  This is how the `Option` and `Result` are defined.

  ```py
  pub enum class Option[T]:
      @no_wrap
      Some(T)
      None
  ```

  So we don't have to wrap `result` in `Some` here

  ```py
  def get_age(self) -> Result[u8]:
      result = self.some_calc()
      if result < 0:
          raise Error("Age cannot be negative")
      else:
          result
  ```

  The same applies here

  ```py
  mut age: Option[u8] = 0
  ```

- `?` operator [In Progress]

  ```py
  def get_surname(p: Person) -> Option[str]: # Also def get_surname(p: Person) -> str?
      (_, _, lastname) = p.get_names()?
      lastname
  ```

- `!` operator [In Progress]

  ```py
  def fetch_peer_addr(net: Network, id: [u8; 16]) -> Result[str]: # Also def fetch_peer_addr(net: Network, id: [u8; 16]) -> str!
      Peer { addr, .. } = net.fetch_peer(id)!
      addr
  ```

- List and Array type annotation

  Dynamic list

  ```py
  nums: List[int] = [1, 2, 3, 4] # or
  nums: [int] = [1, 2, 3, 4]
  ```

  Sized array

  ```py
  nums: Array[int, 4] = [1, 2, 3, 4] # or
  nums: [int, 4] = [1, 2, 3, 4]
  ```

  Unsized array

  ```py
  nums: Array[u8, *] = alloc.allocate_zeroed(Layout(10, 8)!)! # or
  nums: [u8, *] = alloc.allocate_zeroed(Layout(10, 8)!)!
  ```

- Additional reserved keywords

  ```py
  Self, union, enum, dyn, new, abstract, data, const, ref, ptr, val, match, let, mut, var, interface, where, macro, type, pub
  ```

- UFCS

  ```py
  ls = [1, 2, 3, 4]
  len(ls)
  ls.len()
  ```

- `mut` keyword

  Raccoon variables are immutable by default unless explicitly made mutable with the `mut` keyword.

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

  Named tuple is still position-based when unpacking

  ```py
  (name, age) = named_tup
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
      case NormalClass { field1, .. }: field1
      case DataClass(field1, _): field1
      case [x, 5 as y, z]: y # List
      case (x, 5 as y, 10, *z): x # Tuple
      case (x, 5 as y, 10, **z): x # NamedTuple
      case { "x", "y" as y,  *z}: x # Set
      case { "x", "y" as y, **z}: x # Dict
      case 10 | 11 as x: x
      case 0..89: 10
      case other: other
      case _: 11
  ```

- `if-let` statement

  ```py
  if let Person { name, age } = x:
      print(name)
  else:
      print("Not a person")
  ```

- `let-else` statement

  ```py
  let Person { name, age } = x else:
      raise Error("Not a person")

  print(name)
  ```

- Partial application

  ```py
  add2 = add(2, _)
  add10 = add(_, 10)
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
      @no_wrap
      Some(value: T)
      None

  identity: Option[str] = Option.None

  match identity:
      case Some(value): value
      case err: err
  ```

- Updated abstract class syntax

  Abstract classes can't have `init` contructors.

  ```py
  abstract class Observable:
      subscriptions: [Subscription]

      def notify()
      def add_subscription(sub: Subcription)
  ```

- Update enum syntax

  ```py
  enum class Data:
      Inline([u8])
      External { addr: str, port: u16 }
  ```

- Wrapped string and byte literals

  Unlike Rust, string and byte literals are not `strarray` and `[u8, *]` respectively.
  The literals are wrapped in their `str` and `[u8]` types.

  ```py
  name = "James" # str
  data = b"Hello" # [u8]
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

- No magic method syntax

  ```py
  class Person:
      def init(self, name, age):
          self.name = name
          self.age = age
  ```

- Module items can be exported only when explicitly stated

  ```py
  pub data class Person(pub name, pub age)
  ```

  ```py
  pub(gaze) data class Person(name, age)
  ```

- No static field. Only instance field definition

  ```py
  pub class Person:
      pub name: str
      pub age: int
  ```
