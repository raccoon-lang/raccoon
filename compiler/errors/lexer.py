
class LexerError(Exception):
    """ Represents the error the lexer can raise """

    def __init__(self, message, row, column):
        super().__init__(f"(line: {row}, col: {column}) {message}")
        self.message = message  # Added because it is missing after super init
        self.row = row
        self.column = column

    def __repr__(self):
        return (
            f'LexerError(message="{self.message}", row={self.row}'
            f", column={self.column})"
        )
