import sys

sys.path.append('/home/tim/pypy')
import system.rt

system.rt.init()

def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()


def run_file(file):
    from system.reader import read_from_file
    f = read_from_file(file)
    from system.evaluation import eval
    from system.helpers import first
    return eval(first(f)).int()

def entry_point(argv):
    if len(argv) != 2:
        print "Filename required"
    print run_file(argv[1])
    return 0

# _____ Define and setup target ___

def target(driver, args):
    driver.exe_name = 'cljvm-%(backend)s'
    return entry_point, None

if __name__ == '__main__':
    print entry_point(sys.argv)
