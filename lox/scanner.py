#!/usr/bin/env python3

import sys
import enum
from typing import Optional

from . import error

TokenType = enum.Enum(
    'TokenType',
    [
        # Single-character tokens.
        'LEFT_PAREN', 'RIGHT_PAREN', 'LEFT_BRACE', 'RIGHT_BRACE',
        'COMMA', 'DOT', 'MINUS', 'PLUS', 'SEMICOLON', 'SLASH', 'STAR',

        # One or two character tokens.
        'BANG', 'BANG_EQUAL',
        'EQUAL', 'EQUAL_EQUAL',
        'GREATER', 'GREATER_EQUAL',
        'LESS', 'LESS_EQUAL',

        # Literals.
        'IDENTIFIER', 'STRING', 'NUMBER',

        # Keywords.
        'AND', 'CLASS', 'ELSE', 'FALSE', 'FUN', 'FOR', 'IF', 'NIL', 'OR',
        'PRINT', 'RETURN', 'SUPER', 'THIS', 'TRUE', 'VAR', 'WHILE',
        'EOF'
    ]
)

keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}

class Token:
    def __init__(self, tokentype: TokenType, lexeme: str, literal: Optional[str], line: int):
        self.tokentype = tokentype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return "%s %s %s" % (self.tokentype, self.lexeme, self.literal)

    def __repr__(self):
        return "Token(%s)" % str(self)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return all([
            self.tokentype == other.tokentype,
            self.lexeme == other.lexeme,
            self.literal == other.literal
            ])  # Ignore line


class Scanner:
    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []

    def _is_at_end(self):
        return self.current >= len(self.source)

    def scan_tokens(self):
        while not self._is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                # Comments go to end of line
                print("Skipping comment")
                while self.peek() != '\n' and not self._is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in (' ', '\r', '\t'):
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self._handle_string()
        elif c.isdigit():
            self._handle_number()
        elif c.isalpha():
            self._handle_identifier()
        else:
            error.error(self.line, "Unexpected character: %s." % c)

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    def match(self, expected):
        """
        Consume next char only if it's the expected one
        """
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        if self._is_at_end():
            return ''
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return ''
        return self.source[self.current + 1]

    def add_token(self, tokentype, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(
            Token(tokentype, text, literal, self.line)
        )

    def _handle_string(self):
        while self.peek() != '"' and not self._is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self._is_at_end():
            error.error(self.line, "Unterminated string.")
            return

        # The closing ".
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)

    def _handle_number(self):
        while self.peek().isdigit() and not self._is_at_end():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            # Consume the '.'
            self.advance()
            while self.peek().isdigit() and not self._is_at_end():
                self.advance()
        value = self.source[self.start:self.current]
        self.add_token(TokenType.NUMBER, float(value))

    def _handle_identifier(self):
        while self.peek().isalnum():
            # Consume as many letters/digits as possible.
            # Important not to tokenize eg `or` as OR when we have `orange` as IDENTIFIER.
            self.advance()
        value = self.source[self.start:self.current]
        tokentype = keywords.get(value, TokenType.IDENTIFIER)
        self.add_token(tokentype, value)
