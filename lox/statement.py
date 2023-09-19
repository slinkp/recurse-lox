from dataclasses import dataclass
from typing import Optional
import abc

from .scanner import Token
from .expression import Expr, Variable


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
    initializer: Optional[Expr]

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_var_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_if_stmt(self)


@dataclass
class While(Stmt):
    condition: Expr
    statement: Stmt

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_while_stmt(self)


@dataclass
class Function(Stmt):
    name: Token
    parameters: list[Token]
    body: list[Stmt]

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_function_statement(self)


@dataclass
class Return(Stmt):
    keyword: Token  # the `return` itself, for error reporting.
    value: Optional[Expr]

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_return_stmt(self)


@dataclass
class ClassStmt(Stmt):
    name: Token
    methods: list[Function]
    # Superclass is expressed as a single name, but we access it as a variable.
    superclass: Optional[Variable]

    def accept(self, visitor: 'StmtVisitor'):
        visitor.visit_class_stmt(self)


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

    @abc.abstractmethod
    def visit_if_stmt(self, stmt: If):
        pass

    @abc.abstractmethod
    def visit_while_stmt(self, stmt: While):
        pass

    @abc.abstractmethod
    def visit_function_statement(self, stmt: Function):
        pass

    @abc.abstractmethod
    def visit_return_stmt(self, stmt: Return):
        pass

    @abc.abstractmethod
    def visit_class_stmt(self, stmt: ClassStmt):
        pass
