from system.core import symbol, Object, integer
import system.rt as rt
from system.rt import extend

from system.jit import elidable

_tp = symbol("system", "PersistentList")

class PersistentList(Object):
    def __init__(self, w_head, w_tail, count, w_meta):
        self._w_head = w_head
        self._w_tail = w_tail
        self._count = count
        self._w_meta = w_meta

    def repr(self):
        from system.helpers import first, next
        s = self
        a = []
        while s is not None:
            if first(s) is None:
                a.append("nil")
            else:
                a.append(first(s).repr())
            s = next(s)
        return "(" + " ".join(a) + ")"

    def type(self):
        return _tp

EMPTY = PersistentList(None, None, 0, None)

def from_pylist(lst):
    s = EMPTY
    for x in range(len(lst) - 1, - 1, -1):
        s = persistent_list_cons(s, lst[x])
    return s


@extend(rt.first, _tp)
@elidable
def persistent_list_first(self):
    return self._w_head

@extend(rt.next, _tp)
@elidable
def persistent_list_next(self):
    return self._w_tail

@extend(rt._cons, _tp)
@elidable
def persistent_list_cons(self, other):
    if self is EMPTY:
        return PersistentList(other, None, 1, None)
    return PersistentList(other, self, self._count + 1, None)

@extend(rt._count, _tp)
@elidable
def persistent_list_count(self):
    return integer(self._count)

@extend(rt.islist, _tp)
def persistent_list_islist(self):
    from system.bool import w_true
    return w_true
