
try:
    from pypy.rlib.jit import elidable
    from pypy.rlib.jit import JitDriver, promote, unroll_safe, elidable_promote
except:
    from jitfake import *
