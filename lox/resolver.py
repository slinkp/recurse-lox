import enum
from .expression import (
    Assign,
    Expr,
    ExprVisitor,
    Get,
    Set,
    This,
    Variable
    )
from .statement import StmtVisitor, Stmt, Block, Var, Function, Return, ClassStmt
from .token import Token
from .error import ErrorReporter


class FunctionType(enum.Enum):
    NONE = 1
    FUNCTION = 2
    METHOD = 3


class Resolver(ExprVisitor, StmtVisitor):
    """
    Chapter 11:
    https://craftinginterpreters.com/resolving-and-binding.html

    This walks the AST tree after parsing and does a few things:
    - Basic static analysis: Detect some errors like `return` outside a function.
    - Helps the interpreter resolve variables faster by jumping directly to the correct environment.
    - This also fixes closures to continue to point to the original location variables even if
      same names later get added to nearer ancestor scope(s) after function definition.
      (eg the bug example in https://craftinginterpreters.com/resolving-and-binding.html#static-scope)
    """
    def __init__(self, interpreter, error_reporter: ErrorReporter):
        self.interpreter = interpreter
        self.error_reporter = error_reporter or ErrorReporter()
        self.scopes: list[dict[str, bool]] = []
        # This is just here so we can track if we're inside a function definition or not.
        self._current_function: FunctionType = FunctionType.NONE

    ######################################################################
    # Var resolution
    def resolve_stmts(self, statements: list[Stmt]):
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, stmt: Stmt):
        stmt.accept(self)

    def resolve_expr(self, expr: Expr):
        expr.accept(self)

    def resolve_local(self, expr: Expr, name: Token):
        for depth, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, depth)
                return

    def declare(self, name: Token):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.error_reporter.token_error(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        scope[name.lexeme] = True

    ######################################################################
    # Statement visitor overrides

    def visit_block_stmt(self, stmt: Block):
        self._begin_scope()
        self.resolve_stmts(stmt.statements)
        self._end_scope()

    def visit_function_statement(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def visit_class_stmt(self, stmt: ClassStmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self._begin_scope() # Implicit scope for 'this'. Unclear why we don't use the existing one for the body?
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            self._resolve_function(method, FunctionType.METHOD)
        self._end_scope()

    ######################################################################
    # Expr visitor overrides, the important ones

    def visit_variable_expr(self, expr: Variable):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) == False:
            self.error_reporter.token_error(
                expr.name, "Can't read local variable in its own initializer."
            )
        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: Assign):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    ######################################################################
    # Boring expr visitor overrides

    def visit_call_expr(self, expr):
        self.resolve_expr(expr.callee)
        for arg in expr.arguments:
            self.resolve_expr(arg)

    def visit_binary_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_grouping_expr(self, expr):
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr):
        pass

    def visit_logical_expr(self, expr):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_unary_expr(self, expr):
        self.resolve_expr(expr.right)

    def visit_get_expr(self, expr: Get):
        # object dot access.
        # The property itself doesn't need resolving as it's looked up dynamically every time.
        self.resolve_expr(expr.object_)

    def visit_set_expr(self, expr: Set):
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object_)

    def visit_this_expr(self, expr: This):
        self.resolve_local(expr, expr.keyword)

    ######################################################################
    # Boring stmt visitor overrides

    def visit_expression_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_if_stmt(self, stmt):
        # Resolution is different from interpretation:
        # We visit both branches, since both *could* be run.
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt: Return):
        if self._current_function == FunctionType.NONE:
            self.error_reporter.token_error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            self.resolve_expr(stmt.value)

    def visit_while_stmt(self, stmt):
        # Book note in ch 11:
        # "You could imagine doing lots of other analysis in here. For example,
        # if we added break statements to Lox, we would probably want to ensure
        # they are only used inside loops."
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.statement)

    ######################################################################
    # Scope management

    def _begin_scope(self):
        scope: dict[str, bool] = {}
        self.scopes.append(scope)

    def _end_scope(self):
        self.scopes.pop()

    ######################################################################
    # private

    def _resolve_function(self, function: Function, function_type: FunctionType):
        enclosing_function: FunctionType = self._current_function
        self._current_function = function_type
        self._begin_scope()
        for param in function.parameters:
            self.declare(param)
            self.define(param)
        self.resolve_stmts(function.body)
        self._end_scope()
        self._current_function = enclosing_function
