from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_async_sleep(tmp_path):
    # Manually assemble: LOAD_CONST 50ms; ASYNC_SLEEP; AWAIT; STORE_NAME done
    from english_programming.bin.nlbc_encoder import write_module_full
    consts = [(0, 50)]  # int 50
    syms = ['done']
    instrs = [('LOAD_CONST', 0), ('ASYNC_SLEEP', 50), ('AWAIT',), ('STORE_NAME', 0)]
    funcs = []; classes = []
    out = tmp_path / 'sleep.nlbc'
    write_module_full(str(out), consts, syms, instrs, funcs, classes)
    _, _, _, c, s, code, f, cl = parse_module(out.read_bytes())
    env = run_module(c, s, code, f, cl)
    assert 'done' in env


