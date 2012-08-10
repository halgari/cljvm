from system.interpreter import *
from system.objspace import *
from system.ast import *


def run_benchmark(times):
    code = to_bcode(BINARY_ADD)

    max = Argument("max")
    cur = Argument("cur")
    ast = If(Equal(max, cur), cur, Call(CurFunc(), Add(cur, Const(W_Int(1))), max))
    f = Func([cur, max], ast)

    value = Interpreter(f.toFunction()).main_loop(W_Int(0), W_Int(10))


    return value

