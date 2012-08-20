
try:
    from pypy.rlib.jit import elidable
    from pypy.rlib.jit import JitDriver, promote, unroll_safe
except:
    from jitfake import *