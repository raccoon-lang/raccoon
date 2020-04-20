"""
TODO:
    - Move the different visitors into their respective folders.
    - Module documentation.
"""

from collections import namedtuple
from copy import deepcopy
from compiler.visitor import Visitor
from compiler.options import CompilerOptions
from compiler.semantic.declarations import (
    FunctionDeclVisitor
)
from compiler.parser.ast import (
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
)


class SemanticAnalyzer:
    """
    Analyzes the semantics of the program's AST.

    It calls three important visitors which do the bulk of the work.

    - TokenExtractionVisitor

    - MainSemanticVisitor

    - InstantiationVisitor
    """

    def __init__(self, ast, tokens, compiler_opts=CompilerOptions()):
        self.ast = ast
        self.tokens = tokens
        self.compiler_opts = compiler_opts

    def analyze(self):
        """
        Calls the different visitors that analyze the AST for semantic correctness and generates a
        lowered ast for codegen phase.
        """

        relevant_tokens = TokenExtractionVisitor(self.ast, self.tokens).start_visit()
        self.tokens = []  # Free old tokens

        if self.compiler_opts.verbose:
            print("============ relevant_tokens ============\n", relevant_tokens, "\n")

        semantic_values = MainSemanticVisitor(self.ast, relevant_tokens).start_visit()

        if self.compiler_opts.verbose:
            print("============ semantic_values ============\n", semantic_values, "\n")

        lowered_ast = InstantiationVisitor(self.ast, semantic_values).start_visit()

        if self.compiler_opts.verbose:
            print("============ lowered_ast ============\n", lowered_ast, "\n")

        return lowered_ast


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


class MainSemanticVisitor(Visitor):
    """
    This visitor class walks a Raccoon's AST, gathers important information about the program and
    checks for some semantic validity.

    Making it do a lot in a single pass is an intentional design for preformance.

    List of things the visitor does:

    - Creates a symbol table

    - Saves variable declarations

    - Saves function declarations
        - Checks for argument name conflict

    - Saves type declarations
        - Checks for inheritance cycle

    - Creates function frame
        - Unionizes variable types

    - Creates type frame
        - Resolves diamond problem

    - Declares function instances
        - Check argument positions and type restrictions

    - Declares type instances
        - Check recursive instantiation

    - Check elements in wrong context
        - Check for certain flow statements at top level

    - Tracks variable-object lifetimes
    """

    def __init__(self, ast, tokens):
        self.ast = ast
        self.tokens = tokens
        self.symbol_table = {}
        self.current_scope = ""
        self.function_frames = []
        self.type_frames = []
        self.function_instances = []
        self.type_instances = []

    def start_visit(self):
        self.ast.accept(self)
        SemanticValues = namedtuple(
            "SemanticValues",
            "function_frames type_frames function_instances type_instances",
        )
        return SemanticValues(
            self.function_frames,
            self.type_frames,
            self.function_instances,
            self.type_instances,
        )

    def act(self, visitable):
        """
        Called by the visitable.
        """
        type_ = type(visitable)

        if type_ == AssignmentStatement:
            pass

        elif type_ == Function:
            pass

        elif type_ == Class:
            pass

        return True


class InstantiationVisitor(Visitor):
    """
    This visitor class walks a Raccoon's AST, creates instantiations of functions and types
    and link modules together.

    List of things the visitor does:

    - Create function instantiations
        - Check methods exist on types

    - Create function impl frame for lib

    - Create type impl frame for lib

    - Create type instantiations

    - Link modules

    - Canonicalize literal
    """

    def __init__(self, ast, semantic_values):
        self.ast = ast
        self.function_frames = semantic_values.function_frames
        self.type_frames = semantic_values.type_frames
        self.function_instances = semantic_values.function_instances
        self.type_instances = semantic_values.type_instances

    def start_visit(self):
        self.ast.accept(self)
        return None

    def act(self, visitable):
        """
        Called by the visitable.
        """

        return True
