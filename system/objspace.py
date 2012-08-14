import doctest
from pypy.rlib.jit import elidable

types = {}
protofns = {}


class Object(object):
    pass

class TypeDef(Object):
    def __init__(self, name, fields):
        self.fields = list(fields)

    def getFieldOffset(self, fname):
        for x in range(len(self.fields)):
            if self.fields[x] == fname:
                return x
        assert False


class PersistentObject(Object):
    __immutable_fields_ = ["_tdef", "_data"]
    def __init__(self, tdef, data):
        self._tdef = tdef
        self._data = data

    def getField(self, name):
        off = self._tdef.getFieldOffset(name)
        return self._data[off]

    def withField(self, name, newval):
        off = self._tdef.getFieldOffset(name)
        newdat = self._data[:]
        newdat[off] = newval
        return PersistentObject(self._tdef, newdat)

    def getType(self):
        return self._tdef







def typedef(fn):
    name = fn.func_name
    fields = fn.func_code.co_varnames[:fn.func_code.co_argcount]

    types[name] = TypeDef(name, fields)
    print("Registered Type " + name)
    return fn


def s_type(obj):
    assert obj is not None
    return obj.getType()

def s_fget(obj, name):
    return obj.getField(name)

def s_with(obj, name, val):
    return obj.withField(name, val)

def s_wrap_func(fn):
    from system.functions import WrappedFn
    return WrappedFn(fn, None)

class extend(object):
    def __init__(self, tp, proto):
        self._tp = tp
        self._proto = proto

    def __call__(self, fn):
        from system.functions import PolymorphicFn
        w_func = s_wrap_func(fn)
        name = fn.func_name

        if name not in protofns:
            pfn = PolymorphicFn(name)
            protofns[name] = pfn
            setattr(clojure.core, name, pfn)

        protofns[name].extend(types[self._tp.func_name], w_func)

        print "Registered " + self._proto + " : " + name

        return fn


Integer = TypeDef("Integer", [])
NilType = TypeDef("NilType", [])
BoolType = TypeDef("BoolType", [])

class W_Int(Object):
    _immutable_fields_ = ['int_value']
    def __init__(self, v):
        self.int_value = v

    def getIntValue(self):
        return self.int_value

    def getType(self):
        return Integer

    def toString(self):
        return str(self.int_value)

class W_Bool(Object):
    def __init__(self, v):
        self.bool_value = v

#    @elidable
    def getBoolValue(self):
        return self.bool_value

#    @elidable
    def getType(self):
        return BoolType

#    @elidable
    def toString(self):
        return "true" if self.bool_value else "false"

class W_Nil(Object):
    def __init__(self):
        pass

    def getType(self):
        return NilType

    def getString(self):
        return "nil"

nil = W_Nil()

InternalListType = TypeDef("InternalList", [])

class W_InternalList(Object):
    _immutable_fields_ = ['_w_head', '_w_tail']
#    @elidable
    def __init__(self, w_head, w_tail):
        self._w_head = w_head
        self._w_tail = w_tail

    @elidable
    def getFirst(self):
        return self._w_head

    @elidable
    def getNext(self):
        return self._w_tail

    def getType(self):
        return InternalListType

ArrayType = TypeDef("Array", [])

class W_Array(Object):
    def __init__(self, items_w):
        self._items_w = items_w

    @elidable
    def getNth(self, w_nth):
        return self._items_w[s_unwrap_int(w_nth)]

    @elidable
    def getNthInterp(self, nth):
        return self._items_w[nth]

    @elidable
    def getCount(self):
        return W_Int(len(self._items_w))

    @elidable
    def getType(self):
        return ArrayType



def s_cons(newhead, rest):
    return W_InternalList(newhead, rest)

w_true = W_Bool(True)
w_false = W_Bool(False)


def s_unwrap_int(w_int):
    """
    Returns a unwrapped (unboxed) int

    >>> s_unwrap_int(W_Int(42))
    42
    """
    return w_int.getIntValue()

def s_unwrap_bool(w_bool):
    """
    Returns a unwrapped bool

    >>> s_unwrap_bool(w_true)
    True
    >>> s_unwrap_bool(w_false)
    False
    """
    return w_bool.getBoolValue()

def s_add(w_arg1, w_arg2):
    """
    >>> s_unwrap_int(s_add(W_Int(21), W_Int(21)))
    42
    """
    return W_Int(s_unwrap_int(w_arg1) + s_unwrap_int(w_arg2))

def s_sub(w_arg1, w_arg2):
    """
    >>> s_unwrap_int(s_sub(W_Int(21), W_Int(21)))
    0
    """
    return W_Int(s_unwrap_int(w_arg1) - s_unwrap_int(w_arg2))

def s_eq(w_arg1, w_arg2):
    """
    >>> s_unwrap_bool(s_eq(W_Int(42), W_Int(42)))
    True
    >>> s_unwrap_bool(s_eq(W_Int(42), W_Int(41)))
    False
    """
    return w_true if s_unwrap_int(w_arg1) == s_unwrap_int(w_arg2) else w_false


def invoke0(w_fn, arg1):
    return w_fn.invoke0()

def invoke1(w_fn, arg1):
    return w_fn.invoke1(arg1)

def invoke_args(w_fn, args_w):
    if len(args_w) == 0:
        return invoke0(w_fn)
    if len(args_w) == 1:
        return invoke1(w_fn, args_w[0])



