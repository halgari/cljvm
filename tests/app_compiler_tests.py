import unittest
from system.reader import read_from_string
from system.app_compiler import compile_in_module
from system.core import *
import system.rt

class Tests(unittest.TestCase):
    def test_compiler(self):
        form = read_from_string("((fn foo [x y] (add x y)))")
        fn = compile_in_module(form, system.rt)
        self.assertEqual(fn().invoke2(integer(1), integer(2)).int(), 3)
