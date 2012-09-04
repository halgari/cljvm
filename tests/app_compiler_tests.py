import unittest
from system.reader import read_from_string
from system.app_compiler import compile_in_module
import system.rt

class Tests(unittest.TestCase):
    def test_compiler(self):
        form = read_from_string("((fn [x y] (+ x y)))")
        fn = compile_in_module(form, system.rt)
        self.assertEqual(fn.invoke(1, 2), 3)
