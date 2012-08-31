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

def list_reader(r, leftparen):
    from system.persistent_list import EMPTY, from_pylist
    lst = read_delimited_list(')', r, True)

    if len(lst) == 0:
        return EMPTY
    s = from_pylist(lst)
    return s

def unmatched_delimiter_reader(reader, c):
    raise Exception("Unmatched delimter: " + c)


macros = {"(" : list_reader,
          ")" : unmatched_delimiter_reader,
          }

def is_whitespace(ch):
    return ch in ', \n\r\t'

def is_macro(ch):
    return ch in macros

def get_macro(ch):
    if ch in macros:
        return macros[ch]
    return None

def is_digit(ch):
    return ch in '1234567890'

def is_terminating_macro(ch):
    return ch != '#' and ch != '\'' and is_macro(ch)

def read_delimited_list(delim, r, is_recursive):
    a = []

    while True:
        ch = r.read()
        while is_whitespace(ch):
            ch = r.read()

        if ch == delim:
            break

        macro_fn = get_macro(ch)
        if macro_fn is not None:
            mret = macro_fn(r, ch)
            a.append(mret)
        else:
            r.back()
            o = read(r, True, None, is_recursive)
            a.append(o)

    return a

def read_token(r, initch):
    sb = []
    sb.append(initch)

    while True:
        ch = r.read()
        if ch == '' or is_whitespace(ch) or is_terminating_macro(ch):
            r.back()
            return ''.join(sb)
        sb.append(ch)

def read_number(rdr, initch):
    from system.core import integer
    sb = []
    sb.append(initch)

    while True:
        ch = rdr.read()
        if ch == '' or is_whitespace(ch) or is_macro(ch):
            rdr.back()
            break
        sb.append(ch)

    s = ''.join(sb)
    n = integer(int(s))
    return

def interpret_token(s):
    from system.bool import w_true, w_false
    from system.core import symbol
    if s == "nil":
        return None
    if s == "true":
        return w_true
    if s == "false":
        return w_false
    if s == "/":
        return symbol("/")
    if s == "system//":
        return symbol("system", "/")
    ret = None
    ret = match_symbol(s)

    if ret is not None:
        return ret

    raise Exception("Unknown Symbol " + s)

def match_symbol(s):
    if "/" in s:
        sp = s.split("/")
        assert len(sp) == 2
        return symbol(sp[0], sp[1])
    return symbol(s)

def read(r, eof_is_error, eof_value, is_recursive):
    while True:
        ch = r.read()
        while is_whitespace(ch):
            ch = r.read()

        if ch == '':
            if eof_is_error:
                raise Exception("End of file")
            return eof_value

        if is_digit(ch):
            n = read_number(r, ch)
            return n

        macro_fn = get_macro(ch)
        if macro_fn is not None:
            ret = macro_fn(r, ch)
            return ret

        token = read_token(r, ch)
        return interpret_token(token)


def read_from_string(string):
    rdr = ChrReader(string)
    return read(rdr, True, None, True)

def read_from_file(filename):
    code = "( " + open_file_as_stream(filename).readall() + " )"
    print code
    return read_from_string(code)


reader_table = {"(": list_reader}
