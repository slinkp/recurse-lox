from dataclasses import dataclass
from .scanner import Token
import abc

class ASTVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_binary_expr(self, expr):
        pass

    @abc.abstractmethod
    def visit_grouping_expr(self, expr):
        pass

    @abc.abstractmethod
    def visit_literal_expr(self, expr):
        pass

    @abc.abstractmethod
    def visit_unary_expr(self, expr):
        pass

class ASTPrinter(ASTVisitor):
    """
    An ASTVisitor that prints the value of expression tree in a lisp-like style
    (ie parenthesized with prefix operators).
    Useful for understanding the tree and that's all.
    """

    def print(self, expr):
        return expr.accept(self) or ""

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        strings = ' '.join(expr.accept(self) or "" for expr in exprs)
        return "(%s %s)" % (name, strings)


class Expr(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor):
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