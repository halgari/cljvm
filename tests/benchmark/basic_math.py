from system.interpreter import *
from system.objspace import *
from system.ast import *


def run_benchmark(times):
    max = Argument("max")
    cur = Argument("cur")
    ast = If(Equal(max, cur), cur, Call(CurFunc(), Add(cur, Const(W_Int(1))), max))
    f = Func([cur, max], ast)
    max2 = Argument("max")
    f = Func([max2], Call(f, Const(W_Int(0)), max2))



    #value = Interpreter(f.toFunction()).main_loop(W_Int(0), W_Int(2147483648))
    value = Interpreter(f.toFunction()).main_loop(W_Int(int(times)))


    return value

