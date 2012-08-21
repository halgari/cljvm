import doctest
from system.jit import *

types = {}
protofns = {}


def get_location(func):
    #if form is nil or form is None:
    #    return "nil"
    return func.repr()

jitdriver = JitDriver(greens=['func'],
    reds=['args', 'frame'],
    virtualizables=['frame'],
    get_printable_location = get_location
)


class Object(object):
    _immutable_fields_ = ['_w_head', '_w_tail', 'int_value', '_name', 'bool_value']
    pass


# class ResolveFrame(object):
    # _virtualizable2_ = ['_dict_w[*]']
    # def __init__(self, dict_w, prev = None):
        # self._dict_w = dict_w
        # self._prev = prev

    # @elidable
    # def resolve(self, sym):
        # if sym in self._dict_w:
            # return self._dict_w[sym]
        # if self._prev:
            # return self._prev.resolve(sym)
        # else:
            # return unknown

class FExpr(Object):
    """ An expression who's arguments are not evaluated """
    def apply_fexpr(self, frame, args_w, can_tail_call):
        return nil

class Expr(Object):
    """ An expression who's arguments are evaluated"""
    def apply_to(self, args_w, can_tail_call):
        return nil

class IfExpr(FExpr):
    def apply_fexpr(self, frame, args_w, can_tail_call):
        cond = args_w[0]

        if cond.eval(frame, False) is w_true:
            return args_w[1].eval(frame, can_tail_call)
        elif len(args_w) == 3:
            return args_w[2].eval(frame, can_tail_call)
        else:
            return nil

class Equals(Expr):
    def apply_to(self, args_w, can_tail_call):
        fst = args_w[0]
        for x in range(1, len(args_w)):
            if s_eq(fst, args_w[x]) is w_false:
                return w_false
        return w_true

class Add(Expr):
    def apply_to(self, args_w, can_tail_call):
        accum = W_Int(0)
        for x in range(0, len(args_w)):
            accum = s_add(accum, args_w[x])
        return accum

class W_Unknown(Object):
    def __init__(self):
        pass

class W_Trampoline(Object):
    def __init__(self, func_w, args_w):
        self._func_w = func_w
        self._args_w = args_w
    def repr(self):
        return "W_Trampoline(" + self._func_w.repr() + ")"

    def apply(self):
        return self._func_w.apply_to(self._args_w, True)

    def set(self, func_w, args_w):
        self._func_w = func_w
        self._args_w = args_w
        return self

def interpret_seq(frame, sym, args_w, can_tail_call):
    if sym is sym_if:
        return interpret_if(frame, args_w, can_tail_call)



unknown = W_Unknown()

class SelfEvaluating(Object):
    """Defines a object that evals to itself"""
    def eval(self, frame, can_tail_call):
        return self

class Symbol(Object):
    def __init__(self, name):
        self._name = name

    def eval(self, frame, can_tail_call):
        if frame is not noframe:
            if frame._self_name_w is self:
                return frame._self_w
            idx = promote(get_arg_idx(frame._arg_names_w, self))
            if idx != -1:
                return frame._args_w[idx]
        return get_builtin(self)

    def repr(self):
        return self._name

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        if self._name == other._name:
            return True
        return False


class SymbolCache(object):
    def __init__(self):
        self._cache = {}

    def intern(self, s):
        if s in self._cache:
            return self._cache[s]

        sym = Symbol(s)
        self._cache[s] = sym

        return sym

_sym_cache = SymbolCache()

def symbol(s):
    return _sym_cache.intern(s)




sym_if = Symbol("if")
sym_fn = Symbol("fn")

class W_Int(SelfEvaluating):
    def __init__(self, v):
        self.int_value = v

    @elidable
    def int(self):
        return self.int_value

    def repr(self):
        return str(self.int())

    def string(self):
        return str(self.int_value)

class W_Bool(SelfEvaluating):
    def __init__(self, v):
        self.bool_value = v

    def bool(self):
        return self.bool_value

    def repr(self):
        return self.string()

    def string(self):
        return "true" if self.bool_value else "false"

class W_Nil(Object):
    def __init__(self):
        pass

    def to_string(self):
        return "nil"

nil = W_Nil()

