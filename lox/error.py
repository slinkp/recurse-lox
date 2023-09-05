import sys

def error(line, message):
    report(line, "", message)

def report(line, where, message):
    print(
        "[line %s] Error %s: %s" % (line, where, message),
        file=sys.stderr)
