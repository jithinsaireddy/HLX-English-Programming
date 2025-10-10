import os
from pathlib import Path
from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def run_prog(lines):
    # helper to compile to NLBC bytes and run in VM, returning env
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.nlbc', delete=False) as tf:
        out = tf.name
    try:
        compile_english_to_binary(lines, out)
        data = Path(out).read_bytes()
        ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(data)
        env = run_module(consts, syms, code, funcs, classes)
        return env
    finally:
        try:
            Path(out).unlink(missing_ok=True)
        except Exception:
            pass


def test_function_synonyms_and_return():
    os.environ['EP_FUZZY'] = '1'
    prog = [
        "Create function add(a, b)",
        "  add a and b and store the result in out",
        "  return out",
        "End operation",
        "call function add with 2, 3 and store in r",
    ]
    env = run_prog(prog)
    assert env.get('r') == 5


def test_collection_ops_synonyms_list_map_set():
    os.environ['EP_FUZZY'] = '1'
    # lists: append implicit, take last item
    prog = [
        "create a list called nums",
        "append 1 to nums",
        "append 'x' to list nums",
        "take the last item from list nums store in last",
        # maps / dicts
        "create a dictionary called m",
        "put 'a' maps to 1 in m",
        "map get m 'a' store in v",
        # sets
        "create a set called s",
        "add 3 to set s",
        "check if 3 exists in set s store in has",
    ]
    env = run_prog(prog)
    assert env.get('nums') == [1]
    assert env.get('last') == 'x'
    assert env.get('m') == {'a': 1}
    assert env.get('v') == 1
    assert env.get('has') is True


def test_fuzzy_hints_unknown_line_no_error():
    os.environ['EP_FUZZY'] = '1'
    os.environ['EP_FUZZY_HINTS'] = '1'
    prog = [
        "this line will not match any known pattern",
        "set x to 1",
        "print x",
    ]
    env = run_prog(prog)
    # _hints retained in env (underscored keys preserved)
    hints = env.get('_hints', [])
    assert isinstance(hints, list)
    assert any('Unknown:' in h for h in hints)


def test_synonyms_yaml_live_reload(tmp_path, monkeypatch):
    # Create synonyms.yml in CWD so loader picks it up
    cwd = Path.cwd()
    syn = cwd / 'synonyms.yml'
    try:
        syn.write_text("from: push\nto: append\n")
        os.environ['EP_FUZZY'] = '1'
        prog = [
            "create a list called q",
            "push 9 to q",
        ]
        env = run_prog(prog)
        assert env.get('q') == [9]
    finally:
        try:
            syn.unlink()
        except Exception:
            pass
