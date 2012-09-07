import dis
import types
import struct

from treadle_exceptions import *
from compat import version, newCode, SEEK_END, CondJump, AbsoluteJump

from copy import copy

from io import BytesIO



for x in dis.opmap:
    globals()[x] = dis.opmap[x]





class AExpression(object):
    """defines a abstract expression subclass this to create new expressions"""
    def __init__(self):
        pass

    def toCode(self):
        print "----"
        expr = self

        locals = {}
        argcount = 0

        print repr(self)


        co_flags = 0
        if isinstance(self, Func):
            expr = self.expr

            for x in self.args:
                locals[x] = len(locals)

            argcount = len(self.args)
            co_flags = self.flags

            if co_flags & CO_VARARGS:
                argcount -= 1  # VARARGS don't count as args...strange


        if not isinstance(expr, Return):
            expr = Return(expr)



        size, max_seen = expr.size(0, 0)

        recurlocals = reversed(range(len(locals)))

        rp = RecurPoint(0, recurlocals, None)
        ctx = Context(rp, locals)


        expr.emit(ctx)

        code = ctx.stream.getvalue()
        if size != 1:
            raise UnbalancedStackException("Unbalanced stack " + str(size))

        consts = [None] * (len(ctx.consts) + 1)
        for k, v in list(ctx.consts.items()):
            consts[v + 1] = k.getConst()
        consts = tuple(consts)

        varnames = [None] * (len(ctx.varnames))
        for k, v in list(ctx.varnames.items()):
            varnames[v] = k.name
        varnames = tuple(varnames)

        names = [None] * (len(ctx.names))
        for k, v in list(ctx.names.items()):
            names[v] = k
        names = tuple(names)



        freevars = []
        idx = len(ctx.freevars)
        for x in ctx.freevars:
            x.markIdx(idx, ctx)
            freevars.append(x.name)
        freevars = tuple(freevars)


        if freevars or ctx.cellvars:
            co_flags ^= CO_NOFREE
        print freevars, "freevars", ctx.cellvars, "cellvars"
        c = newCode(co_code = code, co_stacksize = max_seen, co_consts = consts, co_varnames = varnames,
                    co_argcount = argcount, co_nlocals = len(varnames), co_names = names, co_flags = co_flags,
                    co_freevars = freevars, co_cellvars = tuple(ctx.cellvars))
        import dis
        dis.dis(c)
        print("---")
        return c

    def toFunc(self, globals = None):
        if globals is None:
            globals = {}
        c = self.toCode()
        return types.FunctionType(c, globals)

    def __getattr__(self, name):
        """Map in every class in this module as a constructor so we can provide
        it as a fluent interface"""
        if name not in globals():
            raise AttributeError("Can't find " + name + " on " + str(self))

        c = globals()[name]

        if type(c) != type:
            raise AttributeError("Can't find " + name + " on " + str(self))

        def consFunc(*args):
            return c(self, *args)

        return consFunc

    def __iter__(self):
        raise StopIteration()




def markupClosures(ctx, expr):
    closures = filter(lambda x: isinstance(x, Closure), flatten(iter, expr))
    cellvars = sorted(filter(lambda x:  isinstance(x, Closure), closures))
    freevars = []

    closures = list(cellvars + freevars)

    for idx in range(len(closures)):
        closures[idx].markIdx(idx)

    return closures

def assertExpression(expr):
    if not isinstance(expr, AExpression):
        raise ExpressionRequiredException("Expected AExpression, got " + str(type(expr)));

def assertAllExpressions(exprs):
    for x in exprs:
        assertExpression(x)

class IAssignable(object):
    """defines an expression that can be on the left side of an assign expression"""


class Return(AExpression):
    """defines an explicit 'return' in the code """
    def __init__(self, expr):
        if not isinstance(expr, AExpression):
            raise ExpressionRequiredException()

        self.expr = expr

    def emit(self, ctx):
        self.expr.emit(ctx)

        data = struct.pack("=B", RETURN_VALUE)
        ctx.stream.write(data)

    def size(self, current, max_seen):
        current, max_seen = self.expr.size(current, max_seen)
        return current, max_seen

    def __repr__(self):
        return "Return(" + repr(self.expr) + ")"

    def __iter__(self):
        yield self.expr

