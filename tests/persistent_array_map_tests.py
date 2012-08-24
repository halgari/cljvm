import unittest
import system.rt as rt
from system.core import integer


class TestArrayMap(unittest.TestCase):
    def test_count(self):
        mp = rt.hash_map.invoke0()
        assert rt.count.invoke1(mp).int() == 0