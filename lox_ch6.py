#!/usr/bin/env python3
import sys

from lox.scanner import Scanner
from lox.parser import Parser
from lox.expression import ASTPrinter

class Lox:
    def __init__(self):
        self.had_error = False

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
        if self.had_error:
            sys.exit(65)

    def run_prompt(self):
        while True:
            line = sys.stdin.readline()
            if line is None:
                break
            self.run(line)
            self.had_error = False

    def run(self, source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        # print(tokens)
        parser = Parser(tokens)
        expression = parser.parse_expr()
        if expression is None:
            return
        if self.had_error:
            return
        print(ASTPrinter().print(expression))


if __name__ == '__main__':
    Lox().main(sys.argv[1:])
