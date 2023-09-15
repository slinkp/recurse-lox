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
        # Resolution pre-chapter 11: we walk back up the chain
        # until we find the name.
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        elif self._enclosing is not None:
            return self._enclosing.get(name)

        raise LoxRuntimeError("Undefined variable '%s'." % name.lexeme, name)

    def get_at(self, distance: int, name: str):
        # Resolution for chapter 11:
        # If static analysis has run as per chapter 11, using resolver,
        # then we know exactly where each variable was defined.
        return self._ancestor(distance)._values[name]

    def _ancestor(self, distance: int) -> 'Environment':
        env: Optional[Environment] = self
        for i in range(distance):
            assert env is not None
            env = env._enclosing
        assert env is not None
        return env

    def assign(self, name: Token, value: Any):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        elif self._enclosing is not None:
            return self._enclosing.assign(name, value)

        raise LoxRuntimeError("Undefined variable '%s'." % name.lexeme, name)

    def assign_at(self, distance: int, name: Token, value: Any):
        self._ancestor(distance)._values[name.lexeme] = value
