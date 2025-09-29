from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_pattern_case(tmp_path):
    lines = [
        "Set v to 'a'",
        "Case v of 'a': set out to 'yes' else set out to 'no'",
    ]
    out = tmp_path / 'pat.nlbc'
    compile_english_to_binary(lines, str(out))
    consts, syms, code, funcs, classes = parse_module(out.read_bytes())[3:]
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('out') == 'yes'


def test_iterators(tmp_path):
    lines = [
        "Create a list called numbers with values 1, 2, 3",
        # Lower manually: ITER_NEW, ITER_HAS_NEXT/ITER_NEXT (not exposed in NL yet)
    ]
    out = tmp_path / 'iter.nlbc'
    compile_english_to_binary(lines, str(out))
    consts, syms, code, funcs, classes = parse_module(out.read_bytes())[3:]
    # Just ensure module parses and runs
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('numbers') == [1,2,3]


