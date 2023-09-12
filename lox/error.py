import sys
from .tokentype import TokenType
from .token import Token

class LoxRuntimeError(RuntimeError):
    def __init__(self, message, token: Token):
        super().__init__(str(message))
        self.token = token

class ErrorReporter:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def reset(self):
        self.had_error = False

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        self.had_error = True
        print(
            "[%s] Error %s: %s" % (line, where, message),
            file=sys.stderr)

    def token_error(self, token, message: str):
        if token.tokentype == TokenType.EOF:
            self.report(token.line, "at end", message)
        else:
            self.report(token.line, "at '%s'"  % token.lexeme, message)

    def runtime_error(self, error: LoxRuntimeError):
        self.had_runtime_error = True
        print(
            "%s\n[line %s]" % (error, error.token.line),
            file=sys.stderr)
