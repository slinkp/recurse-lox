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


## Testing

I wrapped up my python unit tests (with `coverage` reports), `mypy` type
checks, and the dart / lox tests from the [crafting intepreters
repo](https://github.com/munificent/craftinginterpreters/tree/master#testing)
in one `test-all` bash script.

Works:
```console

$ ./test-all
Type check...
Success: no issues found in 8 source files
Success: no issues found in 1 source file
Python tests...
test (tests.test_ast_visitor.Tests.test) ... ok
test_consume (tests.test_parser.Tests.test_consume) ... [line 0] Error  at 'var': whoops expected ===
ok
test_empty_tokens (tests.test_parser.Tests.test_empty_tokens) ... ok
test_instantiation (tests.test_parser.Tests.test_instantiation) ... ok
test_simple_literal_expr (tests.test_parser.Tests.test_simple_literal_expr) ... ok
test_simple_statement (tests.test_parser.Tests.test_simple_statement) ... [line 0] Error  at 'var': Expect expression.
ok
test_empty (tests.test_scanner.Tests.test_empty) ... ok
test_numbers_and_strings (tests.test_scanner.Tests.test_numbers_and_strings) ... ok
test_slashes (tests.test_scanner.Tests.test_slashes) ... ok
test_var_identifier (tests.test_scanner.Tests.test_var_identifier) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.002s

OK

Coverage report...
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
lox/__init__.py                 0      0   100%
lox/error.py                   17      5    71%   7-8, 11, 20, 25
lox/expression.py              59      6    90%   10, 48, 52, 56, 60, 81
lox/parser.py                 105     28    73%   27-29, 37-39, 47-49, 56-58, 65-67, 74, 76, 78, 84-86, 142-157
lox/scanner.py                105     12    89%   85-87, 93, 96, 99, 113, 116, 128, 141, 153, 157-158
lox/token.py                   18      5    72%   12-13, 16-17, 21
lox/tokentype.py                2      0   100%
tests/__init__.py               0      0   100%
tests/test_ast_visitor.py       9      0   100%
tests/test_parser.py           29      0   100%
tests/test_scanner.py          24      0   100%
---------------------------------------------------------
TOTAL                         368     56    85%

Dart tests...
Chapter 4...
All 6 tests passed (59 expectations).
Chapter 6...
All 1 tests passed (1 expectations).
Chapter 7...
All 1 tests passed (1 expectations).
```
