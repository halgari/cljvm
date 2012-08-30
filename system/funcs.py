from system.core import Object
import system.treadle.treadle as tr
MAX_ARITY = 20

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
                   .Call(*args)
        ln = tr.Global("len").Call(args_w)
        cond = tr.Return(tr.If(tr.Equal(ln, tr.Const(arity)), expr))
        return cond

    blocks = []
    for x in range(arity):
        blocks.append(call_invoke(x, self, args_w))
    do = tr.Do(*blocks)
    invoke_args = tr.Func([self, args_w], do).toFunc()

    class FuncBase(Object):
        def type(self):
            import system.core
            return system.core.symbol("system", "Func")

    return type("Func", (FuncBase,), {"invoke_args": invoke_args})

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

    class VariadicFuncBase(Object):
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

        expr = self.Attr("_overrides") \
                   .Subscript(tr.Global("core").Attr("type") \
                                               .Call(arguments[0])) \
                   .Attr("invoke"+str(arity)) \
                   .Call(*arguments)

        fn = tr.Func([self] + arguments, expr).toFunc(globals())
        fn.__name__ = "invoke"+str(arity)
        return fn

    class PolymorphicBase(Func):
        def __init__(self, default = None):
            self._default = default
            self._overrides = {}
        def install(self, tp, func):
            assert isinstance(tp, Object)
            assert isinstance(func, Object)
            self._overrides[tp] = func
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
