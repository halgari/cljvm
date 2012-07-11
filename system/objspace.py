import clojure.core

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

class W_Int(Object):
    def __init__(self, v):
        self.int_value = v

    def getIntValue(self):
        return self.int_value

    def getType(self):
        return Integer

    def toString(self):
        return str(self.int_value)

def s_unwrap_int(w_int):
    return w_int.getIntValue()



def invoke0(w_fn, arg1):
    return w_fn.invoke0()

def invoke1(w_fn, arg1):
    return w_fn.invoke1(arg1)

def invoke_args(w_fn, args_w):
    if len(args_w) == 0:
        return invoke0(w_fn)
    if len(args_w) == 1:
        return invoke1(w_fn, args_w[0])



