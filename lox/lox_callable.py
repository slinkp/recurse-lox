import abc

class LoxCallable(abc.ABC):

    @abc.abstractmethod
    def call(self, interpreter, arguments: list):
        pass

    @abc.abstractmethod
    def arity(self) -> int:
        pass
