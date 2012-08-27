import system.rt as rt
from pypy.rlib.streamio import open_file_as_stream
from system.core import integer, symbol

class SplitReader(object):
    def __init__(self, string):
        self._splits = split_all(string)
        self._idx = 0

    def read(self):
        s = self._splits[self._idx]
        self._idx += 1
        return s

    def back(self):
        self._idx -= 1

    def has_more(self):
        return self._idx < len(self._splits)

def replace(s, f, r):
    res = []
    for x in s:
        if x == f:
            res.append(r)
        else:
            res.append(x)

    return "".join(res)

def all_whitespace(x):
    for s in x:
        if s != ' ' and s != '\t' and s != '\n' and s != '\r':
            return True
    return False

def split_all(string):
    s = []
    string = replace(string, "[", " ( ")
    string = replace(string, "]", " ) ")
    string = replace(string, "(", " ( ")
    string = replace(string, ")", " ) ")

    strs = string.split("\n\t ")
    for x in strs:
        if not all_whitespace(x):
            s.append(x)
    return s


def is_int(string):
    for x in string:
        if ord(x) < ord('0') or ord(x) > ord('9'):
            return False
    return True

def read_list(rdr):
    s = []
    while True:
        term = rdr.read()
        if term == ")":
            return rt.list.invoke_args(s)
        rdr.back()
        s.append(read_term(rdr))

def read_term(rdr):
    term = rdr.read()
    if term == "(":
        return read_list(rdr)
    if is_int(term):
        return integer(int(term))
    return symbol(None, term)

def read_from_string(string):
    rdr = SplitReader(string)
    return read_term(rdr)

def read_from_file(filename):
    code = "( " + open_file_as_stream(filename).readall() + " )"
    print code
    return read_from_string(code)