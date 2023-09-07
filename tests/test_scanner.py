import unittest
from lox.scanner import Token, TokenType, Scanner

class Tests(unittest.TestCase):

    eof = Token(tokentype=TokenType.EOF, lexeme="", literal=None, line=1)
    semi = Token(TokenType.SEMICOLON, ";", None, 1)

    def test_empty(self):
        for source in  '', ' ', '\n\t \r\n\n':
            scanner = Scanner(source)
            self.assertEqual([self.eof], scanner.scan_tokens())

    def test_var_identifier(self):
        source = 'var foo;'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        self.assertEqual(
           [
               Token(TokenType.VAR, "var", "var", 1),
               Token(TokenType.IDENTIFIER, "foo", "foo", 1),
               self.semi,
               self.eof,
            ],
            tokens)

    def test_numbers_and_strings(self):
        source = ' 123.45 \n "foo bar" '
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(
           [
               Token(TokenType.NUMBER, '123.45', 123.45, 1),
               Token(TokenType.STRING, '"foo bar"', "foo bar", 1),
               self.eof,
            ],
            tokens)


    # Not going to burn a lot of time here, but it's good to have a place to dump things when I find bugs
