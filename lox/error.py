import sys
from .tokentype import TokenType

def error(line: int, message: str):
    report(line, "", message)

def report(line: int, where: str, message: str):
    print(
        "[line %s] Error %s: %s" % (line, where, message),
        file=sys.stderr)

def token_error(token, message: str):
    if token.tokentype == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, " at '%s'"  % token.lexeme, message)
