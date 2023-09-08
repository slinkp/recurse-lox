## About

Working through https://craftinginterpreters.com/
but in Python 3.

Q: How far can I get in 4 hours??

A: Finished chapter 6!
This gave me a working scanner, an Expression AST tree, and a tree visitor to
print the AST as a lisp-like syntax as per the book.  The `lox.py` provides a primitive REPL.
And a couple very basic unit tests, and checked my python type declarations with `mypy`.

... well, mostly.
I hadn't found the existing [Lox test suite](https://github.com/munificent/craftinginterpreters/tree/master#testing)
so there were some undiscovered bugs in my code, but I'm still really happy with that progress.
