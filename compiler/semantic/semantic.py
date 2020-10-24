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
from .info import SemanticInfo
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

        info = SemanticVisitor(self.ast, relevant_tokens, self.compiler_opts).start_visit()

        return info


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

    def act(self, ast):
        """
        Called by the visitable.
        """

        ty = type(ast)

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

        if ty in base_types:
            index = ast.index
            self.relevant_tokens[index] = deepcopy(self.tokens[index])

        elif ty == Operator:
            first_idx = ast.op
            self.relevant_tokens[first_idx] = deepcopy(self.tokens[first_idx])

            if (second_idx := ast.rem_op) is not None:
                self.relevant_tokens[second_idx] = deepcopy(self.tokens[second_idx])

        return True


class SemanticVisitor(Visitor):
    """
    This visitor class walks a Raccoon's AST, gathers important information about the program and
    checks for some semantic validity.

    Making it do a lot in a single pass is an intentional design for preformance.
    """

    def __init__(self, ast, tokens, compiler_opts=CompilerOptions()):
        """
        """
        self.program = ast
        self.info = SemanticInfo(tokens, compiler_opts)

    def start_visit(self):
        self.program.accept(self)
        return self.info

    def act(self, ast):
        """
        """

        # Iterate through all statements in the program
        for ast in self.program.statements:
            ty = type(ast)

            if ty == Function:
                FunctionVisitor(self.info, ast).start_visit()
            else:
                pass

        return False
