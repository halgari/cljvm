import sys

#sys.path.append('/home/tim/pypy')

def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()


from system.rt import init
init()

def main(filename):
    import system.reader as reader
    from system.evaluation import eval
    from system.helpers import first, next

    s = reader.read_from_file(filename)

    while s is not None:
        res = eval(first(s))
        print res
        s = next(s)
    return 0


def entry_point(argv):
    if len(argv) != 2:
        print "Filename required"
    res = main(argv[1])
    return res
# _____ Define and setup target ___

def target(driver, args):
    driver.exe_name = 'cljvm-%(backend)s'
    return entry_point, None

if __name__ == '__main__':
    print entry_point(sys.argv)
