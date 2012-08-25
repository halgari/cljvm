import system.rt as rt
from core import Object
from system.rt import extend

class W_Symbol(rt.Object):
    def __init__(self, _ns, _name):
        from util import intern
        self._ns = intern(_ns)
        self._name = intern(_name)

    def equal(self, other):
        if not isinstance(self, W_Symbol):
            return False
        if self._name is other._name \
          and self._ns is other._ns:
            return True
        return False

    def __eq__(self, other):
        return self.equal(other)

    def type(self):
        return _tp

    def repr(self):
        if self._ns is None:
            return self._ns
        return self._ns + "/" + self._name

_tp = W_Symbol("system", "Symbol")


@extend(rt.repr, _tp)
def symbol_repr(self, a):
    if a._ns is None:
        return a._ns
    return a._ns + "/" + a._name



