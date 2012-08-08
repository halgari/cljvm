import sys

sys.path.append('/home/tim/pypy')

def benchmark_fn(name):
    if name == "basic_math":
        import tests.benchmark.basic_math
        return tests.benchmark.basic_math.run_benchmark

fn = benchmark_fn("basic_math")

def entry_point(argv):
    print fn(1000000)
    return 0

# _____ Define and setup target ___

def target(driver, args):
    driver.exe_name = 'cljvm-%(backend)s'
    return entry_point, None

if __name__ == '__main__':
    print entry_point(sys.argv)