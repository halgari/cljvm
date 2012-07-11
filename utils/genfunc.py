import sys

out = sys.stdout

cur_indent = 0
line_start = True

def write(s):
    global line_start
    if line_start:
        newline()
    out.write(str(s))
    line_start = False

def writeln(s):
    global line_start
    if line_start:
        newline()
    out.write(str(s) + "\n")
    line_start = True

def newline():
    out.write(str(" " * (4 * cur_indent)))

def indent():
    global cur_indent
    cur_indent += 1

def dedent():
    global cur_indent
    cur_indent -= 1

arity = 20

names = "abcdefghijklmnopqrstuvwxyz"

output_wrapped = True
output_afn = True
output_polymorphic = True

if output_wrapped:
    for a in range(arity):
        write("def invoke")
        write(a)
        write("(self")
        if a != 0:
            write(",")
        for x in range(a):
            var = names[x]
            write(var)
            if x < a - 1:
                write(",")
        writeln("):")
        indent()

        write("return self._fn(")
        for x in range(a):
            var = names[x]
            write(var)
            if x < a - 1:
                write(",")
        writeln(")")
        dedent()
        writeln("")

if output_afn:
    for a in range(arity):
        write("def invoke")
        write(a)
        write("(self")
        if a != 0:
            write(",")
        for x in range(a):
            var = names[x]
            write(var)
            if x < a - 1:
                write(",")
        writeln("):")
        indent()

        write("assert False")
        dedent()
        writeln("")


if output_polymorphic:
    for a in range(1, arity):
        write("def invoke")
        write(a)
        write("(self")
        if a != 0:
            write(",")
        for x in range(a):
            var = names[x]
            write(var)
            if x < a - 1:
                write(",")
        writeln("):")
        indent()

        write("return self._methods[s_type(a)].invoke")
        write(a)
        write ("(")
        for x in range(a):
            var = names[x]
            write(var)
            if x < a - 1:
                write(",")
        writeln(")")
        dedent()
        writeln("")

