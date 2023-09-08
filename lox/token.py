from typing import Optional
from .tokentype import TokenType

class Token:
    def __init__(self, tokentype: TokenType, lexeme: str, literal: Optional[str], line: int=0):
        self.tokentype = tokentype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        literal = "null" if self.literal is None else self.literal
        return "%s %s %s" % (self.tokentype.name, self.lexeme, literal)

    def __repr__(self):
        fields = "TokenType.%s, %r, %r" % (self.tokentype.name, self.lexeme, self.literal)
        return "Token(%s)" % fields

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return all([
            self.tokentype == other.tokentype,
            self.lexeme == other.lexeme,
            self.literal == other.literal
            ])  # Ignore line
