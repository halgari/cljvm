from core import type
from rt import Func
from util import interp2app

class PolymorphicFunc(Func):
    def __init__(self):
        self._overrides = {}

    def invoke1(self, a):
        tp = type(a)
        if tp not in self._overrides:
            assert False
        return self._overrides[tp].invoke1(a)

    def invoke2(self, a, b):
        tp = type(a)
        if tp not in self._overrides:
            assert False
        return self._overrides[tp].invoke2(a, b)

    def invoke3(self, a, b, c):
        tp = type(a)
        if tp not in self._overrides:
            assert False
        return self._overrides[tp].invoke3(a, b, c)

    def invoke4(self, a, b, c, d):
        tp = type(a)
        if tp not in self._overrides:
            assert False
        return self._overrides[tp].invoke4(a, b, c, d)

    def install(self, tp, func):
        self._overrides[tp] = func


def extend(func, tp):
    def inner(f):
        appfn = interp2app(f)
        func.install(tp, appfn)
        return appfn
    return inner

