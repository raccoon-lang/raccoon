"""
TODO:
    - Move the different visitors into their respective folders.
    - Module documentation.
"""

from collections import namedtuple
from copy import deepcopy
from compiler import CompilerOptions, Visitor
from compiler.ast import (
    Null,
    Identifier,
    Integer,
    Float,
    ImagInteger,
    ImagFloat,
    String,
    ByteString,
    PrefixedString,
    Operator,
    AssignmentStatement,
    Function,
    Class,
    ImportStatement,
)
from compiler.errors.semantic import SemanticError
from compiler.semantic.visitors import FunctionVisitor


class SemanticAnalyzer:
    """
    Analyzes the semantics of the program's AST.

    It calls two important visitors which do the bulk of the work.

    - TokenExtractionVisitor

    - SemanticVisitor
    """

    def __init__(self, ast, tokens, codegen, compiler_opts=CompilerOptions()):
        self.ast = ast
        self.tokens = tokens
        self.compiler_opts = compiler_opts
        self.codegen = codegen

    def analyze(self):
        """
        Calls the different visitors that analyze the AST for semantic correctness and generates a
        an IR for codegen phase.
        """

        relevant_tokens = TokenExtractionVisitor(self.ast, self.tokens).start_visit()
        self.tokens = []  # Free old tokens

        if self.compiler_opts.verbose:
            print(
                f"============ relevant_tokens ============\n"
                f"length = {len(relevant_tokens)}\n\n"
                f"{relevant_tokens}\n"
            )

        semantic_state = SemanticVisitor(
            self.ast, relevant_tokens, self.codegen, self.compiler_opts
        ).start_visit()

        if self.compiler_opts.verbose:
            print(f"============ semantic_state ============\n\n{semantic_state}\n")

        return semantic_state


class TokenExtractionVisitor(Visitor):
    """
    This visitor class walks a Raccoon's AST, given a token list, extracts the tokens that are
    referenced by the AST.
    """

    def __init__(self, ast, tokens):
        self.ast = ast
        self.tokens = tokens
        self.relevant_tokens = {}

    def start_visit(self):
        self.ast.accept(self)
        self.tokens = None  # Free tokens
        return self.relevant_tokens

    def act(self, visitable):
        """
        Called by the visitable.
        """

        type_ = type(visitable)

        base_types = {
            Identifier,
            Integer,
            Float,
            ImagInteger,
            ImagFloat,
            String,
            ByteString,
            PrefixedString,
        }

        if type_ in base_types:
            index = visitable.index
            self.relevant_tokens[index] = deepcopy(self.tokens[index])

        elif type_ == Operator:
            first_idx = visitable.op
            self.relevant_tokens[first_idx] = deepcopy(self.tokens[first_idx])

            if (second_idx := visitable.rem_op) is not None:
                print(f">>> second_idx = {second_idx}")
                self.relevant_tokens[second_idx] = deepcopy(self.tokens[second_idx])

        return True


class SymbolInfo:
    """
    """

    def __init__(self):
        pass


class SemanticState:
    """
    symbol_table is a stack of scopes. Each scope is a table of symbols and their information.
    symbol_table = [
        { # scope 0
            "var": SymbolInfo(...),
            "func": SymbolInfo(...)
        },
        { # scope 1
            "var": SymbolInfo(...)
        }
    ]

    concrete_abis is a set of function and type abis.
    concrete_abis = {"14.1.1", "1.4.15"}

    imports is map of elements imported from other modules.
    imports = {
        "name": (path="module.com", alias=True),
    }
    """

    def __init__(self, tokens, codegen, compiler_opts=CompilerOptions()):
        self.tokens = tokens
        self.current_scope_level = 0
        self.current_path = ""
        self.symbol_table = []
        self.concrete_abis = set()
        self.imports = {}
        self.codegen = codegen
        self.compiler_opts = compiler_opts

    def __repr__(self):
        return (
            f'SemanticState(tokens=[...], current_scope_level={self.current_scope_level}'
            f", current_path={repr(self.current_path)}, symbol_table={self.symbol_table}"
            f", concrete_abis={self.concrete_abis}, codegen={self.codegen}"
            f", compiler_opts={self.compiler_opts})"
        )


class SemanticVisitor(Visitor):
    """
    This visitor class walks a Raccoon's AST, gathers important information about the program and
    checks for some semantic validity.

    Making it do a lot in a single pass is an intentional design for preformance.
    """

    def __init__(self, ast, tokens, codegen, compiler_opts=CompilerOptions()):
        """
        """
        self.ast = ast
        self.state = SemanticState(tokens, codegen, compiler_opts)

    def start_visit(self):
        self.ast.accept(self)
        return self.state

    def act(self, top_level):
        """
        Called by the visitable.
        """
        type_ = type(top_level)

        # We are concerned with top-level stuff.
        if type_ == AssignmentStatement:
            pass

        elif type_ == Function:
            data = FunctionVisitor(top_level, self.state).start_visit()

        elif type_ == Class:
            pass

        elif type_ == ImportStatement:
            pass

        else:
            pass

        return False
