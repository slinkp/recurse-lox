from typing import Optional, List, Any

from .error import ErrorReporter, LoxRuntimeError
from .expression import Expr, Binary, Grouping, Literal, Unary, Variable, Assign, Logical, Call
from .expression import ExprVisitor
from .statement import Stmt, StmtVisitor, ExpressionStmt, Print, Var, Block, If, While, Function, Return, ClassStmt
from .tokentype import TokenType
from .token import Token
from .environment import Environment
from .lox_callable import LoxCallable, StupidReturnException
from .lox_class import LoxClass
from .function import LoxFunction
from . import native_functions


class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self, error_reporter: Optional[ErrorReporter] = None, use_resolver=False):
        self.error_reporter = error_reporter or ErrorReporter()
        self._environment = Environment()
        self.globals = self._environment
        self.globals.define("clock", native_functions.Clock())
        self._locals_distance: dict[int, int] = {}
        if use_resolver:
            # For chapter 11
            self._resolve_variable_expr = self._resolve_variable_expr_using_resolver
            self._assign_value_for_variable = self._assign_value_for_variable_using_resolver
        else:
            # For earlier chapters
            self._resolve_variable_expr = self._resolve_variable_expr_using_current_environment
            self._assign_value_for_variable = self._assign_value_for_variable_using_current_environment

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

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous_env = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self._environment = previous_env

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
        self.execute_block(stmt.statements, Environment(enclosing=self._environment))

    def visit_if_stmt(self, stmt: If):
        condition = self.evaluate(stmt.condition)
        if self._is_truthy(condition):
            self.execute(stmt.then_branch)
        else:
            if stmt.else_branch is not None:
                self.execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: While):
        # Thanks to de-sugaring, this also handles For loops
        while self.evaluate(stmt.condition):
            self.execute(stmt.statement)

    def visit_function_statement(self, stmt: Function):
        func = LoxFunction(stmt, self._environment)
        self._environment.define(stmt.name.lexeme, func)

    def visit_return_stmt(self, stmt: Return):
        # https://craftinginterpreters.com/functions.html#returning-from-calls
        # Question: Is there any reasonable way of doing this without abusing exceptions?
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise StupidReturnException(value)

    def visit_class_stmt(self, stmt: ClassStmt):
        self._environment.define(stmt.name.lexeme, None)
        _class: LoxClass = LoxClass(stmt.name.lexeme)
        self._environment.assign(stmt.name, _class)

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
        match ttype:
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    raise LoxRuntimeError("Operands must be two numbers or two strings.", expr.operator)
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self._check_number_operands(expr.operator, left, right)
                return float(left) * float(right)

        # Supposedly unreachable.
        return None

    def visit_variable_expr(self, expr: Variable):
        # The one funky thing here is we have two ways to do this depending what chapter we're in.
        return self._resolve_variable_expr(expr)

    def _resolve_variable_expr_using_current_environment(self, expr: Variable):
        # Variable resolution as per chapter 8.
        return self._environment.get(expr.name)

    def _resolve_variable_expr_using_resolver(self, expr: Variable):
        # Variable resolution as per chapter 11, corresponds to lookUpVariable in book code.
        name: Token = expr.name
        distance = self._get_distance(expr)
        if distance is not None:
            return self._environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def _get_distance(self, expr: Expr) -> Optional[int]:
        return self._locals_distance.get(id(expr))

    def _set_distance(self, expr: Expr, distance: int):
        self._locals_distance[id(expr)] = distance

    def visit_assign_expr(self, expr: Assign) -> Any:
        value: Any = self.evaluate(expr.value)
        return self._assign_value_for_variable(expr, value)

    def _assign_value_for_variable_using_current_environment(self, expr: Assign, value: Any) -> Any:
        self._environment.assign(expr.name, value)
        return value

    def _assign_value_for_variable_using_resolver(self, expr: Assign, value: Any) -> Any:
        distance = self._get_distance(expr)
        if distance is not None:
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_logical_expr(self, expr: Logical) -> Any:
        # Supports 'and', 'or'
        left_val = self.evaluate(expr.left)
        if self._is_truthy(left_val):
            if expr.operator.tokentype == TokenType.OR:
                return left_val
        elif expr.operator.tokentype == TokenType.AND:
            return left_val
        right_val = self.evaluate(expr.right)
        return right_val

    def visit_call_expr(self, expr: Call) -> Any:
        # Might be a variable, or a callback, method reference ...
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError("Can only call functions and classes.", expr.paren)
        args = [self.evaluate(arg) for arg in expr.arguments]
        if len(args) != callee.arity():
            raise LoxRuntimeError("Expected %d arguments but got %d." % (callee.arity(), len(args)), expr.paren)
        return callee.call(self, args)

    ############################################################
    # Helpers

    def resolve(self, expr: Expr, depth: int):
        # Records how deep in the environment stack an expression is stored.
        self._set_distance(expr, depth)

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
