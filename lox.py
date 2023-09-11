#!/usr/bin/env python3
import sys

from lox.scanner import Scanner
from lox.parser import Parser
from lox.expression import ASTPrinter
from lox.interpreter import Interpreter
from lox.error import ErrorReporter

class Lox:
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.interpreter = Interpreter(error_reporter=self.error_reporter)

    @property
    def had_error(self):
        return self.error_reporter.had_error

    @property
    def had_runtime_error(self):
        return self.error_reporter.had_runtime_error

    def had_any_error(self):
        return self.had_error or self.had_runtime_error

    def main(self, args: list[str]):
        if len(args) > 1:
            print("Usage: lox.py [script]")
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

    def run_file(self, path: str):
        _bytes = open(path, 'r').read()
        self.run(_bytes)
        if self.had_any_error():
            sys.exit(65)

    def run_prompt(self):
        while True:
            line = sys.stdin.readline()
            if line is None:
                break
            self.run(line)
            self.error_reporter.reset()

    def run(self, source: str):
        scanner = Scanner(source, error_reporter=self.error_reporter)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, error_reporter=self.error_reporter)
        statements = parser.parse()
        if self.had_error:
            return
        self.interpreter.interpret(statements)


if __name__ == '__main__':
    Lox().main(sys.argv[1:])
