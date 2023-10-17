from typing import Optional, List, Any
from dataclasses import dataclass

from .error import ErrorReporter, LoxRuntimeError
from .expression import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
    )
from .expression import ExprVisitor
from .statement import Stmt, StmtVisitor, ExpressionStmt, Print, Var, Block, If, While, Function, Return, ClassStmt
from .tokentype import TokenType
from .token import Token
from .environment import Environment
from .lox_callable import LoxCallable
from .lox_class import LoxClass, LoxInstance
from .function import LoxFunction
from . import native_functions


@dataclass
class CallState:
    is_returning: bool = False
    return_value: object = None


class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self, error_reporter: Optional[ErrorReporter] = None, use_resolver=False):
        self.error_reporter = error_reporter or ErrorReporter()
        self._environment = Environment()
        self.globals = self._environment
        self.globals.define("clock", native_functions.Clock())
        self._locals_distance: dict[int, int] = {}
        self._call_stack: list[CallState] = []
        if use_resolver:
            # For chapter 11
            self._resolve_variable_expr = self._resolve_variable_expr_using_resolver
            self._assign_value_for_variable = self._assign_value_for_variable_using_resolver
        else:
            # For earlier chapters
            self._resolve_variable_expr = self._resolve_variable_expr_using_current_environment
            self._assign_value_for_variable = self._assign_value_for_variable_using_current_environment

    @property
    def innermost_call_state(self) -> CallState:
        if self._call_stack:
            return self._call_stack[-1]
        return CallState()

    @property
    def is_returning(self) -> bool:
        return self.innermost_call_state.is_returning

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
                if self.is_returning:
                    break
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
            if self.is_returning:
                break

    def visit_function_statement(self, stmt: Function):
        func = LoxFunction(stmt, self._environment, is_initializer=False)
        self._environment.define(stmt.name.lexeme, func)

    def visit_return_stmt(self, stmt: Return):
        # https://craftinginterpreters.com/functions.html#returning-from-calls
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        # Unlike the book, I don't like using exceptions for return values.
        # Instead we update the top of our stack of CallState, and check
        # `is_returning` in the few appropriate places.
        self.innermost_call_state.return_value = value
        self.innermost_call_state.is_returning = True

    def visit_class_stmt(self, stmt: ClassStmt):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError("Superclass must be a class.", stmt.superclass.name)

        self._environment.define(stmt.name.lexeme, None)

        if superclass is not None:
            self._environment = Environment(self._environment)
            self._environment.define("super", superclass)

        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self._environment, is_initializer=is_initializer)
            methods[method.name.lexeme] = function

        _class: LoxClass = LoxClass(stmt.name.lexeme, methods, superclass)

        if superclass is not None:
            assert self._environment._enclosing is not None
            self._environment = self._environment._enclosing
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
        # Variable resolution as per chapter 11
        name: Token = expr.name
        return self.lookup_variable_using_resolver(name, expr)

    def lookup_variable_using_resolver(self, name: Token, expr: Expr):
        # Corresponds to lookUpVariable in book code chapter 11.
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
        state = CallState()
        self._call_stack.append(state)
        # print("Call stack after append: size: %s, innermost: %s" % (len(self._call_stack), state))
        try:
            callee = self.evaluate(expr.callee)
            if not isinstance(callee, LoxCallable):
                raise LoxRuntimeError("Can only call functions and classes.", expr.paren)
            args = [self.evaluate(arg) for arg in expr.arguments]
            if len(args) != callee.arity():
                raise LoxRuntimeError("Expected %d arguments but got %d." % (callee.arity(), len(args)), expr.paren)
            callee.call(self, args)
            return state.return_value
        finally:
            # print("Call stack before pop: size: %s, popping: %s" % (len(self._call_stack), state))
            self._call_stack.pop()

    def visit_get_expr(self, expr: Get) -> Any:
        # Object dot access.
        obj = self.evaluate(expr.object_)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        else:
            raise LoxRuntimeError("Only instances have properties.", expr.name)

    def visit_set_expr(self, expr: Set) -> Any:
        # Object dot assignment.
        obj = self.evaluate(expr.object_)
        if isinstance(obj, LoxInstance):
            value = self.evaluate(expr.value)
            obj.set(expr.name, value)
        else:
            raise LoxRuntimeError("Only instances have fields.", expr.name)
        return value

    def visit_this_expr(self, expr: This) -> Any:
        return self.lookup_variable_using_resolver(expr.keyword, expr)

    def visit_super_expr(self, expr: Super) -> Any:
        distance = self._get_distance(expr)
        assert distance is not None
        superclass: LoxClass = self._environment.get_at(distance, "super")

        # Horrible hack, we just know that 'this' scope is one beyond 'superclass' scope.
        obj: LoxInstance = self._environment.get_at(distance -1, "this")

        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise LoxRuntimeError("Undefined property '%s'." % expr.method.lexeme, expr.method)

        return obj.bind(method)

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
