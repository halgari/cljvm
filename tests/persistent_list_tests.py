import unittest
import system.rt as rt
from system.core import integer


class TestPersistentList(unittest.TestCase):
    def test_count(self):
        lst = rt.list.invoke0()
        assert rt.count.invoke1(lst).int() == 0

        lst = rt.list.invoke1(integer(1))
        assert rt.count.invoke1(lst).int() == 1

        lst = rt.list.invoke2(integer(2), integer(1))
        assert rt.count.invoke1(lst).int() == 2

        lst = rt.list.invoke3(integer(1), integer(3), integer(1))
        assert rt.count.invoke1(lst).int() == 3
