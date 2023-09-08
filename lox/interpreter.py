from .expression import ASTVisitor
from .expression import Expr, Binary, Grouping, Literal, Unary
from .tokentype import TokenType
from . import error

class Interpreter(ASTVisitor):

    def interpret(self, expression: Expr) -> bool:
        # Unlike book, I return bool if runtime error.
        # That's because I put my error handling in its own module and don't want
        # this to be calling methods of my main script
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
            return False
        except error.LoxRuntimeError as _error:
            error.runtime_error(_error)
            return True

    def stringify(self, value):
        if value is None:
            return 'nil'
        if isinstance(value, float):
            text = str(value)
            # Described at https://craftinginterpreters.com/evaluating-expressions.html#hooking-up-the-interpreter
            # this is hacky: explicit floats that happen to be int-ish will print like ints :shrug:
            if text.endswith('.0'):
                text = text[:-2]
            return text
        return str(value) # Hope this works for everything else :D

    # Implement all the necessary visitor methods

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> object:
        # This just unwraps the inner expression, of any type
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary) -> object:
        right = self.evaluate(expr.right)
        if expr.operator.tokentype == TokenType.BANG:
            return not self._is_truthy(right)
        elif expr.operator.tokentype == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -(float(right))
        else:
            # TODO better error handling? Should never get here anyway.
            raise Exception("Invalid unary operator %r" % expr.operator)

        # Supposedly unreachable.
        return None

    def visit_binary_expr(self, expr: Binary) -> object:
        # Order matters here! These might have side effects.
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        ttype = expr.operator.tokentype
        if ttype == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
        elif ttype == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        elif ttype == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif ttype == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif ttype == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif ttype == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif ttype == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif ttype == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                raise error.LoxRuntimeError("Operands must be two numbers or two strings.", expr.operator)
        elif ttype == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif ttype == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        # Supposedly unreachable.
        return None

    def evaluate(self, expr: Expr):
        # Generic "visit any kind of node"
        return expr.accept(self)

    def _is_equal(self, a, b) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def _is_truthy(self, val) -> bool:
        # Ruby-ish idea of truthiness.
        if val is None:
            return False
        if isinstance(val, bool):
            return bool(val)
        return True

    def _check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise error.LoxRuntimeError("Operand must be a number.", operator)

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise error.LoxRuntimeError("Operands must be numbers.", operator)
