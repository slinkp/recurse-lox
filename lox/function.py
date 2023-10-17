from dataclasses import dataclass
from .lox_callable import LoxCallable
from . import statement
from .environment import Environment

@dataclass
class LoxFunction(LoxCallable):
    # https://craftinginterpreters.com/functions.html#function-objects

    declaration: statement.Function
    closure: Environment
    is_initializer: bool = False

    def call(self, interpreter, arguments: list):
        """
        Sets the return value on the call stack
        """
        # Bind the params into names in the local environment.
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.parameters):
            environment.define(param.lexeme, arguments[i])

        interpreter.execute_block(self.declaration.body, environment)

        if self.is_initializer:
            # Special case per 12.7.1: Class initializers always return 'this'.
            # Needed here because init can be called explicitly.
            this = self.closure.get_at(0, "this")
            interpreter.innermost_call_state.return_value = this

    def arity(self):
        return len(self.declaration.parameters)

    def __str__(self):
        return "<fn %s>" % self.declaration.name.lexeme
