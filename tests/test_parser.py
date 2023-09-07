import unittest
from lox.parser import Parser
from lox.tokentype import TokenType
from lox.scanner import Token
from lox.expression import Literal

class Tests(unittest.TestCase):

    def test_instantiation(self):
        parser = Parser()

    def test_empty_tokens(self):
        parser = Parser()
        self.assertEqual(
            None, parser.parse()
            )

    def test_simple_literal_expr(self):
        tokens = [
            Token(TokenType.NUMBER, '1', 1.0),
            Token(TokenType.EOF, '', None),
        ]
        parser = Parser(tokens)
        expr = parser.parse()
        self.assertEqual(Literal(value=1.0), expr)

    def test_simple_statement(self):
        # Equivalient to 'var foo = 1;'
        tokens = [
            Token(TokenType.VAR, 'var', 'var'),
            Token(TokenType.IDENTIFIER, 'foo', 'foo'),
            Token(TokenType.EQUAL, '=', None),
            Token(TokenType.NUMBER, '1', 1.0),
            Token(TokenType.SEMICOLON, ';', None),
            Token(TokenType.EOF, '', None),
        ]

        parser = Parser(tokens)
        expr = parser.parse()
        self.assertEqual(None, expr)
