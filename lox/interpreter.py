from typing import Optional, List, Any

from .error import ErrorReporter, LoxRuntimeError
from .expression import Expr, Binary, Grouping, Literal, Unary, Variable, Assign
from .expression import ExprVisitor
from .statement import Stmt, StmtVisitor, ExpressionStmt, Print, Var, Block, If
from .tokentype import TokenType
from .environment import Environment

class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self, error_reporter: Optional[ErrorReporter] = None):
        self.error_reporter = error_reporter or ErrorReporter()
        self._environment = Environment()

    def interpret(self, statements: List[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as _error:
            self.error_reporter.runtime_error(_error)

    def interpret_ch7(self, expression: Expr):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except LoxRuntimeError as _error:
            self.error_reporter.runtime_error(_error)

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
        if isinstance(value, bool):
            return str(value).lower()
        return str(value) # Hope this works for everything else :D

    def execute(self, statement: Stmt):
        # Generic "visit any kind of statement"
        statement.accept(self)

    def evaluate(self, expr: Expr):
        # Generic "visit any kind of expression"
        return expr.accept(self)

    # Implement all the necessary visitor methods

    ############################################################
    # StmtVisitor methods

    def visit_expression_stmt(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, stmt: Var):
        # Un-initialized variables are None by default.
        # https://craftinginterpreters.com/statements-and-state.html#interpreting-global-variables
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self._environment.define(stmt.name.lexeme, value)

    def visit_block_stmt(self, stmt: Block):
        self._execute_block(stmt.statements, Environment(enclosing=self._environment))

    def visit_if_stmt(self, stmt: If):
        condition = self.evaluate(stmt.condition)
        if self._is_truthy(condition):
            self.execute(stmt.then_branch)
        else:
            if stmt.else_branch is not None:
                self.execute(stmt.else_branch)

    ############################################################
    # ExprVisitor methods

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
        # We could turn this into a dict that dispatches to callables,
        # but I don't feel like defining all those methods and I don't like lambdas :-p
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
                raise LoxRuntimeError("Operands must be two numbers or two strings.", expr.operator)
        elif ttype == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif ttype == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        # Supposedly unreachable.
        return None

    def visit_variable_expr(self, expr: Variable):
        return self._environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value: Any = self.evaluate(expr.value)
        self._environment.assign(expr.name, value)
        return value

    ############################################################
    # Helpers

    def _is_equal(self, a, b) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        # Booleans: be careful not to return true for `false == 0`
        if isinstance(a, bool) and not isinstance(b, bool):
            return False
        if isinstance(b, bool) and not isinstance(a, bool):
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
        raise LoxRuntimeError("Operand must be a number.", operator)

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError("Operands must be numbers.", operator)

    def _execute_block(self, statements: list[Stmt], environment: Environment):
        previous_env = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self._environment = previous_env
