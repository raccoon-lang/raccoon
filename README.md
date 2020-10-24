<div align="center">
    <a href="#" target="_blank">
        <img src="https://image.flaticon.com/icons/svg/2253/2253609.svg" alt="Raccoon Logo" width="140" height="140"></img>
    </a>
</div>

<h1 align="center">RACCOON</h1>

:warning: This project is experimental and in active development :warning:

### INTRODUCTION
Raccoon is a language with Python 3.x syntax that is amenable to static analysis. The repository both defines the spec of the language and contains a reference implementation of the compiler.

**Raccoon will not maintain full syntactic and semantic compatibility with Python**. Several dynamic elements known of Python are not available in Raccoon. While Raccoon prioritizes a design that benefits static analysis, it still allows Python's level of flexibility where statically determinable.

Below is an example of what Raccoon looks like:

```py
class Person:
    """
    Class for creating details about a person.
    """

    population = 0

    def __init__(self, name, age, gender="Male"):
        self.name = name
        self.age = age
        self.gender = gender
        Person.population += 1

    def __del__(self):
        """
        Decrement population
        """
        Person.population -= 1

    def __str__(self):
        """
        Create a string representation of object
        """
        return f"Person(name={self.name}, age={self.age}, gender={self.gender})"


jane = Person("Jane Doe", "Female", 23)
print("Jane >", jane)
```

You can check [samples folder](#samples) for more examples.

### SETTING UP THE PROJECT
##### REQUIREMENTS
- [Python 3.8+](https://www.python.org/downloads/) - Python interpreter
- [Pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv) - Python package manager
- [LLVM 8.x](https://github.com/llvm/llvm-project/releases/tag/llvmorg-8.0.1) - LLVM library
    <details>
    <summary>Read more</summary>
    <p>

    # macOS

    Install LLVM with [brew](https://brew.sh/)

    ```
    brew install llvm@8
    ```


    # Debian

    Install LLVM 8

    ```
    apt-get install llvm-8
    ```


    # Windows

    ...

    ------

    You can also get the binaries for various platforms [here](https://github.com/llvm/llvm-project/releases/tag/llvmorg-8.0.1)
    </p>
    </details>

- [Binaryen](https://github.com/WebAssembly/binaryen) - Binaryen is needed to generate
    <details>
    <summary>Read more</summary>
    <p>
    You need to build binaryen as a dynamic library by following <a src="https://github.com/WebAssembly/binaryen#building">the instructions on the repo</a>.

    Make sure generated dynamic library is accessible system-wide. You can save it under `/usr/local/lib`.
    </p>
    </details>

##### STEPS
- Clone project
    ```sh
    git clone https://www.github.com/appcypher/raccoon.git
    ```

- Move to project's directory
    ```sh
    cd raccoon
    ```

- Install dependencies

    ```sh
    pipenv install
    ```

- Currently the compiler can only generate tokens and AST from source files.

    ```sh
    cli/raccoon samples/test.ra --tokens
    ```

    ```sh
    cli/raccoon samples/test.ra --ast
    ```

### LICENSE
[Apache License 2.0](LICENSE)

Attributions can be found [here](ATTRIBUTIONS.md)



<sup><sup><sub><sub>[Raccoon](#README.md) is to [Python](https://github.com/python/cpython) what [Crystal](https://github.com/crystal-lang/crystal) is to [Ruby](https://github.com/ruby/ruby)<sub></sub></sup></sup>
