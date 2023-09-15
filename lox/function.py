from dataclasses import dataclass
from .lox_callable import LoxCallable, StupidReturnException
from . import statement
from .environment import Environment

@dataclass
class LoxFunction(LoxCallable):
    # https://craftinginterpreters.com/functions.html#function-objects

    declaration: statement.Function
    closure: Environment
    is_initializer: bool = False

    def call(self, interpreter, arguments: list):
        # Bind the params into names in the local environment.
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.parameters):
            environment.define(param.lexeme, arguments[i])

        ret_value = None
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except StupidReturnException as e:
            ret_value = e.value

        if self.is_initializer:
            # Special case per 12.7.1: Class initializers always return 'this'.
            this = self.closure.get_at(0, "this")
            ret_value = this
        return ret_value

    def arity(self):
        return len(self.declaration.parameters)

    def __str__(self):
        return "<fn %s>" % self.declaration.name.lexeme
