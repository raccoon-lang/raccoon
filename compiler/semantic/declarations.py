"""
This module ...
"""
from compiler.visitor import Visitor


class FunctionDeclVisitor(Visitor):
    """
    This class ...

    FuncParam:
     - name
     - type_annotation
     - default_value_expr

    PositionalParamsSeparator: []

    FuncParams:
     - params
     - tuple_rest_param
     - keyword_only_params
     - named_tuple_rest_param

    Function:
      - name
      - body
      - params
      - return_type_annotation
      - generics_annotation
      - is_async
      - decorators
    """

    def __init__(self, ast):
        self.frame = {}

    def start_visit(self):
        pass

    def act(self, visitable):
        pass


class VariableDeclVisitor(Visitor):
    """
    NamedExpression:
      - name
      - expr

    AssignmentStatement:
      - lhses
      - assignment_op
      - value_expr
      - type_annotation
    """

    def __init__(self, ast):
        pass

    def start_visit(self):
        pass

    def act(self, visitable):
        pass


class ClassDeclVisitor(Visitor):
    """
    Class:
      - name
      - body
      - parent_classes
      - generics_annotation
      - decorators
    """

    def __init__(self, ast):
        pass

    def start_visit(self):
        pass

    def act(self, visitable):
        pass
