from core import Object


class Func(Object):
    def invoke_args(self, w_args):
        if len(w_args) == 0:
            return self.invoke0()
        if len(w_args) == 1:
            return self.invoke1(w_args[0])
        if len(w_args) == 2:
            return self.invoke2(w_args[0], w_args[1])
    def invoke1(self, a):
        assert False

class FExpr(Object):
    def invoke_args(self, w_args):
        if len(w_args) == 0:
            return self.invoke0()
        if len(w_args) == 1:
            return self.invoke1(w_args[0])
        if len(w_args) == 2:
            return self.invoke2(w_args[0], w_args[1])

class VariadicFunc(Object):
    def invoke0(self):
        return self.invoke_args([])
    def invoke1(self, a):
        return self.invoke_args([a])
    def invoke2(self, a, b):
        return self.invoke_args([a, b])
    def invoke3(self, a, b, c):
        return self.invoke_args([a, b, c])

class VariadicFExpr(Object):
    def invoke0(self):
        return self.invoke_args([])
    def invoke1(self, a):
        return self.invoke_args([a])
    def invoke2(self, a, b):
        return self.invoke_args([a, b])
    def invoke3(self, a, b, c):
        return self.invoke_args([a, b, c])

import system.core as core

class PolymorphicFunc(Func):
    def __init__(self):
        self._overrides = {}

    def invoke1(self, a):
        tp = core.type(a)
        if tp not in self._overrides:
            assert False , "No override for " + tp.repr()
        return self._overrides[tp].invoke1(a)

    def invoke2(self, a, b):
        tp = core.type(a)
        if tp not in self._overrides:
            assert False , "No override for " + tp.repr()
        return self._overrides[tp].invoke2(a, b)

    def invoke3(self, a, b, c):
        tp = core.type(a)
        if tp not in self._overrides:
            assert False #, "No override for " + tp.repr()
        return self._overrides[tp].invoke3(a, b, c)

    def invoke4(self, a, b, c, d):
        tp = core.type(a)
        if tp not in self._overrides:
            assert False , "No override for " + tp.repr()
        return self._overrides[tp].invoke4(a, b, c, d)

    def install(self, tp, func):
        assert isinstance(tp, Object)
        assert isinstance(func, Object)
        self._overrides[tp] = func


def extend(func, tp):
    def inner(f):
        appfn = interp2app(f)
        func.install(tp, appfn)
        return appfn
    return inner



class Equal(Func):
    _symbol_ = "="
    def __init__(self):
        pass
    def invoke2(self, a, b):
        import bool
        if core.equal(a, b):
            return bool.w_true
        return bool.w_false

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
    def __init__(self, w_args, w_body):
        self._w_args = w_args
        self._w_body = w_body
    def invoke_args(self, args_w):
        assert len(self._w_args) == len(args_w)
        from system.evaluation import ResolveFrame, eval_item
        from system.bool import w_true
        frame = ResolveFrame(self._w_args, args_w)
        globals = ResolveFrame([], [])
        return eval_item.invoke4(self._w_body, globals, frame, w_true)

class Fn(VariadicFExpr):
    _symbol_ = "fn"
    def __init__(self):
        pass
    def invoke_args(self, args_w):
        from system.helpers import first, next
        args = []
        s = args_w[0]
        while s is not None:
            args.append(first(s))
            s = next(s)
        body = args_w[1]
        return FuncInstance(args, body)

fn = Fn()




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

hash_map = HashMap()


from system.util import interp2app
cons = interp2app(lambda a, b: _cons.invoke2(b, a), "cons")

assoc = interp2app(lambda a, b, c: _assoc.invoke3(a, b, c), "assoc")

add = interp2app(lambda a, b: _add.invoke2(a, b), "+")

repr = PolymorphicFunc()
eval = PolymorphicFunc()
first = PolymorphicFunc()
next = PolymorphicFunc()
count = PolymorphicFunc()
_cons = PolymorphicFunc()
_assoc = PolymorphicFunc()
_get = PolymorphicFunc()
equals = PolymorphicFunc()
_equals = PolymorphicFunc()
_add = PolymorphicFunc()






def init():
    from system.core import symbol
    from system.evaluation import ResolveFrame

    names = []
    values = []

    for k in globals():
        val = globals()[k]
        if isinstance(val, Object) and hasattr(val, "_symbol_"):
            names.append(symbol(None, val._symbol_))
            values.append(val)


    globals()["builtins"] = ResolveFrame(names, values)

