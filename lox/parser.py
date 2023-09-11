from typing import Optional, List
from .expression import Expr, Binary, Unary, Literal, Grouping
from .statement import Stmt, Print, ExpressionStmt
from .tokentype import TokenType
from .scanner import Token
from .error import ErrorReporter

class Parser:
    def __init__(self, tokens: Optional[list[Token]] = None, error_reporter: Optional[ErrorReporter] = None):
        self.current = 0
        self.tokens = tokens or []
        self.error_reporter = error_reporter or ErrorReporter()

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self.is_at_end():
            try:
                statements.append(self.statement())
            except ParseError:
                pass # XXX
        return statements

    def parse_expr(self) -> Optional[Expr]:
        # Legacy  method for chapters < 8
        try:
            return self.expression()
        except ParseError:
            return None

    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self._print_statement()
        else:
            return self._expression_statement()

    def _print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def expression(self):
        return self.equality()

    def equality(self) -> Expr:
        # Rule:
        # comparison ( ( "!=" | "==" ) comparison )* ;

        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        # ( "!" | "-" ) unary | primary ;

        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        # NUMBER | STRING | "true" | "false" | "nil | "(" expression ")" ;
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    ############################################################################3
    # Private

    def match(self, *types: TokenType) -> bool:
        for tokentype in types:
            if self.check(tokentype):
                self.advance()
                return True
        return False

    def check(self, ttype: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().tokentype == ttype

    def is_at_end(self) -> bool:
        if self.current >= len(self.tokens):
            # This wasn't in book, but catches eg empty token list
            return True
        return self.peek().tokentype == TokenType.EOF

    def peek(self) -> Token:
        if self.current >= len(self.tokens):
            # This wasn't in book, but catches eg empty token list
            raise ParseError("Unexpected end of stream")
        return self.tokens[self.current]


    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def consume(self, ttype: TokenType, err_message: str) -> Token:
        # Like advance() but blows up if token isn't of the expected type
        if self.check(ttype):
            return self.advance()
        raise self.error(self.peek(), err_message)

    def error(self, token: Token, message: str) -> 'ParseError':
        # Return instead of raising so the caller can decide
        # whether to bomb out or attempt to recover and parse more.
        # https://craftinginterpreters.com/parsing-expressions.html#entering-panic-mode
        self.error_reporter.token_error(token, message)
        return ParseError()

    def synchronize(self):
        # Discard tokens until we get to beginning of next statement.
        # This is for recovering from parse errors and then continuing parsing.
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            elif self.peek().tokentype in (
                    TokenType.FUN,
                    TokenType.VAR,
                    TokenType.OR,
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.PRINT,
                    TokenType.RETURN,
            ):
                return
            else:
                self.advance()


class ParseError(Exception):
    pass