valid_const_types = {str, int, float, bool, type(None), type(type), types.CodeType, unicode}

class Const(AExpression):
    """defines a constant that will generate a LOAD_CONST bytecode. Note: Const objects
       do no intern their constants, that is left to the language implementors"""
    def __init__(self, const):
        if type(const) not in valid_const_types:
            raise Exception("Only marshallable types allowed as Consts, got: " + str(const) + str(type(const)))
        if isinstance(const, AExpression):
            raise ExpressionNotAllowedException()

        self.value = const

    def emit(self, ctx):
        # find a location for the const
        if self not in ctx.consts:
            ctx.consts[self] = len(ctx.consts)
        idx = len(ctx.consts)

        data = struct.pack("=BH", LOAD_CONST, idx)
        ctx.stream.write(data)

    def getConst(self):
        return self.value

    def size(self, current, max_seen):
        current += 1
        return current, max(current, max_seen)

    def __repr__(self):
        return "Const(" + repr(self.value) + ": " + repr(type(self.value).__name__) + ")"

    def __iter__(self):
        raise StopIteration()

class StoreLocal(AExpression):
    def __init__(self, local, expr):
        assertAllExpressions([local, expr])

        self.local = local
        self.expr = expr
    def size(self, current, max_seen):
        current, max_seen = self.expr.size(current, max_seen)

        return current, max(max_seen, current + 1)

    def emit(self, ctx):
        if self.local not in ctx.varnames:
            ctx.varnames[self.local] = len(ctx.varnames)

        idx = ctx.varnames[self.local]

        self.expr.emit(ctx)

        ctx.stream.write(struct.pack("=BBH", DUP_TOP, STORE_FAST, idx))

    def __iter__(self):
        yield self.local
        yield self.expr


class StoreToLocal(AExpression):
    def __init__(self, expr, local):
        assertAllExpressions([local, expr])

        self.local = local
        self.expr = expr
    def size(self, current, max_seen):
        current, max_seen = self.expr.size(current, max_seen)

        return current, max(max_seen, current + 1)

    def emit(self, ctx):
        if self.local not in ctx.varnames:
            ctx.varnames[self.local] = len(ctx.varnames)

        idx = ctx.varnames[self.local]

        self.expr.emit(ctx)

        ctx.stream.write(struct.pack("=BBH", DUP_TOP, STORE_FAST, idx))

    def __iter__(self):
        yield self.local
        yield self.expr

class StoreToGlobal(AExpression):
    def __init__(self, expr, local):
        assertAllExpressions([local, expr])

        self.local = local
        self.expr = expr
    def size(self, current, max_seen):
        current, max_seen = self.expr.size(current, max_seen)

        return current, max(max_seen, current + 1)

    def emit(self, ctx):
        if self.local not in ctx.varnames:
            ctx.varnames[self.local] = len(ctx.varnames)

        idx = ctx.varnames[self.local]

        self.expr.emit(ctx)

        ctx.stream.write(struct.pack("=BBH", DUP_TOP, STORE_GLOBAL, idx))


class If(AExpression):
    def __init__(self, condition, thenexpr, elseexpr = None):
        if elseexpr == None:
            elseexpr = Const(None)

        self.exprs = [condition, thenexpr, elseexpr]

        for x in self.exprs:
            if not isinstance(x, AExpression):
                raise ExpressionRequiredException()

        self.condition = condition
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def size(self, current, max_seen):
        for x in self.exprs:
            _ , new_max = x.size(current, max_seen)
            max_seen = max(max_seen, new_max)

        return current + 1, max_seen

    def emit(self, ctx):
        self.condition.emit(ctx)

        elsejump = CondJump(ctx)



        self.thenexpr.emit(ctx)

        endofif = AbsoluteJump(ctx)

        elsejump.mark()

        self.elseexpr.emit(ctx)

        endofif.mark()

    def __iter__(self):
        yield self.condition
        yield self.thenexpr
        yield self.elseexpr

    def __repr__(self):
        return "(If " + " ".join(map(repr, [self.condition, self.thenexpr, \
                                                self.elseexpr])) + " )"


