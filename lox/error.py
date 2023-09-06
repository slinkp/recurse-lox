import sys

def error(line: int, message: str):
    report(line, "", message)

def report(line: int, where: str, message: str):
    print(
        "[line %s] Error %s: %s" % (line, where, message),
        file=sys.stderr)
