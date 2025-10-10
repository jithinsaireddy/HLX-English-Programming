import os, tempfile
from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def run_epl(lines):
    with tempfile.NamedTemporaryFile(suffix='.nlbc', delete=False) as tf:
        out = tf.name
    try:
        compile_english_to_binary(lines, out)
        data = open(out, 'rb').read()
        ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(data)
        env = run_module(consts, syms, code, funcs, classes)
        return env
    finally:
        try:
            os.remove(out)
        except Exception:
            pass


def test_pairwise_assignment():
    env = run_epl([
        'create a variable called x and y and set it to 2 and 3',
        'add x and y and store the result in sum',
        'print sum'
    ])
    assert env.get('sum') == 5


def test_broadcast_assignment():
    env = run_epl([
        'create a variable called a, b, c and set it to 4',
        'add a and b and store the result in t',
        'add t and c and store the result in total',
        'print total'
    ])
    assert env.get('total') == 12
