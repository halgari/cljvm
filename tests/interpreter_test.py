import unittest

from system.interpreter import *
from system.objspace import *


class InterpTests(unittest.TestCase):
    def test_BINARY_ADD(self):
        code = to_bcode(BINARY_ADD)
        interp = Interpreter(code, to_stack(W_Int(21), W_Int(21)))
        val = s_unwrap_int(interp.main_loop())
        self.assertEqual(val, 42)

    def test_BINARY_SUB(self):
        code = to_bcode(BINARY_SUB)
        interp = Interpreter(code, to_stack(W_Int(21), W_Int(21)))
        val = s_unwrap_int(interp.main_loop())
        self.assertEqual(val, 0)

