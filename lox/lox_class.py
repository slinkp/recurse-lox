from typing import Optional, Any

from .lox_callable import LoxCallable
from .function import LoxFunction
from .token import Token
from .error import LoxRuntimeError


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name

    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: list[object]):
        return LoxInstance(self)

    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]
        return None


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: dict[str, object] = {}

    def __str__(self):
        return self.klass.name + " instance"

    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method

        raise LoxRuntimeError("Undefined property '%s'." % name.lexeme, name)

    def set(self, name: Token, value: object):
        self.fields[name.lexeme] = value