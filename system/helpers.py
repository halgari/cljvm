import system.rt as rt
from system.bool import w_true, w_false

def count(self):
    return rt.count.invoke1(self)

def next(self):
    return rt.next.invoke1(self)

def first(self):
    return rt.first.invoke1(self)

def equals(self, other):
    return rt.equals.invoke2(self, other)

def isvector(self):
    return rt.isvector.invoke1(self)

def islist(self):
    return rt.islist.invoke1(self)

def nth(self, idx):
    return rt.nth.invoke2(self, idx)

def keyword(ns, name = None):
    if name is None:
        name = ns
        ns = None
    return rt.keyword.invoke2(ns, name)
