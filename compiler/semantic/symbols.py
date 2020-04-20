"""
"""
from enum import Enum


class SymbolKind(Enum):
    """
    The different kinds of symbols in a program.
    """

    FUNCTION = 0
    TYPE = 1
    VAR = 2


class SymbolInfo:
    """
    This contains the information about a symbol on the symbol table.
    """

    def __init__(self, kind=SymbolKind.VAR, scope_level=-1, ast_ref=None):
        self.kind = kind
        self.scope_level = scope_level
        self.ast_ref = ast_ref


class TypeInfo:
    """
    This contains the information about a type on the type table.
    """

    def __init__(self, name, structure=None):
        self.name = name
        self.structure = structure

