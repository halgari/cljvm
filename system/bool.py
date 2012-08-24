import core

class W_Bool(core.Object, core.SelfEvaluating):
    def __init__(self, v):
        self.bool_value = v

    def bool(self):
        return self.bool_value

    def repr(self):
        return "true" if self.bool_value else "false"

w_true = W_Bool(True)
w_false = W_Bool(False)

def bool(o):
    if o == True:
        return w_true
    return w_false
