import abc
import typing

class LoxCallable(abc.ABC):

    @abc.abstractmethod
    def call(self, interpreter, arguments: list):
        pass

    @abc.abstractmethod
    def arity(self) -> int:
        pass

class StupidReturnException(Exception):
    def __init__(self, value: typing.Any, *args, **kw):
        self.value = value
        super().__init__(*args, **kw)

