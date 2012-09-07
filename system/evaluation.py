from system.rt import PolymorphicFunc, extend
from system.symbol import W_Symbol
from system.core import Object
from system.bool import w_true, w_false
from system.jit import elidable
from system.util import interp2app
from system.funcs import AFn
import system.integer
import system.rt as rt

from system.jit import *

def get_printable_location(func):
    if func is None:
        return "nil"
    return func.repr()

jitdriver = JitDriver(greens=['func'],
        reds=['globals', 'frame'],
        virtualizables=['frame'],
        get_printable_location = get_printable_location)


from system.helpers import *



class ResolveFrame(Object):
    _virtualizable2_ = ['_w_args_names', 'w_arg_names']
    def __init__(self, w_arg_names, w_args):
        self._w_arg_names = w_arg_names
        self._w_args = w_args

class TailCallTrampoline(Object):
    def __init__(self, w_fn, args_w):
        self._w_fn = w_fn
        self._args_w = args_w

    def apply_to(self):
        if isinstance(self._w_fn, AFn):
            return self._w_fn.invoke_args(self._args_w)
        else:
            return rt.invoke.invoke_args([self._w_fn] + self._args_w)


@unroll_safe
def get_arg_idx(w_arg_names, sym):
    w_arg_names = promote(w_arg_names)
    sym = promote(sym)
    for x in range(len(w_arg_names)):
        if equals(w_arg_names[x], sym) is w_true:
            return x
    return -1


def resolve(self, globals, frame):
    idx = promote(get_arg_idx(frame._w_arg_names, self))
    if idx >= 0:
        return frame._w_args[idx]
    idx = promote(get_arg_idx(globals._w_arg_names, self))
    if idx >= 0:
        return globals._w_args[idx]
    idx = promote(get_arg_idx(rt.builtins._w_arg_names, self))
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

@unroll_safe
def eval_form(self, globals, frame, can_tail_call):
    if count(self).int() == 0:
        return self

    fn = eval_item.invoke4(promote(first(self)), globals, frame, w_false)

    if isinstance(fn, rt.FExpr) or isinstance(fn, rt.VariadicFExpr):
        eval_args = False
    else:
        eval_args = True

    args = []

    s = promote(next(self))
    argc = promote(count(s))
    args = [None] * argc.int()
    for x in range(argc.int()):
        itm = promote(first(s))
        if eval_args:
            args[x] = eval_item.invoke4(itm, globals, frame, w_false)
        else:
            args[x] = itm

        s = promote(next(s))

    if can_tail_call is w_true \
       and eval_args is True:
        return TailCallTrampoline(fn, args)

    if eval_args is False:
        #FExpr need context arguments
        args = [globals, frame, can_tail_call] + args
        return fn.invoke_args(args)

    if isinstance(fn, AFn):
        return fn.invoke_args(args)
    else:
        return rt.invoke.invoke_args([fn] + args)


_eval_item = PolymorphicFunc()





def self_evaluating(self, globals, frame, can_tail_call):
    return self

def eval_symbol(self, globals, frame, can_tail_call):
    return resolve(self, globals, frame)

from system.util import interp2app
import system.persistent_list
import system.persistent_array_vector
import system.symbol
_eval_item.install(system.integer._tp_integer, interp2app(self_evaluating))
_eval_item.install(system.persistent_list._tp, interp2app(eval_form))
_eval_item.install(system.persistent_array_vector._tp, interp2app(self_evaluating))
_eval_item.install(system.symbol._tp, interp2app(eval_symbol))

class EvalItem(rt.Func):
    def invoke4(self, form, globals, frame, can_tail_call):
        return _eval_item.invoke4(form, globals, frame, can_tail_call)


eval_item = EvalItem()


def eval(form):
    frame = ResolveFrame([], [])
    globals = ResolveFrame([], [])
    ret = eval_item.invoke4(form, globals, frame, w_true)
    while isinstance(ret, TailCallTrampoline):
        ret = ret.apply_to()
    return ret
