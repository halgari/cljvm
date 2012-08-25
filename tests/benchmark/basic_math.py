from system.rt import list, count
from system.core import integer, symbol
from system.evaluation import eval
import system.rt
from system.helpers import *

system.rt.init()

def run_benchmark(times):
    c = list.invoke_args([symbol(None, "+"), integer(2), integer(3)])

    return eval(c).int()

