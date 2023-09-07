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

    def test_slashes(self):
        source = '  1 / 2 // 3 / 4\n 5 / 6'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual(
            [
                Token(TokenType.NUMBER, "1", 1.0, 1),
                Token(TokenType.SLASH, "/", None, 1),
                Token(TokenType.NUMBER, "2", 2.0, 1),
                Token(TokenType.NUMBER, "5", 5.0, 1),
                Token(TokenType.SLASH, "/", None, 1),
                Token(TokenType.NUMBER, "6", 6.0, 1),
                self.eof,
            ],
            tokens)
