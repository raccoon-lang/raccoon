"""
"""

from enum import Enum
from copy import deepcopy
from compiler.options import CompilerOptions
from compiler.codegen import LLVMCodegen, WasmCodegen, Codegen

class SymbolKind(Enum):
    VARIABLE = 0
    FUNCTION = 1
    CLASS = 2
    PARAM = 3


class Scope:
    """
    """
    def __init__(self, name, parent, typed={}, untyped={}):
        self.name = name
        self.parent = parent
        self.typed = typed
        self.untyped = untyped

    def __repr__(self):
        fields = deepcopy(vars(self))
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"


class SymbolInfo:
    """
    """

    def __init__(
        self,
        kind=None,
        ast_ref=None,
        instances=[],
        type_id=None,
        element_types=[],
        path="",
    ):
        self.kind = kind
        self.ast_ref = ast_ref
        self.instances = instances
        self.element_types = element_types
        self.path = path

    def __repr__(self):
        fields = deepcopy(vars(self))
        fields["ast_ref"] = "..."
        fields["kind"] = repr(self.kind)
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"


class TypeInfo:
    """
    """

    def __init__(
        self,
        name,
        subtype_range,
        overrides=[],
    ):
        self.name = name
        self.subtype_range = subtype_range
        self.overrides = overrides

    def __repr__(self):
        fields = deepcopy(vars(self))
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"


class SemanticInfo:
    """
    """

    def __init__(self, tokens, compiler_opts=CompilerOptions()):
        self.tokens = tokens
        self.current_path = ""
        self.compiler_opts = compiler_opts
        self.symbols = SemanticInfo.get_prelude_symbols()
        self.current_parent_scope = 0 # 0 since the current scope is __main__
        self.inheritance_lists = SemanticInfo.get_primitive_types()

    def exit_scope(self):
        self.current_parent_scope -= 1

    def add_new_scope(self, symbol_name):
        self.symbols.append(Scope(symbol_name, self.current_parent_scope))

    def add_new_symbol(self, name, symbol_info, typed=True):
        if typed:
            self.symbols[-1].typed[name] = symbol_info
        else:
            self.symbols[-1].untyped[name] = symbol_info

    def add_new_top_level_symbol(self, name, symbol_info, typed=True):
        if typed:
            self.symbols[0].typed[name] = symbol_info
        else:
            self.symbols[0].untyped[name] = symbol_info

    @staticmethod
    def get_primitive_types():
        """
        The first set of inheritance lists are assigned to primitive types.
        """
        return [
            [TypeInfo('void', (0, 1))], # 0.0
            [TypeInfo('int', (0, 1))], # 1.0
            [TypeInfo('i8', (0, 1))], # 2.0
            [TypeInfo('i16', (0, 1))], # 3.0
            [TypeInfo('i32', (0, 1))], # 4.0
            [TypeInfo('i64', (0, 1))], # 5.0
            [TypeInfo('uint', (0, 1))], # 6.0
            [TypeInfo('u8', (0, 1))], # 7.0
            [TypeInfo('u16', (0, 1))], # 8.0
            [TypeInfo('u32', (0, 1))], # 9.0
            [TypeInfo('u64', (0, 1))], # 10.0
            [TypeInfo('f32', (0, 1))], # 11.0
            [TypeInfo('f64', (0, 1))], # 12.0
        ]

    @staticmethod
    def get_prelude_symbols():
        """
        Get prelude symbols like str, int, etc.
        """

        # Create top-level scope and add __main__ to top-level
        top = [Scope("top", parent=-1, typed={
            "__main__": SymbolInfo(
                kind=SymbolKind.FUNCTION,
            )
        })]

        # Create __main__ scope
        top.append(Scope("__main__", parent=0))

        return top

    @staticmethod
    def get_prelude_ast():
        pass

    def __repr__(self):
        fields = deepcopy(vars(self))
        fields['kind'] = type(self).__name__
        string = ", ".join([f"{repr(key)}: {repr(val)}" for key, val in fields.items()])
        return "{" + string + "}"

