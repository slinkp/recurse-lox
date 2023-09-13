import time

from .lox_callable import LoxCallable

class Clock(LoxCallable):

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        return time.time()

    def __str__(self):
        return "<native fn>"
