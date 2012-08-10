from system.consts import *


class AExpression(object):
    def toFunction(self):
        from interpreter import Function

        expr = self
        if not isinstance(expr, Func):
            expr = Func([], self)


        argnames = []
        for x in expr._args:
            argnames.append(x._name)

        ctx = Context()

        expr._body.emit(ctx, True)

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

    def emit(self, ctx, tc):
        ctx._bcode.append(chr(LOAD_ARG))
        ctx._bcode.append(chr(self._idx))

class Const(AExpression):
    def __init__(self, val):
        self._value = val

    def emit(self, ctx, tc):
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

    def emit(self, ctx, tc):
        if self._value is None:
            self._value = Const(self.toFunction())

        self._value.emit(ctx, tc)

class BinaryOp(AExpression):
    def __init__(self, op, a, b):
        self._a = a
        self._b = b
        self._op = op

    def emit(self, ctx, tc):
        self._b.emit(ctx, False)
        self._a.emit(ctx, False)
        ctx._bcode.append(chr(self._op))
        
class Call(AExpression):
    def __init__(self, fn, *args):
        self._args = list(args)
        self._fn = fn
    
    def emit(self, ctx, tc):
        for x in self._args:
            x.emit(ctx, False)
        self._fn.emit(ctx, False)
        ctx._bcode.append(chr(TAIL_CALL if tc else CALL_FUNCTION))
        ctx._bcode.append(chr(len(self._args)))



class Add(BinaryOp):
    def __init__(self, a, b):
        BinaryOp.__init__(self, BINARY_ADD, a, b)

class Subtract(BinaryOp):
    def __init__(self, a, b):
        BinaryOp.__init__(self, BINARY_SUB, a, b)

class Equal(BinaryOp):
    def __init__(self, a, b):
        BinaryOp.__init__(self, IS_EQ, a, b)

class CurFunc(AExpression):
    def __init__(self):
        pass
    def emit(self, ctx, tc):
        ctx._bcode.append(chr(CUR_FUNC))


class If(AExpression):
    def __init__(self, cond, then, elsethen):
        self._cond = cond
        self._then = then
        self._else = elsethen

    def emit(self, ctx, tc):
        self._cond.emit(ctx, False)
        org_bcode = ctx._bcode
        ctx._bcode = []

        self._then.emit(ctx, tc)

        then_bcode = ctx._bcode
        ctx._bcode = []

        self._else.emit(ctx, tc)

        else_bcode = ctx._bcode

        ctx._bcode = org_bcode

        ctx._bcode.append(chr(JUMP_IF_FALSE))
        ctx._bcode.append(chr(len(then_bcode) + 2))
        ctx._bcode.extend(then_bcode)
        ctx._bcode.append(chr(JUMP))
        ctx._bcode.append(chr(len(else_bcode)))
        ctx._bcode.extend(else_bcode)

