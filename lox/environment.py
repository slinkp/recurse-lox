from typing import Any, Optional
from .error import LoxRuntimeError
from .token import Token

class Environment:
    def __init__(self, enclosing: Optional['Environment']=None):
        self._values: dict[str, Any] = {}
        self._enclosing = enclosing

    def define(self, name: str, value: Any):
        self._values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        elif self._enclosing is not None:
            return self._enclosing.get(name)

        raise LoxRuntimeError("Undefined variable '%s'." % name.lexeme, name)

    def assign(self, name: Token, value: Any):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        elif self._enclosing is not None:
            return self._enclosing.assign(name, value)

        raise LoxRuntimeError("Undefined variable '%s'." % name.lexeme, name)
