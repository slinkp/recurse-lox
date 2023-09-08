#!/usr/bin/env python3

import sys
from typing import Optional

from . import error
from .tokentype import TokenType

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
    def __init__(self, tokentype: TokenType, lexeme: str, literal: Optional[str], line: int=0):
        self.tokentype = tokentype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return "TokenType.%s, %r, %r" % (self.tokentype.name, self.lexeme, self.literal)

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
        self._mapping = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '-': TokenType.MINUS,
            '+': TokenType.PLUS,
            ';': TokenType.SEMICOLON,
            '*': TokenType.STAR,
            '!': self._handle_bang,
            '=': self._handle_eq,
            '<': self._handle_lt,
            '>': self._handle_gt,
            '/': self._handle_slash,
            ' ': self._handle_whitespace,
            '\r': self._handle_whitespace,
            '\t': self._handle_whitespace,
            '\n': self._handle_newline,
            '"': self._handle_string,
        }


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
        token_or_action = self._mapping.get(c)
        if isinstance(token_or_action, TokenType):
            self.add_token(token_or_action)
        elif callable(token_or_action):
            token_or_action()
        elif token_or_action is None:
            if c.isdigit():
                self._handle_number()
            elif c.isalpha():
                self._handle_identifier()
            else:
                self._handle_unexpected_char()
        else:
            error.error("Bug! Unhandled case for character %s" % c)

    def _handle_whitespace(self):
        pass

    def _handle_eq(self):
        self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)

    def _handle_lt(self):
        self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)

    def _handle_gt(self):
        self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)

    def _handle_slash(self):
        if self.match('/'):
            # Comments go to end of line
            while self.peek() != '\n' and not self._is_at_end():
                self.advance()
        else:
            self.add_token(TokenType.SLASH)

    def _handle_newline(self):
        self.line += 1

    def _handle_bang(self):
        self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)

    def _handle_unexpected_char(self):
        error.error(self.line, "Unexpected character: %s." % self.source[self.current])

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
