from system.core import Object, symbol, integer
import system.rt as rt
from system.rt import extend

_tp = symbol("system", "PersistentArrayVector")


class PersistentArrayVector(Object):
    def __init__(self, lst_w, meta):
        self.lst_w = lst_w
        self._meta = meta

    def type(self):
        return _tp

    def repr(self):
        a = []
        for x in range(len(self.lst_w)):
            if self.lst_w[x] is None:
                a.append("nil")
            else:
                a.append(self.lst_w[x].repr())

        return "[" + " ".join(a) + "]"

@extend(rt._count, _tp)
def persistent_array_vector_count(self):
    return integer(len(self.lst_w))

@extend(rt._nth, _tp)
def persistent_array_vector_nth(self, w_nth):
    return self.lst_w[w_nth.int()]

@extend(rt.isvector, _tp)
def persistent_list_isvector(self):
    from system.bool import w_true
    return w_true

def from_pylist(lst):
    return PersistentArrayVector(lst[:], None)
