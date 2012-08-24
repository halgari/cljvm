import core
from system.bool import w_true, w_false
import util
from system.core import symbol
from system.rt import extend, equals

_tp_integer = symbol("system", "Integer")

class W_Integer(core.Object):
    def __init__(self, v):
        self.int_value = v

    def int(self):
        return self.int_value

    def type(self):
        return _tp_integer

def int_repr(self):
    return str(self.int())

#core.repr.install(core.symbol("system", "Integer"), util.interp2app(int_repr, "repr"))

@extend(equals, _tp_integer)
def int_equals(self, other):
    if not core.type(other) == _tp_integer:
        return w_false
    if self.int() == other.int():
        return w_true
    return w_false

