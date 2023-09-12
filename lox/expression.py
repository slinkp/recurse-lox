import abc
from dataclasses import dataclass
from typing import Any

from .scanner import Token


class Expr(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: 'ExprVisitor'):
        pass


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


class ExprVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass

    @abc.abstractmethod
    def visit_grouping_expr(self, expr: Grouping):
        pass

    @abc.abstractmethod
    def visit_literal_expr(self, expr: Literal):
        pass

    @abc.abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass

    @abc.abstractmethod
    def visit_variable_expr(self, expr: Variable):
        pass

    @abc.abstractmethod
    def visit_assign_expr(self, expr: Assign) -> Any:
        pass

class ASTPrinter(ExprVisitor):
    """
    An ExprVisitor that prints the value of expression tree in a lisp-like style
    (ie parenthesized with prefix operators).
    Useful for understanding the tree and that's all.
    """

    def print(self, expr):
        return expr.accept(self) or ""

    def visit_binary_expr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr: Variable):
        return expr.name.lexeme  # Is that all??

    def visit_assign_expr(self, expr: Assign):
        # Like C, and unlike Python, assignment is an expression, not a statement.
        return self.parenthesize("assign %s" % expr.name.lexeme, expr.value)

    def parenthesize(self, name, *exprs: Expr):
        strings = ' '.join(expr.accept(self) or "" for expr in exprs)
        return "(%s %s)" % (name, strings)

