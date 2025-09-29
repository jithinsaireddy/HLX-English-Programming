from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_op_counter_increments(tmp_path):
    lines = [
        "Set a to 0",
        "Set b to 1",
        "Add a and b and store the result in a",
    ]
    out = tmp_path / 'p.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('_op_counts', 0) > 0


