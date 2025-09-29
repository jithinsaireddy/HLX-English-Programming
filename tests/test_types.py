import pytest
from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_concat_requires_strings(tmp_path):
    # This should pass type verifier: string + string
    lines = [
        "Set a to 'hi'",
        "Set b to 'there'",
        "Concatenate a and b and store in c",
    ]
    out = tmp_path / 'ok.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    parse_module(buf)  # no exception


def test_concat_type_error(tmp_path):
    # This will trip type check if both are numbers (strict), but we allow unknown to pass.
    lines = [
        "Set a to 1",
        "Set b to 2",
        "Concatenate a and b and store in c",
    ]
    out = tmp_path / 'bad.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    # run_module invokes verifier which should raise ValueError
    consts, syms, code, funcs, classes = parse_module(buf)[3:]
    with pytest.raises(ValueError):
        run_module(consts, syms, code, funcs, classes)


