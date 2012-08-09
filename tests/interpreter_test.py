import unittest

from system.interpreter import *
from system.objspace import *
from system.ast import Const, Add, Subtract, Argument, Func


class InterpTests(unittest.TestCase):
    def test_CONST(self):
        f = Const(W_Int(42))
        val = Interpreter(f.toFunction()).main_loop()
        self.assertEqual(s_unwrap_int(val), 42)

    def test_BINARY_ADD(self):
        f = Add(Const(W_Int(22)), Const(W_Int(20)))
        val = Interpreter(f.toFunction()).main_loop()
        self.assertEqual(s_unwrap_int(val), 42)

    def test_BINARY_SUB(self):
        f = Subtract(Const(W_Int(22)), Const(W_Int(20)))
        val = Interpreter(f.toFunction()).main_loop()
        self.assertEqual(s_unwrap_int(val), 2)

    def test_ARG(self):
        a = Argument("x")
        f = Func([a], a)
        val = Interpreter(f.toFunction()).main_loop(W_Int(42))
        self.assertEqual(s_unwrap_int(val), 42)

    def test_ARGs(self):
        a = Argument("a")
        b = Argument("b")
        f = Func([a, b], Add(a, b))
        val = Interpreter(f.toFunction()).main_loop(W_Int(1), W_Int(2))
        self.assertEqual(s_unwrap_int(val), 3)
