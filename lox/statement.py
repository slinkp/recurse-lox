from dataclasses import dataclass
from .scanner import Token
from .expression import Expr

import abc


class Stmt(abc.ABC):

    @abc.abstractmethod
    def accept(self, visitor: 'StmtVisitor'):
        pass

@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_print_stmt(self)

@dataclass
class ExpressionStmt(Stmt):
    expression: Expr

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_expression_stmt(self)


class StmtVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_print_stmt(self, expr: Print):
        pass

    @abc.abstractmethod
    def visit_expression_stmt(self, expr: ExpressionStmt):
        pass
