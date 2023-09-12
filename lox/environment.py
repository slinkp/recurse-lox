from typing import Any
from .error import LoxRuntimeError
from .token import Token

class Environment:
    def __init__(self):
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise LoxRuntimeError("Undefined variable '%s'." % name.lexeme, name)

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise LoxRuntimeError("Undefined variable '%s'." % name.lexeme, name)
