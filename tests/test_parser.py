import unittest
from lox.parser import Parser

class Tests(unittest.TestCase):

    def test_instantiation(self):
        parser = Parser()

    def test_empty_tokens(self):
        parser = Parser()
