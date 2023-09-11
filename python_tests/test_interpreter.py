import unittest
from lox.interpreter import Interpreter
from lox.error import LoxRuntimeError

class Tests(unittest.TestCase):

    def get_expr(self, code):
        # Very lazily use other classes instead of building exprs
        from lox.parser import Parser
        from lox.scanner  import Scanner
        scanner = Scanner(code)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        expression = parser.parse()
        return expression

    def test_instantiation(self):
        Interpreter()

    def test_evaluate_binary(self):
        result_mapping = {
            "1 + 1": 2,
            "3 * 4": 12,
            '"a" + "b"': "ab",
            "6.0 / 3": 2,
            "nil == nil": True,
            "(3.5 + 2.5) / 2": 3,
        }
        for code, expected in result_mapping.items():
            expr = self.get_expr(code)
            interpreter = Interpreter()
            result = interpreter.evaluate(expr)
            self.assertEqual(expected, result, "Unexpected result from code %r" % code)

    def test_evaluate_unary(self):
        result_mapping = {
            "! true": False,
            "! false": True,
            "!! true": True,
        }
        for code, expected in result_mapping.items():
            expr = self.get_expr(code)
            interpreter = Interpreter()
            result = interpreter.evaluate(expr)
            self.assertEqual(expected, result, "Unexpected result from code %r" % code)

    def test_runtime_error(self):
        code = 'nil + 23'
        expr = self.get_expr(code)
        interpreter = Interpreter()
        with self.assertRaises(LoxRuntimeError):
            result = interpreter.evaluate(expr)
