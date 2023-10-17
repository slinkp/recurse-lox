import abc

class LoxCallable(abc.ABC):

    @abc.abstractmethod
    def call(self, interpreter, arguments: list):
        """
        Represents something callable, eg a function or class.
        """
        pass

    @abc.abstractmethod
    def arity(self) -> int:
        pass
