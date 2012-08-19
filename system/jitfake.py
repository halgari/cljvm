

print "WARNING: FAKING JIT...."


def elidable(f):
    return f

def promote(f):
    return f

class JitDriver(object):
    def __init__(self, **kw):
        pass
    def jit_merge_point(self, **kw):
        pass