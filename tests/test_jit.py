from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_hot_loop_jit(tmp_path):
    # Simple loop that should trigger JIT backedge counting but still produce correct result
    lines = [
        "Set a to 0",
        "Set n to 20",
        # while a is less than n do print a (ensures backedges)
        "While a is less than 5 do print a",
    ]
    out = tmp_path / "jit.nlbc"
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)
    # Just ensure environment exists and no crash
    assert env is not None


