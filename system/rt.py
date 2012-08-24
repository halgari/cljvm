from core import Object


class Func(Object):
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


class HashMap(VariadicFunc):
    _symbol_ = "list"
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


from system.polymorphic_func import PolymorphicFunc
repr = PolymorphicFunc()
eval = PolymorphicFunc()
first = PolymorphicFunc()
next = PolymorphicFunc()
count = PolymorphicFunc()
_cons = PolymorphicFunc()
_assoc = PolymorphicFunc()
_get = PolymorphicFunc()
