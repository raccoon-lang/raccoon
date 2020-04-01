<div align="center">
    <a href="#" target="_blank">
        <img src="https://image.flaticon.com/icons/svg/296/296589.svg" alt="Corona Logo" width="140" height="140"></img>
    </a>
</div>


<h1 align="center">CORONA</h1>

### INTRODUCTION
Corona is a language with Python 3.x syntax that is amenable to static analysis. The repository both defines the spec of the language and contains a reference implementation of the compiler, which compiles a legal Corona code to WebAssembly.

**Corona will not maintain complete syntactic and semantic compatibility with Python**. Several dynamic elements known of Python are not available in Corona. For example, Corona doesn't have runtime module modification.

There are other similarly oriented projects, but they are all objectively different from Corona.

MicroPython is a well-optimized Python interpreter (with some JIT support) while Nuitka compiles Python to C. These two projects still allow dynamic aspects of Python, which means their performances may suffer from those parts.

Vyper (not to be mistaken for Corona) primarily targets Ethereum VM and not designed for general-purpose programming.

Also unlike Nim, Boo and Cobra, Corona tries to stick to Python syntax and semantics as much as possible and wherever it makes sense.

RPython is quite similar to this project, but the developers have [made it clear](https://rpython.readthedocs.io/en/latest/faq.html#do-i-have-to-rewrite-my-programs-in-rpython) that their goal is not to make RPython a standalone language.

### SETTING UP THE PROJECT
##### REQUIREMENTS
- [Python 3.7+](https://www.python.org/downloads/) - Python interpreter
- [Pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv) - Python package manager

##### STEPS
- Clone project
    ```sh
    git clone https://www.github.com/appcypher/corona.git
    ```

- Move to project's directory
    ```sh
    cd corona
    ```

- Install dependencies

    ```sh
    pipenv install
    ```

- Build the project [macOS and Linux]
    ```sh
    sh build.sh setup
    ```

- Compile and run sample corona code [WIP]
    ```sh
    corona samples/class.vi
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
    corona --help
    ```

- Compile and execute a Corona source file [WIP]
    ```sh
    corona samples/class.vi
    ```

### LANGUAGE DESIGN
Corona is similar to Python in a lot of ways, but being a statically-typed language, it made some trade-offs to ensure predictable performance. In this respect, Corona is not always compatible with Python.

Corona's type system is also similar to Python's although it is a bit more fleshed out. While Corona prioritizes a design that benefits static analysis, it still allows Python's level of flexibility where statically determinable. This is why type inference and structural typing are an important part of Corona.

For more details, check [NOTES.md](NOTES.md)

### LICENSE
[Apache License 2.0](LICENSE)

Attributions can be found [here](ATTRIBUTIONS.md)



<sup><sup><sub><sub>[Corona](#README.md) is to [Python](https://github.com/python/cpython) what [Crystal](https://github.com/crystal-lang/crystal) is to [Ruby](https://github.com/ruby/ruby)<sub></sub></sup></sup>
