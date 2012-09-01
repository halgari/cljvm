from funcs import Func
from system.jit import elidable


def interp2app(func, sym = None):
    _symbol_ = sym if sym is not None else func.__name__
    def invoke0(self):
        return func()
    def invoke1(self, a):
        return func(a)
    def invoke2(self, a, b):
        return func(a, b)
    def invoke3(self, a, b, c):
        return func(a, b, c)
    def invoke4(self, a, b, c, d):
        return func(a, b, c, d)

    tp = {"invoke0" : invoke0,\
          "invoke1" : invoke1,\
          "invoke2" : invoke2,\
          "invoke3" : invoke3, \
          "invoke4" : invoke4, \
          "_symbol_" : _symbol_}
    for x in range(5):
        if x != func.func_code.co_argcount:
            del tp["invoke"+str(x)]
    newtp = type(_symbol_, (Func,), tp)
    newtp.__module__ = func.__module__
    return newtp()

class StringCache(object):
    def __init__(self):
        self._cache = {}

    def intern(self, string):
        if string not in self._cache:
            self._cache[string] = string
        return self._cache[string]

_string_cache = StringCache()

def intern(string):
    return _string_cache.intern(string)


def assertEqual(self, first, other):
    from system.helpers import equals
    from bool import w_true

    self.assertTrue(equals(first, other) is w_true)
