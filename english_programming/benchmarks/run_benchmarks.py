import time
import tempfile
from pathlib import Path

from english_programming.bin.nlbc_encoder import write_module
from english_programming.bin.nlvm_bin import parse_module, run_module


def bench_epl_arith(n_iters: int) -> float:
    # i=0; one=1; repeat n: i=i+one (unrolled) – avoids backward jumps
    constants = []
    symbols = ['i', 'one']
    I = []
    constants.append((0, 0))
    I += [('LOAD_CONST', 0), ('STORE_NAME', 0)]
    constants.append((0, 1))
    I += [('LOAD_CONST', 1), ('STORE_NAME', 1)]
    for _ in range(n_iters):
        I += [('LOAD_NAME', 0), ('LOAD_NAME', 1), ('ADD',), ('STORE_NAME', 0)]
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'arith.nlbc'
        write_module(str(out), constants, symbols, I)
        buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    t0 = time.perf_counter()
    env = run_module(consts, syms, code, funcs, classes)
    took = time.perf_counter() - t0
    assert env.get('i') == n_iters
    return took


def bench_py_arith(n_iters: int) -> float:
    t0 = time.perf_counter()
    i = 0
    for _ in range(n_iters):
        i += 1
    took = time.perf_counter() - t0
    assert i == n_iters
    return took


def bench_epl_set_ops(n_items: int) -> float:
    # s = new set; insert n_items; check contains last
    constants = [(2, 'a')]
    symbols = ['s']
    I = [('SET_NEW',), ('STORE_NAME', 0)]
    for _ in range(n_items):
        I += [('LOAD_NAME', 0), ('LOAD_CONST', 0), ('SET_ADD',), ('STORE_NAME', 0)]
    I += [('LOAD_NAME', 0), ('LOAD_CONST', 0), ('SET_CONTAINS',), ('STORE_NAME', 0)]
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'set.nlbc'
        write_module(str(out), constants, symbols, I)
        buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    t0 = time.perf_counter()
    env = run_module(consts, syms, code, funcs, classes)
    took = time.perf_counter() - t0
    assert env.get('s') is True or env.get('s')
    return took


def bench_py_set_ops(n_items: int) -> float:
    t0 = time.perf_counter()
    s = set()
    for _ in range(n_items):
        s.add('a')
    assert ('a' in s)
    took = time.perf_counter() - t0
    return took


def bench_epl_file_io(n_loops: int) -> float:
    # write/read append cycles minimal
    with tempfile.TemporaryDirectory() as td:
        fpath = Path(td) / 'f.txt'
        constants = [(2, str(fpath)), (2, 'x'), (2, 'y')]
        symbols = ['tmp']
        I = []
        for _ in range(n_loops):
            I += [('LOAD_CONST', 1), ('LOAD_CONST', 0), ('WRITEFILE',)]
            I += [('LOAD_CONST', 2), ('LOAD_CONST', 0), ('APPENDFILE',)]
            I += [('LOAD_CONST', 0), ('READFILE',), ('STORE_NAME', 0)]
        out = Path(td) / 'fio.nlbc'
        write_module(str(out), constants, symbols, I)
        buf = out.read_bytes()
        _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
        t0 = time.perf_counter()
        env = run_module(consts, syms, code, funcs, classes)
        took = time.perf_counter() - t0
        return took


def bench_py_file_io(n_loops: int) -> float:
    with tempfile.TemporaryDirectory() as td:
        fpath = Path(td) / 'f.txt'
        t0 = time.perf_counter()
        for _ in range(n_loops):
            fpath.write_text('x')
            with fpath.open('a') as f:
                f.write('y')
            _ = fpath.read_text()
        took = time.perf_counter() - t0
    return took


def main():
    N_ARITH = 400_000
    N_SET = 50_000
    N_FIO = 500

    results = []

    epl = bench_epl_arith(N_ARITH)
    py = bench_py_arith(N_ARITH)
    results.append(('arith', N_ARITH, epl, py))

    epl = bench_epl_set_ops(N_SET)
    py = bench_py_set_ops(N_SET)
    results.append(('set_ops', N_SET, epl, py))

    epl = bench_epl_file_io(N_FIO)
    py = bench_py_file_io(N_FIO)
    results.append(('file_io', N_FIO, epl, py))

    # Write markdown summary
    out = Path(__file__).absolute().parents[2] / 'docs' / 'benchmarks.md'
    lines = [
        '# EPL Benchmarks (vs CPython baseline)\n',
        '',
        '| task | size | epl (s) | python (s) | ratio (epl/python) |',
        '|---|---:|---:|---:|---:|',
    ]
    for name, size, epl_t, py_t in results:
        ratio = epl_t / py_t if py_t > 0 else float('inf')
        lines.append(f"| {name} | {size} | {epl_t:.4f} | {py_t:.4f} | {ratio:.2f} |")
    out.write_text('\n'.join(lines) + '\n')

    # Print summary
    print('\n'.join(lines))


if __name__ == '__main__':
    main()


