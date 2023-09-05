import unittest

class Tests(unittest.TestCase):

    def test(self):
        # Need to import at runtime because ... reasons
        from lox.scanner import Token, TokenType
        from lox.expression import Binary, Unary, Literal, Grouping, ASTPrinter

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
