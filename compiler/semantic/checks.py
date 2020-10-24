"""
"""

from compiler.errors import SemanticError


class SemanticChecks:
    @staticmethod
    def param_name_conflict(param_name_token, function_name_token, scope):
        """
        Check param names do not conflict with each other.
        """

        param_name_str = param_name_token.data
        param_name_row = param_name_token.row
        param_name_col = param_name_token.column
        function_name_str = function_name_token.data

        if param_name_str in scope.typed or param_name_str in scope.untyped:
            raise SemanticError(
                f"Duplicate parameter name `{param_name_str}` in function `{function_name_str}`",
                param_name_row,
                param_name_col
            )
