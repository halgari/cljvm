import core
import util

class W_Integer(core.Object):
    def __init__(self, v):
        self.int_value = v

    def int(self):
        return self.int_value

def int_repr(self):
    return str(self.int())

#core.repr.install(core.symbol("system", "Integer"), util.interp2app(int_repr, "repr"))
