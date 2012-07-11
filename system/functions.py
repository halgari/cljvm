from objspace import Object, s_type

class WrappedFn(Object):
    """Allows an interp function to act as a app function"""
    def __init__(self, fn, meta):
        self._fn = fn
        self._meta = meta
        self._requiredArity = fn.func_code.co_argcount

    def getRequiredArity(self):
        return self._requiredArity

    def invoke0(self):
        return self._fn()

    def invoke1(self,a):
        return self._fn(a)

    def invoke2(self,a,b):
        return self._fn(a,b)

    def invoke3(self,a,b,c):
        return self._fn(a,b,c)

    def invoke4(self,a,b,c,d):
        return self._fn(a,b,c,d)

    def invoke5(self,a,b,c,d,e):
        return self._fn(a,b,c,d,e)

    def invoke6(self,a,b,c,d,e,f):
        return self._fn(a,b,c,d,e,f)

    def invoke7(self,a,b,c,d,e,f,g):
        return self._fn(a,b,c,d,e,f,g)

    def invoke8(self,a,b,c,d,e,f,g,h):
        return self._fn(a,b,c,d,e,f,g,h)

    def invoke9(self,a,b,c,d,e,f,g,h,i):
        return self._fn(a,b,c,d,e,f,g,h,i)

    def invoke10(self,a,b,c,d,e,f,g,h,i,j):
        return self._fn(a,b,c,d,e,f,g,h,i,j)

    def invoke11(self,a,b,c,d,e,f,g,h,i,j,k):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k)

    def invoke12(self,a,b,c,d,e,f,g,h,i,j,k,l):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l)

    def invoke13(self,a,b,c,d,e,f,g,h,i,j,k,l,m):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m)

    def invoke14(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m,n)

    def invoke15(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o)

    def invoke16(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p)

    def invoke17(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q)

    def invoke18(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r)

    def invoke19(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s):
        return self._fn(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s)

class PolymorphicFn(Object):
    def __init__(self, name):
        self._name = name
        self._methods = {}

    def extend(self, tp, w_fn):
        self._methods[tp] = w_fn

    def invoke1(self,a):
        return self._methods[s_type(a)].invoke1(a)

    def invoke2(self,a,b):
        return self._methods[s_type(a)].invoke2(a,b)

    def invoke3(self,a,b,c):
        return self._methods[s_type(a)].invoke3(a,b,c)

    def invoke4(self,a,b,c,d):
        return self._methods[s_type(a)].invoke4(a,b,c,d)

    def invoke5(self,a,b,c,d,e):
        return self._methods[s_type(a)].invoke5(a,b,c,d,e)

    def invoke6(self,a,b,c,d,e,f):
        return self._methods[s_type(a)].invoke6(a,b,c,d,e,f)

    def invoke7(self,a,b,c,d,e,f,g):
        return self._methods[s_type(a)].invoke7(a,b,c,d,e,f,g)

    def invoke8(self,a,b,c,d,e,f,g,h):
        return self._methods[s_type(a)].invoke8(a,b,c,d,e,f,g,h)

    def invoke9(self,a,b,c,d,e,f,g,h,i):
        return self._methods[s_type(a)].invoke9(a,b,c,d,e,f,g,h,i)

    def invoke10(self,a,b,c,d,e,f,g,h,i,j):
        return self._methods[s_type(a)].invoke10(a,b,c,d,e,f,g,h,i,j)

    def invoke11(self,a,b,c,d,e,f,g,h,i,j,k):
        return self._methods[s_type(a)].invoke11(a,b,c,d,e,f,g,h,i,j,k)

    def invoke12(self,a,b,c,d,e,f,g,h,i,j,k,l):
        return self._methods[s_type(a)].invoke12(a,b,c,d,e,f,g,h,i,j,k,l)

    def invoke13(self,a,b,c,d,e,f,g,h,i,j,k,l,m):
        return self._methods[s_type(a)].invoke13(a,b,c,d,e,f,g,h,i,j,k,l,m)

    def invoke14(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n):
        return self._methods[s_type(a)].invoke14(a,b,c,d,e,f,g,h,i,j,k,l,m,n)

    def invoke15(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o):
        return self._methods[s_type(a)].invoke15(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o)

    def invoke16(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p):
        return self._methods[s_type(a)].invoke16(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p)

    def invoke17(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q):
        return self._methods[s_type(a)].invoke17(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q)

    def invoke18(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r):
        return self._methods[s_type(a)].invoke18(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r)

    def invoke19(self,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s):
        return self._methods[s_type(a)].invoke19(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s)