from dataclasses import dataclass
from .lox_callable import LoxCallable, StupidReturnException
from . import statement
from .environment import Environment

@dataclass
class LoxFunction(LoxCallable):
    # https://craftinginterpreters.com/functions.html#function-objects

    declaration: statement.Function
    closure: Environment

    def call(self, interpreter, arguments: list):
        # Bind the params into names in the local environment.
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.parameters):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except StupidReturnException as e:
            return e.value

    def arity(self):
        return len(self.declaration.parameters)

    def __str__(self):
        return "<fn %s>" % self.declaration.name.lexeme
