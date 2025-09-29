from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_sets_and_membership(tmp_path):
    lines = [
        "Create a set called s",
        "Add 'a' to set s",
        "Check if 'a' in set s store in has",
    ]
    out = tmp_path / 'set.nlbc'
    compile_english_to_binary(lines, str(out))
    consts, syms, code, funcs, classes = parse_module(out.read_bytes())[3:]
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('has') is True


def test_csv_yaml_roundtrip(tmp_path):
    lines = [
        "Set txt to 'a,b\\n1,2'",
        "Parse csv txt store in rows",
        "Stringify csv rows store in outcsv",
        "Set y to '{a: 1, b: 2}'",
        "Parse yaml y store in yobj",
        "Stringify yaml yobj store in ytxt",
    ]
    out = tmp_path / 'io.nlbc'
    compile_english_to_binary(lines, str(out))
    consts, syms, code, funcs, classes = parse_module(out.read_bytes())[3:]
    env = run_module(consts, syms, code, funcs, classes)
    assert 'a,b' in env.get('outcsv', '')
    assert 'a' in env.get('ytxt', '')


