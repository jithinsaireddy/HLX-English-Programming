import time
from english_programming.bin.nlbc_encoder import write_module
from english_programming.bin.nlvm_bin import parse_module, run_module


def make_loop_module(n_iters=1000):
    # constants, symbols, main_instrs implementing repeated increments (no backward jumps)
    constants = []
    symbols = ['i', 'one']
    # program: i=0; one=1; repeat n: i=i+one
    I = []
    # i = 0
    constants.append((0, 0))
    I += [('LOAD_CONST', 0), ('STORE_NAME', 0)]
    # one = 1
    constants.append((0, 1))
    I += [('LOAD_CONST', 1), ('STORE_NAME', 1)]
    # Unrolled increments
    for _ in range(n_iters):
        I += [('LOAD_NAME', 0), ('LOAD_NAME', 1), ('ADD',), ('STORE_NAME', 0)]
    return constants, symbols, I


def test_hot_loop_microbenchmark(tmp_path):
    constants, symbols, instrs = make_loop_module(n_iters=2000)
    out = tmp_path / 'bench.nlbc'
    write_module(str(out), constants, symbols, instrs)
    buf = out.read_bytes()
    ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(buf)

    t0 = time.time()
    env = run_module(consts, syms, code, funcs, classes)
    took = time.time() - t0
    assert env.get('i') == 2000
    # sanity check: run should complete quickly (<0.5s)
    assert took < 0.5


