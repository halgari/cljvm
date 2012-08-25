import system.rt as rt


def count(self):
    return rt.count.invoke1(self)

def next(self):
    return rt.next.invoke1(self)

def first(self):
    return rt.first.invoke1(self)

def equals(self, other):
    return rt.equals.invoke2(self, other)

