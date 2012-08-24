from system.rt import list, count
from system.core import integer

def run_benchmark(times):
    c = list.invoke_args([integer(times), integer(2), integer(3)])

    return count.invoke1(c).int()

