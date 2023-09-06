#!/usr/bin/env python3
import sys

from lox.scanner import Scanner


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

        # For now just print
        for token in tokens:
            print(token)


if __name__ == '__main__':
    Lox().main(sys.argv[1:])