class ABinaryOp(AExpression):
    def __init__(self, a, b, op):
        self.a = a
        self.b = b
        self.op = op

    def size(self, current, max_seen):
        current, max_seen = self.a.size(current, max_seen)
        current, max_seen = self.b.size(current, max_seen)


        return current - 1, max_seen

    def emit(self, ctx):
        self.a.emit(ctx)
        self.b.emit(ctx)
        ctx.stream.write(struct.pack("=B", self.op))

    def __iter__(self):
        yield self.a
        yield self.b



class Slice1(ABinaryOp):
    def __init__(self, a, b):
        ABinaryOp.__init__(self, a, b, globals()["SLICE+1"])

class Subscript(ABinaryOp):
    def __init__(self, a, b):
        ABinaryOp.__init__(self, a, b, BINARY_SUBSCR)

class And(ABinaryOp):
    def __init__(self, a, b):
        ABinaryOp.__init__(self, a, b, BINARY_AND)

class Subtract(ABinaryOp):
    def __init__(self, a, b):
        ABinaryOp.__init__(self, a, b, BINARY_SUBTRACT)



class Do(AExpression):
    def __init__(self, *exprs):
        if not exprs:
            exprs = [Const(None)]

        for x in exprs:
            if not isinstance(x, AExpression):
                raise ExpressionRequiredException()
        self.exprs = exprs

    def size(self, current, max_seen):
        last = self.exprs[-1]
        for x in self.exprs:
            current, max_seen = x.size(current, max_seen)
            if last is not x:
                current -= 1

        return current, max_seen

    def emit(self, ctx):
        last = self.exprs[-1]
        for x in self.exprs:
            x.emit(ctx)
            if last is not x:
                ctx.stream.write(struct.pack("=B", POP_TOP))

    def __repr__(self):
        return "Do(" + ", ".join(map(repr, self.exprs)) + ")"

    def __iter__(self):
        for x in self.exprs:
            yield x

class Class(AExpression):
    def __init__(self, methods, inherits, name):
        self.name = name
        self.inherits = inherits
        self.methods = methods

    def size(self, current, max_count):
        current, max_count = self.name.size(current, max_count)
        current, max_count = self.inherits.size(current, max_count)
        current, max_count = self.inherits.size(current, max_count)
        return current - 2, max_count

    def emit(self, ctx):
        self.name.emit(ctx)
        self.inherits.emit(ctx)
        self.methods.emit(ctx)

        ctx.stream.write(struct.pack("=B", BUILD_CLASS))

class Local(AExpression, IAssignable):
    def __init__(self, name):
        assert isinstance(name, (str, unicode))
        self.name = name

    def size(self, current, max_count):
        current += 1
        return current, max(current, max_count)

    def emit(self, ctx):
        if self not in ctx.varnames:
            ctx.varnames[self] = len(ctx.varnames)

        idx = ctx.varnames[self]

        ctx.stream.write(struct.pack("=BH", LOAD_FAST, idx))

    def __repr__(self):
        return self.name

    def __iter__(self):
        raise StopIteration()

class Closure(Local, IAssignable):
    def __init__(self, name, src):
        assertExpression(src)
        self.name = name
        self.src = src
        self.locs = []

    def markIdx(self, idx, ctx):
        for x in self.locs:
            ctx.stream.seek(x)
            ctx.stream.write(struct.pack("=BH", LOAD_DEREF, idx))
        ctx.stream.seek(0, SEEK_END)



    def emit(self, ctx):
        self.locs.append(ctx.stream.tell())
        ctx.stream.write(struct.pack("=BH", LOAD_DEREF, 0))
        ctx.freevars[self] = self


    def emitPreamble(self, ctx):
        self.src.emit(ctx)

    def __repr__(self):
        return "Closure(" + repr(self.src) + ", " + self.name + ")"

class Global(AExpression):
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name

    def size(self, current, max_count):
        current += 1
        return current, max(current, max_count)

    def emit(self, ctx):
        if self.name not in ctx.names:
            ctx.names[self.name] = len(ctx.names)

        idx = ctx.names[self.name]

        ctx.stream.write(struct.pack("=BH", LOAD_GLOBAL, idx))

    def __repr__(self):
        return "Global(" + self.name+")"

