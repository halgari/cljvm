from system.polymorphic_func import PolymorphicFunc, extend
from system.symbol import W_Symbol
from core import equal



eval = PolymorphicFunc()

class ResolveFrame(object):
    def __init__(self, w_arg_names, w_args):
        self._w_args_names = w_arg_names
        self._w_args = w_args


def get_arg_idx(w_arg_names, sym):
    for x in range(len(w_arg_names)):
        if equal(w_arg_names[x], sym):
            return x
    return -1


def resolve(self, globals, frame):
    idx = get_arg_idx(frame._w_arg_names, self)
    if idx >= 0:
        return frame._w_args[idx]
    idx = get_arg_idx(globals._w_arg_names, self)
    if idx >= 0:
        return globals._w_args[idx]
    idx = get_arg_idx(builtins._w_arg_names, self)
    assert idx >= 0
    return builtins._w_args[idx]




@extend(eval, W_Symbol)
def eval_W_Symbol(self, globals, frame, can_tail_call):
    return resolve(self, globals, frame)


def self_evaluating(self, globals, frame, can_tail_call):
    return self

eval.install(W_Int, self_evaluating)