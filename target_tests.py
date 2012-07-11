import sys
import tests.cons

sys.path.append('/home/tim/pypy')

class TestHelper(object):
    def assertEqual(self, x, y):
        assert x == y


def entry_point(argv):
    tests.cons.run(TestHelper())

    return 0

# _____ Define and setup target ___

def target(driver, args):
    driver.exe_name = 'cljvm-%(backend)s'
    return entry_point, None

if __name__ == '__main__':
    entry_point(sys.argv)