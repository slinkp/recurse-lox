from typing import Optional, List
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
from .statement import (
    Block,
    ClassStmt,
    ExpressionStmt,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Var,
    While,
)
from .tokentype import TokenType
from .scanner import Token
from .error import ErrorReporter


MAX_ARGS = 255


class Parser:
    def __init__(
        self,
        tokens: Optional[list[Token]] = None,
        error_reporter: Optional[ErrorReporter] = None,
    ):
        self.current = 0
        self.tokens = tokens or []
        self.error_reporter = error_reporter or ErrorReporter()

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def parse_expr(self) -> Optional[Expr]:
        # Legacy  method for chapters < 8
        try:
            return self.expression()
        except ParseError:
            return None

    def declaration(self) -> Optional[Stmt]:
        # declaration > funDecl | varDecl | statement ;
        # funDecl -> "fun" function ;
        # function -> IDENTIFIER "(" parameters? ")" block ;
        try:
            if self.match(TokenType.FUN):
                return self._function("function")
            if self.match(TokenType.CLASS):
                return self._class_declaration()
            if self.match(TokenType.VAR):
                return self._var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def _function(self, kind: str) -> Function:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect %s name." % kind)
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after %s name." % kind)
        parameters: List[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= MAX_ARGS:
                    self.error(
                        self.peek(), "Can't have more than %d parameters." % MAX_ARGS
                    )
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before %s body." % kind)
        body: List[Stmt] = self._block()
        return Function(name, parameters, body)

    def _class_declaration(self) -> ClassStmt:
        # classDecl -> "class" IDENTIFIER ( "<" IDENTIFIER )? "{" function* "}" ;

        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass = None
        if self.match(TokenType.LESS):
            superclass_id = self.consume(
                TokenType.IDENTIFIER, "Expect superclass name."
            )
            superclass = Variable(superclass_id)

        self.consume(TokenType.LEFT_BRACE, "Expect '{' after class name.")
        methods: list[Function] = []
        while not self.is_at_end() and not self.check(TokenType.RIGHT_BRACE):
            method = self._function("method")
            methods.append(method)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        _class = ClassStmt(name, methods, superclass)
        return _class

    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self._if_statement()
        elif self.match(TokenType.FOR):
            return self._for_statement()
        elif self.match(TokenType.WHILE):
            return self._while_statement()
        elif self.match(TokenType.PRINT):
            return self._print_statement()
        elif self.match(TokenType.RETURN):
            return self._return_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return Block(self._block())
        else:
            return self._expression_statement()

    def _print_statement(self) -> Print:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def _expression_statement(self) -> ExpressionStmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def _if_statement(self) -> If:
        # -> "if" "(" expression ")" statement ( "else" statement )? ;
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch: Stmt = self.statement()
        else_branch: Optional[Stmt] = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def _while_statement(self) -> While:
        # -> "while" "(" expression ")" statement;
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        statement: Stmt = self.statement()
        return While(condition, statement)

    def _for_statement(self) -> Stmt:
        # "for" "(" ( varDecl | exprStmt | ";" ) expression? ";" expression? ")" statement
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer: Optional[Stmt] = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Optional[Expr] = None
        if not (self.check(TokenType.SEMICOLON)):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Optional[Expr] = None
        if not (self.check(TokenType.RIGHT_PAREN)):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self.statement()

        ######################################################################
        # De-sugaring!
        # https://craftinginterpreters.com/control-flow.html#desugaring
        ######################################################################

        if increment is not None:
            # The increment expression just runs after every time we do the body,
            # so combine them into a block.
            body = Block([body, ExpressionStmt(increment)])

        # You can always express 'for' as an equivalent 'while'.
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        # SHove the whole thing into a block that does the initialization first.
        if initializer is not None:
            body = Block([initializer, body])

        return body

    def _return_statement(self):
        keyword: Token = self.previous()
        value: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return Return(keyword, value)

    def _var_declaration(self) -> Var:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self) -> Expr:
        # Most of the methods for handling expression types
        # delegate to other expression types.
        # This mirrors the grammar as defined in the book
        # in appendix I (https://craftinginterpreters.com/appendix-i.html)
        # eg:
        # expression -> assignment ;
        # assignment -> ... IDENTIFIER "=" assignment | logic_or ;
        # logic_or -> ... etc etc
        return self.assignment()

    def assignment(self) -> Expr:
        # assignment -> ( call "." )? IDENTIFIER "=" assignment | logic_or ;
        # https://craftinginterpreters.com/statements-and-state.html#assignment-syntax
        expr: Expr = self.or_()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            # Since assignment is right-associative, we recursively call
            # assignment() to parse the right-hand side.
            value: Expr = self.assignment()
            if isinstance(expr, Variable):
                name_token: Token = expr.name
                return Assign(name_token, value)
            elif isinstance(expr, Get):
                # Yes, Get. Object *access* can be the left side of assignment.
                # See 12.4.2 in the book.
                get: Get = expr
                return Set(get.object_, get.name, value)
            else:
                # We'll support more complex expressions later
                # (anythign that evaluates to an assignable reference).
                self.error(equals, "Invalid assignment target.")
        return expr

    def or_(self) -> Expr:
        expr: Expr = self.and_()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_()  # Why is this and()?
            expr = Logical(expr, operator, right)
        return expr

    def and_(self) -> Expr:
        expr: Expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

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

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
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
        # unary -> ( "!" | "-" ) unary | call ;

        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self) -> Expr:
        # call -> primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
        # arguments -> expression ( "," expression )* ;
        expr: Expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                expr = Get(expr, name)
            else:
                break
        return expr

    def _finish_call(self, callee: Expr) -> Call:
        arguments: list[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= MAX_ARGS:
                    self.error(
                        self.peek(), "Can't have more than %d arguments." % MAX_ARGS
                    )
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        # "true" | "false" | "nil" | "this"
        #      | NUMBER | STRING | IDENTIFIER | "(" expression ")"
        #      | "super" "." IDENTIFIER ;
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.SUPER):
            keyword: Token = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method: Token = self.consume(
                TokenType.IDENTIFIER, "Expect superclass method name."
            )
            return Super(keyword, method)

        if self.match(TokenType.THIS):
            return This(self.previous())

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

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

    def error(self, token: Token, message: str) -> "ParseError":
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
            if self.previous().tokentype == TokenType.SEMICOLON:
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
