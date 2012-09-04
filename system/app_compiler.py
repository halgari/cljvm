

# This is a compiler from vetalis lisp code to rpython
import system.treadle.treadle as tr
from system.bool import w_true, w_false
from system.integer import W_Integer
from system.core import Object, symbol, integer
from system.funcs import *
from system.helpers import *
from system.persistent_list import from_pylist as pylist_to_list, PersistentList
from system.symbol import W_Symbol

import copy

def compile_impl(name, argsv, body, env):
    methname = "invoke" + str(count(argsv).int())
    self = tr.Argument("self")
    args = {symbol(methname): self}
    trarg = [self]
    for x in range(count(argsv).int()):
        s = nth(argsv, integer(x))
        args[s] = tr.Argument(s.repr())
        trarg.append(args[s])

    with merge_locals(env, args):
        expr = tr.Func(trarg, compile_do(body, env))
        return [tr.Const(methname), expr]

def compile_do(forms, env):
    s = forms
    out = []
    while s is not None:
        out.append(compile(first(s), env))
        s = next(s)
    return tr.Do(*out)

def compile_impls(name, impls, env):
    s = impls
    meths = []
    while s is not None:
        meths.extend(compile_impl(name, first(first(s)), next(first(s)), env))

        s = next(s)

    meths = tr.Dict(*meths)

    return meths.Class(tr.Const(Func).Tuple(), tr.Const(name._name))

def compile_fn(form, env):
    name = first(form)
    s = form
    if isvector(first(s)) is w_true:
        impls = pylist_to_list([s])
    else:
        impls = s

    return compile_impls(name, impls, env)


class Ctx(object):
    def __init__(self):
        self._locals = {}

def compile_symbol(sym, env):
    if sym in env._locals:
        return env._locals[sym]
    return tr.Global(sym._name)

def compile_invoke(form, env):
    fn = first(form)
    if isinstance(fn, W_Symbol):
        if fn in dispatchers:
            return dispatchers[fn](next(form), env)
    fn = compile(fn, env)
    args = []
    s = next(form)
    while s is not None:
        args.append(compile(first(s), env))
        s = next(s)
    return fn.Call(*args)




def compile(form, env):
    if isinstance(form, W_Integer):
        return tr.Const(form.int())
    if isinstance(form, W_Symbol):
        return compile_symbol(form, env)
    if isinstance(form, PersistentList):
        return compile_invoke(form, env)

def compile_in_module(form, module):
    a = []
    s = form
    while s is not None:
        a.append(compile(first(s), Ctx()))
        s = next(s)

    return tr.Do(*a).toFunc()



class merge_locals(object):
    def __init__(self, ctx, locals = {}):
        self._ctx = ctx
        self._locals = locals
    def __enter__(self):
        import copy
        self._old = copy.copy(self._ctx._locals)
        for x in self._locals:
            self._ctx._locals[x] = self._locals[x]
    def __exit__(self, type, value, tb):
        self._ctx._locals = self._old


def merge(d1, d2):
    d1 = copy.copy(d1)
    for x in d2:
        d1[x] = d2[x]
    return d1

dispatchers = {symbol("fn") : compile_fn}
