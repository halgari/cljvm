import system.rt as rt
from pypy.rlib.streamio import open_file_as_stream
from system.core import integer, symbol, Object


whitespace = '\t\r\n ,'

class EOS(Object):
    pass

eos = EOS()


class ChrReader(object):
    def __init__(self, str):
        self._str = str
        self._idx = 0

    def read(self):
        s = self._str[self._idx]
        self._idx += 1
        return s

    def back(self):
        self._idx -= 1

    def has_more(self):
        return self._idx < len(self._str)


def is_int(string):
    for x in string:
        if ord(x) < ord('0') or ord(x) > ord('9'):
            return False
    return True

def read_list(rdr, chr):
    s = []
    while True:
        term = rdr.read()
        while term in whitespace:
            term = rdr.read()

        if term == ")":
            return rt.list.invoke_args(s)
        rdr.back()
        s.append(read_term(rdr))

def read_term(rdr):
    term = rdr.read()
    while term in whitespace:
        if not rdr.has_more():
            return eos
        term = rdr.read()

    if term in reader_table:
        return reader_table[term](rdr, term)

    s = [term]
    while True:
        term = rdr.read()
        if term in reader_table:
            rdr.back()
            break
        s.append(term)
        if term in whitespace:
            break
            
    term = "".join(s).strip(' ')
    if is_int(term):
        return integer(int(term))
    return symbol(None, term)

def read_from_string(string):
    rdr = ChrReader(string)
    return read_term(rdr)

def read_from_file(filename):
    code = "( " + open_file_as_stream(filename).readall() + " )"
    print code
    return read_from_string(code)


reader_table = {"(": read_list}
