from system.objspace import *

from system.util import data_to_app

if_ = symbol("if")
add_ = symbol("+")
fn_ = symbol("fn")
tmp = symbol("tmp")
x = symbol("x")
max = symbol("max")
cur = symbol("cur")
eq = symbol("=")

def load_data():
    expr = (fn_, tmp, [cur, max],
             (if_, (eq, cur, max),
              cur,
              (tmp, (add_, 1, cur), max)))
    globals()["expr"] = data_to_app(expr)

load_data()


def run_benchmark(times):
    code = make_list(expr, W_Int(0), W_Int(int(times)))
    ret = eval(code)

    return ret.int()

