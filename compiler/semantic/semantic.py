"""
TODO:
    - Move the different visitors into their respective folders.
    - Module documentation.
"""

from copy import deepcopy
from compiler.parser.ast import (
    Identifier,
    Integer,
    Float,
    ImagInteger,
    ImagFloat,
    String,
    ByteString,
    PrefixedString,
    Operator,
)


class SemanticAnalyzer:
    """
    Analyzes the semantics of the program's AST.

    It calls three important visitors which do the bulk of the work.

    - TokenExtractionVisitor
    - MainSemanticVisitor
    - InstantiationVisitor
    """

    def __init__(self, parser, ast):
        self.parser = parser
        self.ast = ast

    def analyze(self):
        """
        TODO: documentation
        """

        tokens_visitor = TokenExtractionVisitor(self.parser, self.ast)
        tokens_visitor.start_visit()

        print("::: ast ::: \n", self.ast, '\n')
        print("::: saved tokens :::\n", tokens_visitor.tokens, '\n')
        print("::: reset parser :::\n", tokens_visitor.parser, '\n')

        main_visitor = MainSemanticVisitor(self.ast)
        main_visitor.start_visit()


class TokenExtractionVisitor:
    """
    This visitor class walks a Raccoon's AST, given a token list, extracts the tokens that are
    referenced by the AST and frees parser resources.

    List of what the visitor does:

    - Get tokens referenced by AST

    - Resets parser
    """

    def __init__(self, parser, ast):
        self.parser = parser
        self.ast = ast
        self.tokens = {}

    def start_visit(self):
        self.ast.accept(self)
        self.parser.reset()

    def act(self, visitable):
        """
        Called by the visitable. This is where the operations take place.
        """

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

        type_ = type(visitable)

        if type_ in base_types:
            index = visitable.index
            self.tokens[index] = deepcopy(self.parser.tokens[index])

        elif type_ == Operator:
            first_idx = visitable.op
            self.tokens[first_idx] = deepcopy(self.parser.tokens[first_idx])

            if (second_idx := visitable.rem_op) is not None:
                self.tokens[second_idx] = deepcopy(self.parser.tokens[second_idx])

        return True


class MainSemanticVisitor:
    """
    This visitor class walks a Raccoon's AST, gathers important information about the
    program and checks for some semantic validity.

    Making it do a lot in a single pass is an intentional design for preformance.

    List of what the visitor does:

    - Canonicalizes literal

    - Creates a symbol table

    - Saves variable declarations

    - Saves function deaclarations
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

    - Tracks variable-object lifetimes
    """

    def __init__(self, ast):
        self.visit_deep = False
        self.ast = ast
        self.symbol_table = {}
        self.current_scope = ""

    def start_visit(self):
        self.ast.accept(self)

    def act(self, visitable):
        """
        Called by the visitable. This is where the operations take place.
        """
        pass
