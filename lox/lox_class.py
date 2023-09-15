from .lox_callable import LoxCallable

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

    def __str__(self):
        return self.klass.name + " instance"
