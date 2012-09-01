import system.rt as rt
from core import Object
from system.rt import extend
from system.jit import *

class W_Symbol(rt.Object):
    def __init__(self, _ns, _name):
        from util import intern
        assert _name is not None
        self._ns = intern(_ns)
        self._name = intern(_name)



    def __eq__(self, other):
        from system.helpers import equals, w_true
        return equals(self, other) is w_true

    def type(self):
        return _tp

    def repr(self):
        if self._ns is None:
            return self._name
        return self._ns + "/" + self._name
    def __repr__(self):
        return self.repr()

_tp = W_Symbol("system", "Symbol")

@extend(rt.equals, _tp)
def equal(self, other):
    return symbol_equals(self, other)

def symbol_equals(self, other):
    from system.helpers import w_true, w_false
    if self is other:
        return w_true
    if not isinstance(other, W_Symbol):
        return w_false
    if self._name is other._name\
    and self._ns is other._ns:
        return w_true
    return w_false

@extend(rt.repr, _tp)
@elidable
def symbol_repr(self, a):
    if a._ns is None:
        return a._name
    return a._ns + "/" + a._name