class W_Cons(Object):
    _immutable_fields_ = ['_w_head', '_w_tail']
    def __init__(self, w_head, w_tail):
        self._w_head = w_head
        self._w_tail = w_tail


    def first(self):
        return self._w_head

    def next(self):
        return self._w_tail

    @elidable
    def count(self):
        i = 0
        s = self
        while s is not nil and s is not None:
            i += 1
            s = s.next()
        return i

    def repr(self):
        s = self
        v = []
        while s is not None and s is not nil:
            v.append(s.first().repr())
            s = s.next()

        return "(" + " ".join(v) + ")"

    def list(self):
        s = self
        cnt = self.count()
        l = [None] * cnt
        for x in range(cnt):
            l[x] = s.first()
            s = s.next()
        return l


    @unroll_safe
    def eval(self, frame, can_tail_call):
        fn = promote(self.first()).eval(frame, False)
        argc = promote(self.count() - 1)
        args_w = [None] * argc
        s = self.next()
        for x in range(argc):
            if isinstance(fn, Expr):
                args_w[x] = promote(s._w_head).eval(frame, False)
            elif isinstance(fn, FExpr):
                args_w[x] = promote(s._w_head)
            s = promote(s._w_tail)

        if can_tail_call and not isinstance(fn, FExpr):
            return trampoline.set(fn, args_w)
        else:
            if isinstance(fn, FExpr):
                return fn.apply_fexpr(frame, args_w, can_tail_call)
        return fn.apply_to(args_w, can_tail_call)


class W_Array(Object):
    def __init__(self, items_w):
        self._items_w = items_w

    def app_nth(self, w_nth):
        return self._items_w[s_unwrap_int(w_nth)]

    def nth(self, nth):
        return self._items_w[nth]

    def count(self):
        return W_Int(len(self._items_w))

    def list(self):
        return self._items_w


def s_cons(newhead, rest):
    return W_Cons(newhead, rest)

w_true = W_Bool(True)
w_false = W_Bool(False)


def s_unwrap_int(w_int):
    """
    Returns a unwrapped (unboxed) int

    >>> s_unwrap_int(W_Int(42))
    42
    """
    return w_int.int()

def s_unwrap_bool(w_bool):
    """
    Returns a unwrapped bool

    >>> s_unwrap_bool(w_true)
    True
    >>> s_unwrap_bool(w_false)
    False
    """
    return w_bool.bool()

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

@elidable
def get_arg_idx(arg_names_w, sym):
    for x in range(len(arg_names_w)):
        if arg_names_w[x] is sym:
            return x
    return -1

class FuncResolveFrame(object):
    _virtualizable2_ = ['_args_w', '_arg_names_w', '_self_w', '_self_name_w']
    def __init__(self, _self_name_w, _self_w, _arg_names_w, _args_w):
        self._arg_names_w = _arg_names_w
        self._args_w = _args_w
        self._self_w = _self_w
        self._self_name_w = _self_name_w

class FuncInstance(Expr):
    def __init__(self, name, args, body):
        self._name = name
        self._args_w = args.list()
        self._body = body


    def repr(self):
        return "FuncInstance(" + self._name.repr() + ")"

    def apply_to(self, args_w, can_tail_call):
        assert len(args_w) == len(self._args_w)

        frame = FuncResolveFrame(self._name, self, self._args_w, args_w)

        jitdriver.jit_merge_point(func = self,
            args = args_w,
            frame = frame)
        ret = nil
        return self._body[0].eval(frame, True)

class Func(FExpr):
    def __init__(self):
        pass
    def apply_fexpr(self, frame, args_w, can_tail_call):
        nm = args_w[0]
        args = args_w[1]
        body = args_w[2:]

        return FuncInstance(nm, args, body)

class Equals(Expr):
    def apply_to(self, args_w, can_tail_call):
        return s_eq(args_w[0], args_w[1])

def make_list(*args):
    s = nil
    argsl = list(args)
    for x in range(len(argsl) -1, -1, -1):
        s = s_cons(argsl[x], s)
    return s

@elidable
def get_builtin(sym):
    if sym in builtins:
        return builtins[sym]
    return unknown

builtins = {symbol("if"): IfExpr(),
            symbol("+"): Add(),
            symbol("fn"): Func(),
            symbol("="): Equals()}

noframe = FuncResolveFrame(None, None, None, [])
trampoline = W_Trampoline(None, None)

def eval(form_w, env_w = None):
    env_w = noframe
    res = form_w.eval(env_w, True)

    while isinstance(res, W_Trampoline):
        res = res.apply()

    return res