class Import(AExpression):
    def __init__(self, name):
        self.name = name

    def size(self, current, max_count):
        current += 1
        return current, max(current, max_count)

    def emit(self, ctx):
        if self.name not in ctx.names:
            ctx.names[self.name] = len(ctx.names)

        idx = ctx.names[self.name]

        ctx.stream.write(struct.pack("=BH", IMPORT_NAME, idx))

    def __repr__(self):
        return "Import(" + self.name+")"

class Call(AExpression):
    def __init__(self, method, *exprs):
        self.method = method
        self.exprs = exprs
        assertExpression(self.method)
        assertAllExpressions(self.exprs)

    def size(self, current, max_seen):
        current, max_seen = self.method.size(current, max_seen)
        for x in self.exprs:
            current, max_seen = x.size(current, max_seen)

        current -= len(self.exprs)

        return current, max_seen

    def emit(self, ctx):
        self.method.emit(ctx)

        for x in self.exprs:
            x.emit(ctx)

        ctx.stream.write(struct.pack("=BH", CALL_FUNCTION, len(self.exprs)))

    def __repr__(self):
        return "(" + repr(self.method) + " " + " ".join(map(repr, self.exprs)) + ")"

    def __iter__(self):
        yield self.method
        for x in self.exprs:
            yield x

class Func(AExpression):
    def __init__(self, args, expr, resolver = None):
        if resolver == None:
            resolver = lambda x: None
        self.resolver = resolver

        for x in args:
            if not isinstance(x, Argument):
                raise ArgumentExpressionRequiredException()

        self.flags = 67

        if len(args) and isinstance(args[-1], RestArgument):
            self.flags |= CO_VARARGS

        self.args = args
        self.expr = expr
        self.value = None

    def size(self, current, max_seen):
        current += 1
        return current, max(max_seen, current)

    def freeze(self):
        if self.value is None:
            self.code = self.toCode()
            self.value = Const(self.code)

            self.freeVars = self.code.co_freevars


    def emit(self, ctx):
        self.freeze()

        if self.freeVars:
            for x in self.freeVars:
                idx = len(ctx.cellvars)
                ctx.cellvars.append(x)
                resolved = self.resolver(x)
                assert resolved

                resolved.emitPreamble(ctx)
                ctx.stream.write(struct.pack("=BHBH", STORE_DEREF, idx, LOAD_CLOSURE, idx))

            ctx.stream.write(struct.pack("=BH", BUILD_TUPLE, len(self.freeVars)))
            self.value.emit(ctx)
            ctx.stream.write(struct.pack("=BH", MAKE_CLOSURE, 0))
        else:
            self.value.emit(ctx)
            ctx.stream.write(struct.pack("=BH", MAKE_FUNCTION, 0))

    def __repr__(self):
        return "Func(" + repr(map(repr, self.args)) + " -> " + repr(self.expr) + " | " + repr(self.flags) + ")"

    def __iter__(self):
        yield self.expr

class Loop(AExpression):
    def __init__(self, body, vars, args):
        assertAllExpressions([body] + vars + args)
        self.vars = vars
        self.args = args
        self.body = body
        self.inits = []
        assert len(vars) == len(args)

        for x in range(len(self.vars)):
            self.inits.append(self.vars[x].StoreLocal(self.args[x]))

        self.inits = Do(*self.inits)


    def size(self, current, max_seen):
        current, max_seen = Do(self.inits, self.body).size(current, max_seen)
        return current, max_seen

    def emit(self, ctx):
        map(lambda x: x.emit(ctx), self.inits)

        argints = map(lambda x: ctx.varnames[x], self.vars)
        ctx.stream.write(struct.pack("=B", POP_TOP))

        ctx.pushRecurPoint(argints)

        self.body.emit(ctx)

        ctx.popRecurPoint()

    def __repr__(self):
        return "Loop([" + ", ".join(map(repr, self.vars)) + "] [" \
                    + ", ".join(map(repr, self.args)) + " ]" + \
                     repr(self.body)




