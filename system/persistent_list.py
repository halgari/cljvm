from system.core import symbol, Object, integer
import system.rt as rt
from system.rt import extend


_tp = symbol("system", "PersistentList")

class PersistentList(Object):
    def __init__(self, w_head, w_tail, count, w_meta):
        self._w_head = w_head
        self._w_tail = w_tail
        self._count = count
        self._w_meta = w_meta

    def type(self):
        return _tp

EMPTY = PersistentList(None, None, 0, None)

@extend(rt.first, _tp)
def persistent_list_first(self):
    return self._w_head

@extend(rt.next, _tp)
def persistent_list_next(self):
    return self._w_tail

@extend(rt._cons, _tp)
def persistent_list_cons(self, other):
    if self is EMPTY:
        return PersistentList(other, None, 1, None)
    return PersistentList(other, self, self._count + 1, None)

@extend(rt.count, _tp)
def persistent_list_count(self):
    return integer(self._count)




