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


def test_repeat_times():
    env = run_epl([
        'set sum to 0',
        'repeat 5 times:',
        '  add sum and 1 and store the result in sum',
        'print sum'
    ])
    assert env.get('sum') == 5
    outs = [v for (op, *rest) in env.get('_traces', []) if op == 'PRINT' for v in rest]
    assert outs and outs[-1] == 5


def test_for_range_inclusive():
    env = run_epl([
        'set sum to 0',
        'for i from 1 to 4:',
        '  add sum and i and store the result in sum',
        'print sum'
    ])
    assert env.get('sum') == 10


def test_foreach_list():
    env = run_epl([
        'create a list called xs with values 1, 2, 3',
        'set sum to 0',
        'for each x in list xs:',
        '  add sum and x and store the result in sum',
        'print sum'
    ])
    assert env.get('sum') == 6


def test_while_condition_spacy():
    env = run_epl([
        'set i to 0',
        'set sum to 0',
        'while i is less than or equal to 3:',
        '  add sum and i and store the result in sum',
        '  add i and 1 and store the result in i',
        'print sum'
    ])
    assert env.get('sum') == 6
