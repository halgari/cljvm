import unittest


class Tests(unittest.TestCase):
    def test_Cons(self):
        import tests.cons
        tests.cons.run(self)
