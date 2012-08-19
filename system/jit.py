
try:
    from pypy.rlib.jit import elidable
    from pypy.rlib.jit import JitDriver, promote
except:
    from jitfake import *