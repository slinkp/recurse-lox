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
(I managed to get coverage to include lines covered by dart, too.)

It works:
```console
$ ./test-all

Type check...
Success: no issues found in 8 source files
Success: no issues found in 1 source file
Python tests...
test (python_tests.test_ast_visitor.Tests.test) ... ok
test_evaluate_binary (python_tests.test_interpreter.Tests.test_evaluate_binary) ... ok
test_evaluate_unary (python_tests.test_interpreter.Tests.test_evaluate_unary) ... ok
test_instantiation (python_tests.test_interpreter.Tests.test_instantiation) ... ok
test_runtime_error (python_tests.test_interpreter.Tests.test_runtime_error) ... ok
test_consume (python_tests.test_parser.Tests.test_consume) ... [line 0] Error  at 'var': whoops expected ===
ok
test_empty_tokens (python_tests.test_parser.Tests.test_empty_tokens) ... ok
test_instantiation (python_tests.test_parser.Tests.test_instantiation) ... ok
test_simple_literal_expr (python_tests.test_parser.Tests.test_simple_literal_expr) ... ok
test_simple_statement (python_tests.test_parser.Tests.test_simple_statement) ... [line 0] Error  at 'var': Expect expression.
ok
test_empty (python_tests.test_scanner.Tests.test_empty) ... ok
test_numbers_and_strings (python_tests.test_scanner.Tests.test_numbers_and_strings) ... ok
test_slashes (python_tests.test_scanner.Tests.test_slashes) ... ok
test_var_identifier (python_tests.test_scanner.Tests.test_var_identifier) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.003s

OK

Dart tests...
Chapter 4...
All 6 tests passed (59 expectations).
Chapter 6...
All 1 tests passed (1 expectations).
Chapter 7...
All 1 tests passed (1 expectations).
Coverage report...
Name                               Stmts   Miss  Cover   Missing
----------------------------------------------------------------
lox.py                                49     12    76%   28-29, 33, 39, 42-47, 55, 57
lox/__init__.py                        0      0   100%
lox/error.py                          25      5    80%   16, 19, 29, 34-35
lox/expression.py                     59      6    90%   10, 48, 52, 56, 60, 81
lox/interpreter.py                    93     22    76%   16-17, 21, 29, 49, 63, 65-66, 68-69, 71-72, 74-75, 94, 103-105, 110, 113, 118, 123
lox/parser.py                        106     10    91%   38-40, 143-158
lox/scanner.py                       106      8    92%   86-88, 117, 129, 142, 154, 158-159
lox/token.py                          18      3    83%   16-17, 21
lox/tokentype.py                       2      0   100%
lox_ch4.py                            34     10    71%   15-16, 20, 26, 29-34
lox_ch6.py                            38     12    68%   14-15, 19, 25, 28-33, 42, 44
python_tests/__init__.py               0      0   100%
python_tests/test_ast_visitor.py       9      0   100%
python_tests/test_interpreter.py      34      0   100%
python_tests/test_parser.py           29      0   100%
python_tests/test_scanner.py          24      0   100%
----------------------------------------------------------------
TOTAL                                626     88    86%

All passed
```
