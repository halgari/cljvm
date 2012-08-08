from system.interpreter import *
from system.objspace import *

def run_benchmark(times):
    code = to_bcode(BINARY_ADD)

    accum = 0
    for x in range(times):
        interp = Interpreter(code, to_stack(W_Int(1), W_Int(0)))
        val = s_unwrap_int(interp.main_loop())
        accum += val

    return accum

