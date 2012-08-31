

class Object(object):
    pass


def symbol(ns, name = None):
    if name is None:
        name = ns
        ns = None
    from symbol import W_Symbol
    return W_Symbol(ns, name)

def type(a):
    if a is None:
        return symbol("system", "Nil")
    return a.type()

def integer(i):
    from system.integer import W_Integer
    return W_Integer(i)