class Recur(AExpression):
    def __init__(self, *args):
        self.args = args

    def size(self, current, max_seen):

        for x in self.args:
            current, max_seen = x.size(current, max_seen)

        return current - len(self.args) + 1, max_seen

    def emit(self, ctx):

        for x in self.args:
            x.emit(ctx)

        for x in ctx.recurPoint.args:
            ctx.stream.write(struct.pack("=BH", STORE_FAST, x))

        ctx.stream.write(struct.pack("=BH", JUMP_ABSOLUTE, ctx.recurPoint.offset))

    def __iter__(self):
        for x in args:
            yield x


class AbstractBuilder(AExpression):
    """An expression that creates a tuple from the arguments"""
    def __init__(self, buildbc, exprs):
        self.buildbc = buildbc
        assertAllExpressions(exprs)
        self.exprs = exprs

    def size(self, current, max_seen):
        for x in self.exprs:
            current, max_seen = x.size(current, max_seen)
        current -= len(self.exprs)
        current += 1
        return current, max_seen

    def emit(self, ctx):
        for x in self.exprs:
            x.emit(ctx)
        ctx.stream.write(struct.pack("=BH", self.buildbc, len(self.exprs)))

    def __iter__(self):
        for x in self.exprs:
            yield x

class Dict(AExpression):
    """Builds a dict from the given expressions"""
    def __init__(self, *exprs):
        assertAllExpressions(exprs)
        self.exprs = exprs

    def size(self, current, max_seen):
        current += 1
        max_seen = max(current, max_seen)

        for i in range(0, len(self.exprs), 2):
            current, max_seen = self.exprs[i+1].size(current, max_seen)
            current, max_seen = self.exprs[i].size(current, max_seen)
            current -= 2

        return current, max_seen

    def emit(self, ctx):
        ctx.stream.write(struct.pack("=BH", BUILD_MAP, int(len(self.exprs) / 2)))

        for i in range(0, len(self.exprs), 2):
            self.exprs[i+1].emit(ctx)  # Key is popped first, so push value first
            self.exprs[i].emit(ctx)
            ctx.stream.write(struct.pack("=B", STORE_MAP))




class Tuple(AbstractBuilder):
    def __init__(self, *exprs):
        AbstractBuilder.__init__(self, BUILD_TUPLE, exprs)

class List(AbstractBuilder):
    def __init__(self, *exprs):
        AbstractBuilder.__init__(self, BUILD_LIST, exprs)

class Attr(AExpression):
    """Generates a getattr bytecode"""
    def __init__(self, src, name):
        self.src = src
        self.name = name

    def size(self, current, max_seen):
        current, max_seen = self.src.size(current, max_seen)
        return current, max_seen

    def emit(self, ctx):

        if self.name not in ctx.names:
            ctx.names[self.name] = len(ctx.names)

        idx = ctx.names[self.name]
        self.src.emit(ctx)
        ctx.stream.write(struct.pack("=BH", LOAD_ATTR, idx))

    def __repr__(self):
        return "(." + self.name + " " + repr(self.src) + ")"

    def __iter__(self):
        yield self.src


class Compare(AExpression):
    def __init__(self, expr1, expr2, op):
        assertAllExpressions([expr1, expr2])
        self.expr1 = expr1
        self.expr2 = expr2
        self.op = op

    def size(self, current, max_seen):
        current, max_seen = self.expr1.size(current, max_seen)
        current, max_seen = self.expr2.size(current, max_seen)

        return current - 1, max_seen

    def emit(self, ctx):
        self.expr1.emit(ctx)
        self.expr2.emit(ctx)

        ctx.stream.write(struct.pack("=BH", COMPARE_OP, self.op))

    def __iter__(self):
        yield self.expr1
        yield self.expr2


class Raise(AExpression):
    def __init__(self, expr):
        assertAllExpressions([expr])
        self.expr = expr

    def size(self, current, max_size):
        current, max_size = self.expr.size(current, max_size)

        return current, max_size

    def emit(self, ctx):
        self.expr.emit(ctx)

        ctx.stream.write(struct.pack("=BH", RAISE_VARARGS, 1))

    def __iter__(self):
        yield self.expr

