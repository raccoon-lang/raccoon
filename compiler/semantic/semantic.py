"""
TODO:
    - Move the different visitors into their respective folders.
    - Module documentation.
"""
import json
from copy import deepcopy
from collections import namedtuple
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
from compiler.semantic.visitors import (
    AssignmentVisitor,
    FunctionVisitor
)
from utils import json_dumps


class SemanticAnalyzer:
    """
    Analyzes the semantics of the program's AST.

    It calls two important visitors which do the bulk of the work.

    - TokenExtractionVisitor

    - SemanticVisitor
    """

    def __init__(self, ast, tokens, compiler_opts=CompilerOptions()):
        self.ast = ast
        self.tokens = tokens
        self.compiler_opts = compiler_opts

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
                f"{json_dumps(relevant_tokens)}\n"
            )

        state = SemanticVisitor(self.ast, relevant_tokens, self.compiler_opts).start_visit()

        return state


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
    symbols = [
        { # scope 0
            "typed": {
                "var": SymbolInfo(
                    ast_ref=()
                ),
                "func": SymbolInfo(
                    ast_ref=(),
                )
            },
            "untyped": {
                "ls": SymbolInfo(
                    ast_ref=(),
                    list_type_indices=[]
                ),
            }
        },
    ]

    imports is map of elements imported from other modules.
    imports = {
        "name": (path="module.com", alias=True),
    }
    """

    def __init__(self, tokens, compiler_opts=CompilerOptions()):
        self.tokens = tokens
        self.current_scope_level = 0
        self.current_path = ""
        self.symbols = []
        self.inheritance_lists = []
        self.imports = {}
        self.compiler_opts = compiler_opts

    def add_scope(self, scope):
        self.current_scope_level += 1
        self.symbols.append(scope)

    def __repr__(self):
        fields = deepcopy(vars(self))
        fields['kind'] = type(self).__name__
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"

class SemanticVisitor(Visitor):
    """
    This visitor class walks a Raccoon's AST, gathers important information about the program and
    checks for some semantic validity.

    Making it do a lot in a single pass is an intentional design for preformance.
    """

    def __init__(self, ast, tokens, compiler_opts=CompilerOptions()):
        """
        """
        self.ast = ast
        self.state = SemanticState(tokens, compiler_opts)

    def start_visit(self):
        self.ast.accept(self)
        return self.state

    def act(self, top_level):
        """
        Called by the visitable.
        """
        type_ = type(top_level)

        # We are concerned with top-level stuff.
        if type_ == Function:
            FunctionVisitor(top_level, self.state).start_visit()

        else:
            pass

        return False
