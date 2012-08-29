from system.rt import PolymorphicFunc, extend
from system.symbol import W_Symbol
from system.core import Object
from system.bool import w_true, w_false
import system.integer
import system.rt as rt



from system.helpers import *



class ResolveFrame(Object):
    def __init__(self, w_arg_names, w_args):
        self._w_arg_names = w_arg_names
        self._w_args = w_args


def get_arg_idx(w_arg_names, sym):
    for x in range(len(w_arg_names)):
        if equals(w_arg_names[x], sym) is w_true:
            return x
    return -1


def resolve(self, globals, frame):
    idx = get_arg_idx(frame._w_arg_names, self)
    if idx >= 0:
        return frame._w_args[idx]
    idx = get_arg_idx(globals._w_arg_names, self)
    if idx >= 0:
        return globals._w_args[idx]
    idx = get_arg_idx(rt.builtins._w_arg_names, self)
    assert idx >= 0, "finding " + self.repr()
    return rt.builtins._w_args[idx]


def dispatch_invoke(fn, a):
    if len(a) == 0:
        return fn.invoke0()
    if len(a) == 1:
        return fn.invoke1(a[0])
    if len(a) == 2:
        return fn.invoke2(a[0], a[1])
    if len(a) == 3:
        return fn.invoke3(a[0], a[1], a[2])
    if len(a) == 4:
        return fn.invoke4(a[0], a[1], a[2], a[3])

def eval_form(self, globals, frame, can_tail_call):
    if count(self).int() == 0:
        return self

    fn = eval_item.invoke4(first(self), globals, frame, w_false)

    if isinstance(fn, rt.FExpr) or isinstance(fn, rt.VariadicFExpr):
        eval_args = False
    else:
        eval_args = True

    args = []

    s = next(self)
    while s is not None:
        itm = first(s)
        if eval_args:
            args.append(eval_item.invoke4(itm, globals, frame, w_false))
        else:
            args.append(itm)

        s = next(s)

    return dispatch_invoke(fn, args)

eval_item = PolymorphicFunc()





def self_evaluating(self, globals, frame, can_tail_call):
    return self

def eval_symbol(self, globals, frame, can_tail_call):
    return resolve(self, globals, frame)

from system.util import interp2app
import system.persistent_list
import system.symbol
eval_item.install(system.integer._tp_integer, interp2app(self_evaluating))
eval_item.install(system.persistent_list._tp, interp2app(eval_form))
eval_item.install(system.symbol._tp, interp2app(eval_symbol))

def eval(form):
    frame = ResolveFrame([], [])
    globals = ResolveFrame([], [])
    return eval_item.invoke4(form, globals, frame, w_true)


