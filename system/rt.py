from core import Object
from util import interp2app

from funcs import *

def extend(func, tp):
    def inner(f):
        appfn = interp2app(f)
        func.install(tp, appfn)
        return f
    return inner




class List(VariadicFunc):
    _symbol_ = "list"
    def __init__(self):
        pass
    def invoke_args(self, w_args):
        from system.persistent_list import EMPTY
        s = EMPTY
        for x in range(len(w_args) - 1, -1, -1):
            s = cons.invoke2(w_args[x], s)
        return s

list = List()

class FuncInstance(VariadicFunc):
    def __init__(self, w_globals, w_name, w_args, w_body):
        self._w_name = w_name
        self._w_args = [w_name] + w_args
        self._w_body = w_body
        self._w_globals = w_globals
    def repr(self):
        return "FuncInstance<" + self._w_name.repr() + ">"
    def invoke_args(self, args_w):
        assert len(self._w_args) - 1 == len(args_w)
        from system.evaluation import ResolveFrame, eval_item, TailCallTrampoline
        from system.bool import w_true
        from system.evaluation import jitdriver
        args_w = [self] + args_w
        frame = ResolveFrame(self._w_args, args_w)

        jitdriver.jit_merge_point(frame = frame,
                                  globals = self._w_globals,
                                  func = self)

        ret = eval_item.invoke4(self._w_body, self._w_globals, frame, w_true)
        return ret


class Fn(VariadicFExpr):
    _symbol_ = "fn"
    def __init__(self):
        pass
    def invoke_args(self, args_w):
        from system.helpers import first, next
        globals, frame, can_tail_call, name, s = args_w[:5]
        body = args_w[5:][0]
        args = []
        while s is not None:
            args.append(first(s))
            s = next(s)
        return FuncInstance(globals, name ,args, body)

fn = Fn()


class If(FExpr):
    _symbol_ = "if"
    def __init__(self):
        pass
    def invoke6(self, globals, frame, ctc, cond, then, el):
        from system.evaluation import eval_item, w_false
        res = eval_item.invoke4(cond, globals, frame, w_false)
        if res is not w_false and res is not None:
            return eval_item.invoke4(then, globals, frame, ctc)
        else:
            return eval_item.invoke4(el, globals, frame, ctc)
    def invoke5(self, globals, frame, ctc, cond, then):
        return self.invoke6(globals, frame, ctc, cond, then, None)

iffn = If()


class HashMap(VariadicFunc):
    _symbol_ = "hash-map"
    def __init__(self):
        pass
    def invoke_args(self, args_w):
        from system.persistent_array_map import EMPTY
        s = EMPTY
        for x in range(0, len(args_w), 2):
            s = assoc.invoke3(s, args_w[x], args_w[x + 1])
        return s

@interp2app
def keyword(ns, name):
    from system.keywords import keyword
    return keyword(ns, name)

hash_map = HashMap()


from system.util import interp2app
cons = interp2app(lambda a, b: _cons.invoke2(b, a), "cons")

assoc = interp2app(lambda a, b, c: _assoc.invoke3(a, b, c), "assoc")

add = interp2app(lambda a, b: _add.invoke2(a, b), "+")
count = interp2app(lambda a: _count.invoke1(a), "count")
nth = interp2app(lambda a, b: _nth.invoke2(a, b), "nth")

repr = PolymorphicFunc()
eval = PolymorphicFunc()
first = PolymorphicFunc()
next = PolymorphicFunc()
_count = PolymorphicFunc()
_cons = PolymorphicFunc()
_assoc = PolymorphicFunc()
_get = PolymorphicFunc()
equals = PolymorphicFunc(symbol = "=")

invoke = PolymorphicFunc(symbol = "invoke")

@interp2app
def _default_false(self):
    from system.bool import w_false
    return w_false

isvector = PolymorphicFunc(symbol = "vector?", default = _default_false)
islist = PolymorphicFunc(symbol = "list?", default = _default_false)

_add = PolymorphicFunc()
_nth = PolymorphicFunc()






def init():
    from system.core import symbol
    from system.evaluation import ResolveFrame
    import sys

    from system.reader import read_from_string
    from system.app_compiler import compile_in_module

    form = read_from_string("((fn baz [x y] (add x y)))")
    comped = compile_in_module(form, sys.modules["system.rt"])
    globals()["baz"] = comped()

    names = []
    values = []

    for k in globals():
        val = globals()[k]
        if isinstance(val, Object) and hasattr(val, "_symbol_"):
            names.append(symbol(None, val._symbol_))
            values.append(val)


    globals()["builtins"] = ResolveFrame(names, values)
