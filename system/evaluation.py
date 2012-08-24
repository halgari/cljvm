from system.rt import PolymorphicFunc, extend
from system.symbol import W_Symbol
import system.integer
from core import equal
import system.rt as rt

from system.helpers import *



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

def dispatch_invoke(fn, a):
    if len(a) == 0:
        return fn.invoke0()
    if len(a) == 1:
        return fn.invoke1(a[0])
    if len(a) == 2:
        return fn.invoke2(a[0], a[1])
    if len(a) == 3:
        return fn.invoke3(a[0], a[1], a[2])

def eval_form(self, globals, frame, can_tail_call):
    if count(self).int() == 0:
        return self

    fn = eval_item.invoke4(first(self), globals, frame, can_tail_call)

    if isinstance(fn, rt.FExpr):
        eval_args = False
    else:
        eval_args = True

    args = []

    s = next(self)
    while s is not None:
        itm = first(s)
        if eval_args:
            args.append(eval_item.invoke4(itm, globals, frame, False))
        else:
            args.append(itm)

        s = next(s)

    return dispatch_invoke(fn, args)

eval_item = PolymorphicFunc()



@extend(eval_item, W_Symbol)
def eval_W_Symbol(self, globals, frame, can_tail_call):
    return resolve(self, globals, frame)


def self_evaluating(self, globals, frame, can_tail_call):
    return self

from system.util import interp2app
import system.persistent_list
eval_item.install(system.integer._tp_integer, interp2app(self_evaluating))
eval_item.install(system.persistent_list._tp, interp2app(eval_form))

def eval(form):
    frame = ResolveFrame([], [])
    globals = {}
    return eval_item.invoke4(form, globals, frame, True)