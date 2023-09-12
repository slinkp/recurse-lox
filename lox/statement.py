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


@dataclass
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_block_stmt(self)

@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_var_stmt(self)


class StmtVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_print_stmt(self, stmt: Print):
        pass

    @abc.abstractmethod
    def visit_expression_stmt(self, stmt: ExpressionStmt):
        pass

    @abc.abstractmethod
    def visit_var_stmt(self, stmt: Var):
        pass

    @abc.abstractmethod
    def visit_block_stmt(self, stmt: Block):
        pass
