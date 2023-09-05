import unittest
from ..expression import *
from ..scanner import Token, TokenType

class Tests(unittest.TestCase):

    def test(self):
        # operator=Unary(
        #     operator=Token(TokenType.MINUS, "-", None, 1),
        #     right=Literal(123))

        expr = Binary(
            left=Unary(
                operator=Token(TokenType.MINUS, "-", None, 1),
                right=Literal(123)),
            operator=Token(TokenType.STAR, '*', None, 1),
            right=Grouping(
                Literal(45.67)
                ))

        printer = ASTPrinter()
        result = printer.print(expr)
        self.assertEqual(
            '(* (- 123) (group 45.67))', result
        )
