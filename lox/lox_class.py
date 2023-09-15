from .lox_callable import LoxCallable
from .token import Token
from .error import LoxRuntimeError

class LoxClass(LoxCallable):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: list[object]):
        return LoxInstance(self)


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: dict[str, object] = {}

    def __str__(self):
        return self.klass.name + " instance"

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        else:
            raise LoxRuntimeError("Undefined property '%s'." % name.lexeme, name)

    def set(self, name: Token, value: object):
        self.fields[name.lexeme] = value