class Finally(AExpression):
    def __init__(self, body, final):
        assertAllExpressions([body, final])
        self.body = body
        self.final = final

    def size(self, current, max_size):
        current, max_size = self.body.size(current, max_size)
        _, max_size = self.body.size(current, max_size)

        return current, max_size

    def emit(self, ctx):
        jmp = AbsoluteJump(ctx, SETUP_FINALLY)
        self.body.emit(ctx)
        endjmp = AbsoluteJump(ctx)
        ctx.stream.write(struct.pack("=B", POP_BLOCK))
        jmp.mark()
        ctx.stream.write(struct.pack("=BH", LOAD_CONST, 0))
        self.final.emit(ctx)
        ctx.stream.write(struct.pack("=BB", POP_TOP, END_FINALLY))
        endjmp.mark()

    def __iter__(self):
        yield self.body
        yield self.final



compare_ops = ["Lesser",
               "LesserOrEqual",
               "Equal",
               "NotEqual",
               "Greater",
               "GreaterOrEqual",
               "In",
               "NotIn",
               "Is",
               "IsNot",
               "ExceptionMatch"]

def _initCompareOps():
    opcnt = 0
    for x in compare_ops:
        def init(self, expr1, expr2, op = opcnt):
            Compare.__init__(self, expr1, expr2, op)

        Tmp = type(x, tuple([Compare]), {"__init__": init})

        globals()[x] = Tmp
        opcnt += 1

_initCompareOps()

class Argument(Local):
    def __init__(self, name):
        Local.__init__(self, name)
    def __repr__(self):
        return "Argument(" + self.name + ")"


class RestArgument(Argument):
    def __init__(self, name):
        Local.__init__(self, name)


class LineNo(AExpression):
    def __init__(self, expr, lineno):
        assert isinstance(lineno, int)
        assertExpression(expr)

        self.expr = expr
        self.lineno = lineno

    def size(self, current, max_size):
        return self.expr.size(current, max_size)

    def emit(self, cxt):
        if ctx.lastlineno is None:
            ctx.lastlineno = self.lineno
            ctx.lastbc = ctx.stream.tell()
            ctx.startlineno = ctx.lastlineno
        else:
            bcoffset = ctx.stream.tell() - ctx.lastbc
            linenooffset = ctx.lineno - ctx.lastlineno

            assert bcoffset <= 255 and bcoffset >= 0
            assert lineoffset <= 255 and lineoffset >= 0

            ctx.stream.write(struct.pack("=BB", bcoffset, lineoffset))

        self.expr.emit(ctx)


class RecurPoint(object):
    def __init__(self, offset, args, next):
        self.next = next
        self.args = args
        self.offset = offset





class Context(object):
    """defines a compilation context this keeps track of locals, output streams, etc"""
    def __init__(self, recurPoint, varnames = {}):
        self.stream = BytesIO()
        self.consts = {}
        self.varnames = varnames
        self.recurPoint = recurPoint
        self.names = {}
        self.freevars = {}
        self.cellvars = []
        self.linenotab = BytesIO()
        self.lastlineno = None
        self.startlineno = None
        self.lastbc = None


    def pushRecurPoint(self, args):
        self.recurPoint = RecurPoint(self.stream.tell(), args, self.recurPoint)

    def popRecurPoint(self):
        self.recurPoint = self.recurPoint.next




ConstFalse = Const(False)
ConstTrue = Const(True)
ConstNone = Const(None)


### Taken from byteplay.py

# Flags from code.h
CO_OPTIMIZED              = 0x0001      # use LOAD/STORE_FAST instead of _NAME
CO_NEWLOCALS              = 0x0002      # only cleared for module/exec code
CO_VARARGS                = 0x0004
CO_VARKEYWORDS            = 0x0008
CO_NESTED                 = 0x0010      # ???
CO_GENERATOR              = 0x0020
CO_NOFREE                 = 0x0040      # set if no free or cell vars
CO_GENERATOR_ALLOWED      = 0x1000      # unused
# The future flags are only used on code generation, so we can ignore them.
# (It does cause some warnings, though.)
CO_FUTURE_DIVISION        = 0x2000
CO_FUTURE_ABSOLUTE_IMPORT = 0x4000
CO_FUTURE_WITH_STATEMENT  = 0x8000


ConstTrue = Const(True)
ConstFalse = Const(False)
