import unittest

from system.evaluation import eval
from system.core import integer, symbol
from system.util import assertEqual
import system.rt as rt

rt.init()

class TestEvaluation(unittest.TestCase):
    def test_int(self):
        result = eval(integer(1))
        assertEqual(self, result, integer(1))

    def test_add(self):
        lst = rt.list.invoke_args([symbol(None, "+"), integer(1), integer(2)])
        result = eval(lst)
        assertEqual(self, result, integer(3))

