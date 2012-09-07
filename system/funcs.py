from system.core import Object
from system.jit import *

import system.treadle.treadle as tr
MAX_ARITY = 20

class AFn(Object):
    pass

class AFExpr(Object):
    pass


def gen_func(arity):
    """Generates an abstract function that takes a variable number of arguments
    via invoke_args and dispatches to invoke0, invoke1, etc."""

    self = tr.Argument("self")
    args_w = tr.Argument("args_w")

    def call_invoke(arity, self, args_w):
        args = []
        for x in range(arity):
            args.append(args_w.Subscript(tr.Const(x)))
        expr = self.Attr("invoke" + str(arity)) \
                   .Call(*args) \
                   .Return()
        ln = tr.Global("len").Call(args_w)
        cond = tr.If(tr.Equal(ln, tr.Const(arity)), expr)
        return cond

    blocks = []
    for x in range(arity):
        blocks.append(call_invoke(x, self, args_w))
    do = tr.Do(*blocks)
    invoke_args = tr.Func([self, args_w], do).toFunc(globals())

    class FuncBase(AFn):
        def type(self):
            import system.core
            return system.core.symbol("system", "Func")

    def gen_attr_error(arity):
        args = [tr.Argument("self")]
        for x in range(arity):
            args.append(tr.Argument("arg" + str(x)))
        fn = tr.Func(args, tr.Return(tr.Const(None))).toFunc()
        fn.__name__ = "invoke" + str(arity)
        return fn


    members = {"invoke_args": invoke_args}
    # pypy translator will complain without this:
    for x in range(arity):
        fn = gen_attr_error(x)
        members[fn.__name__] = fn

    return type("Func", (FuncBase,), members)

Func = gen_func(MAX_ARITY)


def gen_variadicfunc(arity):
    """Generates a type that has invoke0, invoke1, etc. that dispatch to invoke_args"""
    def gen_dispatch(arity):
        self = tr.Argument("self")
        arguments = []
        for x in range(arity):
            arguments.append(tr.Argument("arg" + str(x)))
        expr = self.Attr("invoke_args").Call(tr.List(*arguments))
        fn = tr.Func([self] + arguments, expr).toFunc()
        fn.__name__ = "invoke"+str(arity)
        return fn

    members = {}
    for x in range(arity):
        fn = gen_dispatch(x)
        members[fn.__name__] = fn

    class VariadicFuncBase(AFn):
        def type(self):
            import system.core
            return system.core.symbol("system", "Func")


    return type("VariadicFunc", (VariadicFuncBase,), members)



VariadicFunc = gen_variadicfunc(MAX_ARITY)

import system.core as core

def gen_polymorphicfunc(arity):
    """Generates a object that dispatches based on the first argument"""
    def gen_dispatch(arity):
        self = tr.Argument("self")
        arguments = []
        for x in range(arity):
            arguments.append(tr.Argument("arg" + str(x)))

        expr = self.Attr("get_override") \
                   .Call(tr.Global("core").Attr("type") \
                                          .Call(arguments[0])) \
                   .Attr("invoke"+str(arity)) \
                   .Call(*arguments)

        fn = tr.Func([self] + arguments, expr).toFunc(globals())
        fn.__name__ = "invoke"+str(arity)
        return fn

    @unroll_safe
    def get_override(overrides, tp, default):
        from system.bool import w_true, w_false
        from system.symbol import symbol_equals
        for x in range(0, len(overrides), 2):
            if symbol_equals(overrides[x], tp) is w_true:
                return overrides[x + 1]
        if default is not None:
            return default
        assert False, "no override for " + tp._name

    class PolymorphicBase(Func):
        def __init__(self, default = None, symbol = None):
            if symbol:
                self._symbol_ = symbol
            self._default = default
            self._overrides = []


        def get_override(self, tp):
            return promote(get_override(self._overrides, tp, self._default))

        def install(self, tp, func):
            assert isinstance(tp, Object)
            assert isinstance(func, Object)
            import copy
            self._overrides = self._overrides[:]
            self._overrides.extend([tp, func])

        def type(self):
            import system.core
            return system.core.symbol("system", "Func")

    members = {}
    for x in range(1, arity):
        fn = gen_dispatch(x)
        members[fn.__name__] = fn


    return type("PolymorphicFn", (PolymorphicBase, ), members)

PolymorphicFunc = gen_polymorphicfunc(MAX_ARITY)


class FExpr(Func):
    pass

class VariadicFExpr(VariadicFunc):
    pass



def gen_rest_fn(arity):
    class RestFnBase(Func):
        def __init__(self, arity):
            self._required_arity = arity
        def throw_arity(self, arity):
            raise TypeError, "bad arity. Expected " + str(arity)
        def bounded_length(self, s, max):
            i = 0
            while s is not None and i < max:
                i += 1
                s = next(s)
            return i

    def gen_dispatch_func(arity):
        self = tr.Argument("self")
        req_arity = self.Attr("_required_arity")
        args = map(lambda x: tr.Argument("arg" + str(x)), range(arity))
        ifs = []
        for x in range(arity):
            argexpr = args[:x]
            argexpr.append(tr.Global("list_from_pylist").Call(tr.List(*args[x:])))
            expr = req_arity.Equal(tr.Const(x)) \
                            .If(self.Attr("do_invoke").Call(*argexpr))
            ifs.append(expr)

        ifs.append(self.Attr("throw_arity").Call(tr.Const(arity)))
        return tr.Func([self] + args, tr.Do(*ifs)).toFunc(globals())

    def gen_do_invoke(arity):
        self = tr.Argument("self")
        args = [self] + map(lambda x: tr.Argument("arg" + str(x)), range(arity))

        body = tr.Const(None)
        return tr.Func(args, body).toFunc(globals())

    def gen_invoke_args(max_arity):
        self = tr.Argument("self")
        sargs = tr.Argument("sargs")
        arity = tr.Local("arity")
        bounded = self.Attr("bouned_length") \
                      .Call(sargs, self.Attr("_required_arity")) \
                      .LesserOrEqual(self.Attr("_required_arity")) \
                      .If(self.Attr("apply_to_helper") \
                              .Call(self, sargs) \
                              .Return())

        ifs = []
        ifs.append(bounded)

        locs = map(lambda x: tr.Argument("arg" + str(x)), range(max_arity))

        _first = tr.Global("first")
        _next = tr.Global("next")

        for x in range(max_arity):
            set_locs = []
            for sl in range(x):
                a = _first.Call(sargs).StoreToLocal(locs[sl])
                b = _next.Call(sargs).StoreToLocal(sargs)
                set_locs.extend([a, b])

            expr = self.Attr("do_invoke" + str(x)) \
                       .Call(*locs[:x] + [sargs]) \
                       .Return()
            print set_locs + [expr]
            do = tr.Do(*(set_locs + [expr]))
            ife = self.Attr("_required_arity") \
                      .Equal(tr.Const(x)) \
                      .If(do)

            ifs.append(ife)

        ifs.append(self.Attr("throw_arity").Call(tr.Const(-1)))
        return tr.Func([self, sargs], tr.Do(*ifs)).toFunc(globals())





    invokes = dict(map(lambda x: ("invoke"+str(x), gen_dispatch_func(x)), range(arity)))
    do_invokes = dict(map(lambda x: ("do_invoke"+str(x), gen_do_invoke(x)), range(arity)))
    invoke_args = gen_invoke_args(MAX_ARITY)
    members = dict(invokes.items() +  do_invokes.items())
    members["invoke_args"] = invoke_args
    return type("RestFn", (RestFnBase, ), members)


RestFN = gen_rest_fn(MAX_ARITY)
