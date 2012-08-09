from system.consts import *


class AExpression(object):
    def toFunction(self):
        from interpreter import Function

        expr = self
        if not isinstance(expr, Func):
            expr = Func([], self)



        argnames = map(lambda x: x._name, expr._args)

        ctx = Context()

        expr._body.emit(ctx)

        consts = [None] * len(ctx._consts)
        for k in ctx._consts:
            consts[ctx._consts[k]] = k._value

        bcode = ''.join(ctx._bcode)
        func = Function(bcode, argnames, consts)

        return func



class Context(object):
    def __init__(self):
        self._bcode = []
        self._consts = {}






class Argument(AExpression):
    def __init__(self, name):
        self._name = name

    def tag(self, idx):
        self._idx = idx

    def emit(self, ctx):
        ctx._bcode.append(chr(LOAD_ARG))
        ctx._bcode.append(chr(self._idx))

class Const(AExpression):
    def __init__(self, val):
        self._value = val

    def emit(self, ctx):
        if self not in ctx._consts:
            ctx._consts[self] = len(ctx._consts)

        ctx._bcode.append(chr(LOAD_CONST))
        ctx._bcode.append(chr(ctx._consts[self]))





class Func(AExpression):
    def __init__(self, args, body):
        for x in range(len(args)):
            args[x].tag(x)
        self._args = args
        self._body = body
        self._value = None

    def emit(self, ctx):
        if self._value is None:
            self._value = Const(self.toFunction())

        self._value.emit(ctx)

class BinaryOp(AExpression):
    def __init__(self, op, a, b):
        self._a = a
        self._b = b
        self._op = op

    def emit(self, ctx):
        self._b.emit(ctx)
        self._a.emit(ctx)
        ctx._bcode.append(chr(self._op))

class Add(BinaryOp):
    def __init__(self, a, b):
        BinaryOp.__init__(self, BINARY_ADD, a, b)

class Subtract(BinaryOp):
    def __init__(self, a, b):
        BinaryOp.__init__(self, BINARY_SUB, a, b)
