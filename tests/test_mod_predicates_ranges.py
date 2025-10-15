from english_programming.bin.nlvm_bin import parse_module, run_module
from english_programming.bin.nlp_compiler_bin import compile_english_to_binary


def _compile_run(lines, tmp_path, name):
    out = tmp_path / name
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)
    return env


def test_mod_and_divisible(tmp_path):
    lines = [
        "Set a to 10",
        "Set b to 3",
        "Compute a modulo b and store the result in r",
        "If a is divisible by b then Set d to 1",
    ]
    env = _compile_run(lines, tmp_path, 'mod.nlbc')
    assert env.get('r') == 1
    assert env.get('d') == 1


def test_even_odd_predicates(tmp_path):
    lines = [
        "Set x to 4",
        "If x is even then Set e to 1",
        "Set y to 5",
        "If y is odd then Set o to 1",
    ]
    env = _compile_run(lines, tmp_path, 'even_odd.nlbc')
    assert env.get('e') == 1
    assert env.get('o') == 1


def test_prime_filter(tmp_path):
    lines = [
        "Filter numbers from 1 to 20 where i is prime into primes",
    ]
    env = _compile_run(lines, tmp_path, 'primes.nlbc')
    assert env.get('primes') == [2,3,5,7,11,13,17,19]


def test_range_and_sum(tmp_path):
    lines = [
        "Create a list numbers from 1 to 10",
        "Filter numbers from 1 to 10 where i is even into evens",
        "Sum numbers from 1 to 10 where i divisible by 3 into s",
    ]
    env = _compile_run(lines, tmp_path, 'range_sum.nlbc')
    assert env.get('numbers') == list(range(1, 11))
    assert env.get('evens') == [2,4,6,8,10]
    assert env.get('s') == 18


def test_natural_english_sequence(tmp_path):
    # spaCy normalization + sequence splitting on commas/then
    lines = [
        "Create a list of numbers from 1 to 10, then filter for even numbers and calculate their sum.",
    ]
    # Provide synonym-friendly expanded forms via spaCy + synonyms
    env = _compile_run(lines, tmp_path, 'natural.nlbc')
    # Expect derived variables available
    # Depending on lowering strategy, we check for sum result;
    # we accept either 'sum' or 'sumevens' present
    sum_val = env.get('sum') or env.get('s') or env.get('sum_of_evens')
    assert sum_val == 30


