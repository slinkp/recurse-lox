import abc
from dataclasses import dataclass
from typing import Any, List

from .scanner import Token


class Expr(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: 'ExprVisitor'):
        pass # pragma: no cover


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)

@dataclass
class Literal(Expr):
    value: object

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor) -> Any:
        return visitor.visit_assign_expr(self)


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)

@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)


@dataclass
class Call(Expr):
    # Expr callee, Token paren, List<Expr> arguments",
    callee: Expr
    paren: Token
    arguments: List[Expr]

    def accept(self, visitor):
        return visitor.visit_call_expr(self)


@dataclass
class Get(Expr):
    # Used for object.property access
    object_: Expr
    name: Token

    def accept(self, visitor):
        return visitor.visit_get_expr(self)


@dataclass
class Set(Expr):
    # Used to assign obj properties
    object_: Expr
    name: Token
    value: Expr

    def accept(self, visitor):
        return visitor.visit_set_expr(self)


@dataclass
class This(Expr):
    keyword: Token

    def accept(self, visitor):
        return visitor.visit_this_expr(self)


@dataclass
class Super(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor):
        return visitor.visit_super_expr(self)


class ExprVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_grouping_expr(self, expr: Grouping):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_literal_expr(self, expr: Literal):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_variable_expr(self, expr: Variable):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_assign_expr(self, expr: Assign) -> Any:
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_logical_expr(self, expr: Logical):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_call_expr(self, expr: Call):
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_get_expr(self, expr: Get) -> Any:
        pass # pragma: no-cover

    @abc.abstractmethod
    def visit_super_expr(self, expr: Super) -> Any:
        pass # pragma: no-cover


class ASTPrinter(ExprVisitor):
    """
    An ExprVisitor that prints the value of expression tree in a lisp-like style
    (ie parenthesized with prefix operators).
    Useful for understanding the tree and that's all.
    """

    def print(self, expr):
        return expr.accept(self) or ""

    def visit_binary_expr(self, expr: Binary):
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self._parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr: Variable):
        return expr.name.lexeme  # Is that all??

    def visit_assign_expr(self, expr: Assign):
        # Like C, and unlike Python, assignment is an expression, not a statement.
        return self._parenthesize("= %s" % expr.name.lexeme, expr.value)

    def visit_logical_expr(self, expr: Logical):
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_call_expr(self, expr: Call):
        # hmm, in lisp it's just (func-name arg...)
        return self._parenthesize("call", expr.callee, *expr.arguments)

    def visit_get_expr(self, expr: Get):
        # hmmmm
        return self._parenthesize("get %r" % expr.name.lexeme, expr.object_)

    def visit_set_expr(self, expr: Set):
        # hmmmm
        return self._parenthesize("set %r" % expr.name.lexeme, expr.object_, expr.value)

    def visit_this_expr(self, expr: This):
        # hmmmm
        return "this"

    def visit_super_expr(self, expr: Super):
        return "super.%s" % expr.method.lexeme

    def _parenthesize(self, name, *exprs: Expr):
        strings = ' '.join(expr.accept(self) or "" for expr in exprs)
        return "(%s %s)" % (name, strings)

