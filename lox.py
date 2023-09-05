#!/usr/bin/env python3

import sys

class Scanner:
    def __init__(self, source):
        pass

    def scan_tokens(self):
        return []

class Lox:
    def __init__(self):
        self.had_error = False

    def main(self, args):
        if len(args) > 1:
            print("Usage: lox.py [script]")
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

    def run_file(self, path):
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

    def run(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        # For now just print
        for token in tokens:
            print(token)

    def error(self, line, message):
        self.report(line, "", message)

    def report(self, line, where, message):
        print(
            "[line " + line + "] Error " + where + ": " + message,
            file=sys.stderr)


if __name__ == '__main__':
    Lox().main(sys.argv[1:])
