<div align="center">
    <a href="#" target="_blank">
        <img src="https://image.flaticon.com/icons/svg/2253/2253609.svg" alt="Raccoon Logo" width="140" height="140"></img>
    </a>
</div>

<h1 align="center">RACCOON</h1>

### INTRODUCTION
Raccoon is a language with Python 3.x syntax that is amenable to static analysis. The repository both defines the spec of the language and contains a reference implementation of the compiler.

**Raccoon will not maintain complete syntactic and semantic compatibility with Python**. Several dynamic elements known of Python are not available in Raccoon. For example, Raccoon doesn't have runtime module modification.

### SETTING UP THE PROJECT
##### REQUIREMENTS
- [Python 3.8+](https://www.python.org/downloads/) - Python interpreter
- [Pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv) - Python package manager
- [LLVM 8.x](https://github.com/llvm/llvm-project/releases/tag/llvmorg-8.0.1) - LLVM library
    <details>
    <summary>Read more</summary>

    #### WINDOWS

    _TODO_

    #### MAC OS

    Install LLVM with [brew](https://brew.sh/)

    ```
    brew install llvm@8
    ```

    #### DEBIAN

    Install LLVM 8

    ```
    apt-get install llvm-8
    ```

    ------

    You can also get the binaries of the various platform [here](https://github.com/llvm/llvm-project/releases/tag/llvmorg-8.0.1)
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

- Currently only compilation to AST is supported.
    ```sh
    cli/raccoon samples/test.ra --ast
    ```

### TESTING
##### REQUIREMENTS
- Same as [setting up the project](#setting-up-the-project)

##### STEPS
- You can run all the tests in a single command.
    ```bash
    pipenv run pytest
    ```

### USAGE
- Show help info
    ```sh
    cli/raccoon --help
    ```

- Compile and execute a Raccoon source file [WIP]
    ```sh
    cli/raccoon samples/test.ra
    ```

### LANGUAGE DESIGN
Raccoon is similar to Python in a lot of ways, but being a statically-typed language, it made some trade-offs to ensure predictable performance. In this respect, Raccoon is not always compatible with Python.

Raccoon's type system is also similar to Python's although it is a bit more fleshed out. While Raccoon prioritizes a design that benefits static analysis, it still allows Python's level of flexibility where statically determinable. This is why type inference and structural typing are an important part of Raccoon.

For more details, check [NOTES.md](NOTES.md)

### LICENSE
[Apache License 2.0](LICENSE)

Attributions can be found [here](ATTRIBUTIONS.md)



<sup><sup><sub><sub>[Raccoon](#README.md) is to [Python](https://github.com/python/cpython) what [Crystal](https://github.com/crystal-lang/crystal) is to [Ruby](https://github.com/ruby/ruby)<sub></sub></sup></sup>
